from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import time
import os
import winsound  # For Windows alarm sound

import concurrent.futures

# Handles the YOLOv4 detection algorithm with alarm sound
class Detection(QThread):

    def __init__(self, camera_source, detection_window):
        super(Detection, self).__init__()
        self.camera_source = camera_source  # Can be camera index (int) or file path (str)
        self.detection_window = detection_window
        self.running = True
        self.last_alarm_time = 0
        self.alarm_cooldown = 2  # Seconds between alarms
        self.error_occurred = False
        self.alarm_playing = False
        self.alarm_start_time = 0
        self.alarm_duration = 20  # Alarm plays for 20 seconds
        self.frame_skip = 1  # Process every frame if possible (threaded)
        self.frame_counter = 0
        self.last_detection_result = None  # Store last detection result
        self.detection_frame = None  # Frame being processed for detection
        self.detection_result_time = 0  # Time when detection result was obtained
        self.result_ttl = 2.0  # Keep detection result for 2.0 seconds (persistent boxes - longer display)
        self.consecutive_detections = 0  # Counter for stability
        self.detection_threshold = 3     # Number of consecutive frames to confirm detection
        self.min_confidence = 0.75       # Higher confidence to reduce false positives (laptop keyboard)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.detection_future = None
        self.is_detecting = False
    
    changePixmap = pyqtSignal(QImage)

    def play_alarm(self):
        """Play alarm sound when weapon is detected"""
        current_time = time.time()
        
        # Start alarm if not already playing
        if not self.alarm_playing:
            self.alarm_playing = True
            self.alarm_start_time = current_time
            self.last_alarm_time = current_time
        
        # Play beep every 0.5 seconds
        if current_time - self.last_alarm_time >= 0.5:
            try:
                # Play system beep sound (Windows) - longer beep
                winsound.Beep(1000, 400)  # Frequency 1000Hz, duration 400ms
                self.last_alarm_time = current_time
            except:
                # Fallback if winsound doesn't work
                print("ALARM: Weapon Detected!")
    
    def run_detection_task(self, frame, net, output_layers, width, height, classes, colors, font):
        """Task to run in background thread"""
        try:
            # Create blob and run forward pass
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)
            
            # Process results
            return self.process_detections_fast(frame, outs, width, height, classes, colors, font)
        except Exception as e:
            print(f"Background detection error: {e}")
            return False, [], [], []

    def run(self):
        """Runs the detection model, evaluates detections and draws boxes around detected objects"""
        try:
            # Loads Yolov4
            net = cv2.dnn.readNet("weights/yolov4.weights", "cfg/yolov4.cfg")
            
            # Use CUDA if available (optional, keeping CPU for compatibility)
            # net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            # net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            
            classes = []
            
            # Loads object names
            with open("obj.names", "r") as f:
                classes = [line.strip() for line in f.readlines()]
            
            layer_names = net.getLayerNames()
            # Get unconnected output layers (returns 1D numpy array in OpenCV 4.x)
            unconnected_out_layers = net.getUnconnectedOutLayers()
            # Convert to list of layer names (subtract 1 because OpenCV uses 1-based indexing)
            output_layers = [layer_names[int(i) - 1] for i in unconnected_out_layers.flatten()]
            colors = np.random.uniform(0, 255, size=(len(classes), 3))
            
            font = cv2.FONT_HERSHEY_PLAIN
            
            # Determine if source is camera or file
            if isinstance(self.camera_source, str):
                # Check if it's a URL (DroidCam) or file path
                if self.camera_source.startswith(('http://', 'https://')):
                    # DroidCam URL - try different approaches to connect
                    cap = None
                    url = self.camera_source
                    
                    # Try different URL formats and backends
                    url_variants = [
                        url,  # Original URL
                        url.replace('/video', '/mjpegfeed?640x480'),  # Alternative DroidCam format
                    ]
                    
                    backends_to_try = [
                        cv2.CAP_FFMPEG,  # FFMPEG backend (best for IP cameras)
                        cv2.CAP_ANY,     # Any available backend
                    ]
                    
                    # Try connecting with different methods
                    for url_variant in url_variants:
                        # Method 1: Try with explicit backend (OpenCV 4.x syntax)
                        try:
                            cap = cv2.VideoCapture(url_variant, cv2.CAP_FFMPEG)
                            if cap.isOpened():
                                # Set timeout for IP camera
                                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                                # Optimize camera settings for better quality and performance
                                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize lag
                                cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS
                                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Higher resolution for clarity
                                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Higher resolution for clarity
                                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Better codec
                                # Test by reading a frame
                                ret, test_frame = cap.read()
                                if ret and test_frame is not None:
                                    print(f"Successfully connected to: {url_variant}")
                                    break
                                else:
                                    cap.release()
                                    cap = None
                        except Exception as e:
                            if cap:
                                cap.release()
                            cap = None
                            print(f"FFMPEG backend failed: {e}")
                        
                        # Method 2: Try without backend specification
                        if not cap or not cap.isOpened():
                            try:
                                cap = cv2.VideoCapture(url_variant)
                                if cap.isOpened():
                                    cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
                                    cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS
                                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Higher resolution
                                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Higher resolution
                                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Better codec
                                    ret, test_frame = cap.read()
                                    if ret and test_frame is not None:
                                        print(f"Successfully connected (default backend): {url_variant}")
                                        break
                                    else:
                                        cap.release()
                                        cap = None
                            except Exception as e:
                                if cap:
                                    cap.release()
                                cap = None
                                print(f"Default backend failed: {e}")
                        
                        if cap and cap.isOpened():
                            break
                    
                    self.process_video(cap, net, classes, layer_names, output_layers, colors, font)
                elif self.camera_source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    # Image file
                    self.process_image(self.camera_source, net, classes, layer_names, output_layers, colors, font)
                else:
                    # Video file
                    cap = cv2.VideoCapture(self.camera_source)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
                    self.process_video(cap, net, classes, layer_names, output_layers, colors, font)
            else:
                # Camera index (for webcam)
                cap = cv2.VideoCapture(self.camera_source)
                # Optimize webcam settings for better quality
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize lag
                cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Higher resolution for clarity
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Higher resolution for clarity
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Better codec
                self.process_video(cap, net, classes, layer_names, output_layers, colors, font)
        except Exception as e:
            # If anything goes wrong, show error frame
            print(f"Detection error: {e}")
            self.error_occurred = True
            error_frame = np.zeros((480, 854, 3), dtype=np.uint8)
            error_frame.fill(20)
            cv2.putText(error_frame, f"Error: {str(e)[:50]}", (50, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(error_frame, "Click 'Stop Monitoring' to close", (50, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            rgbImage = cv2.cvtColor(error_frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, 854, 480, 854 * 3, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)
            # Keep showing error frame
            while self.running:
                time.sleep(0.1)
                self.changePixmap.emit(p)
    
    def process_image(self, image_path, net, classes, layer_names, output_layers, colors, font):
        """Process a single image file"""
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Could not load image from {image_path}")
            return

        height, width, channels = frame.shape
        
        # Running the detection model
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)
        
        # Evaluating detections
        weapon_detected = self.process_detections(frame, outs, width, height, classes, colors, font)
        
        if weapon_detected:
            self.play_alarm()
        
        # Showing final result
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        bytesPerLine = channels * width
        convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
        self.changePixmap.emit(p)
    
    def process_video(self, cap, net, classes, layer_names, output_layers, colors, font):
        """Process video stream (camera or video file)"""
        if not cap.isOpened():
            self.error_occurred = True
            # Show error message and create a blank frame with error text
            error_frame = np.zeros((480, 854, 3), dtype=np.uint8)
            error_frame.fill(20)  # Dark background
            cv2.putText(error_frame, "Error: Could not open camera", (50, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(error_frame, "Please check your camera connection", (50, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(error_frame, "Click 'Stop Monitoring' to close", (50, 300), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            rgbImage = cv2.cvtColor(error_frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, 854, 480, 854 * 3, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)
            # Keep window open even with error - continuously show error frame
            while self.running:
                time.sleep(0.1)
                # Re-emit error frame periodically to keep it visible
                self.changePixmap.emit(p)
            if cap:
                cap.release()
            return
        
        frame_count = 0
        consecutive_failures = 0
        last_detection_time = 0
        
        # Detection while loop - optimized for real-time video
        while self.running:
            # Clear buffer by reading and discarding old frames (keep only latest)
            # This ensures we always show the most recent frame (reduces lag)
            for _ in range(2):  # Read and discard 2 frames to clear buffer (reduced for speed)
                cap.grab()  # Fast grab without decoding
            
            # Read the latest frame
            ret, frame = cap.read()
            if not ret:
                consecutive_failures += 1
                frame_count += 1
                # If we can't read frames for too long, show error but keep window open
                if consecutive_failures > 30:  # After 30 failed attempts
                    error_frame = np.zeros((480, 854, 3), dtype=np.uint8)
                    error_frame.fill(20)  # Dark background
                    cv2.putText(error_frame, "Camera disconnected or not available", (50, 200), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(error_frame, "Please check your camera connection", (50, 250), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(error_frame, "Click 'Stop Monitoring' to close", (50, 300), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
                    rgbImage = cv2.cvtColor(error_frame, cv2.COLOR_BGR2RGB)
                    convertToQtFormat = QImage(rgbImage.data, 854, 480, 854 * 3, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                    time.sleep(0.1)
                    continue
                time.sleep(0.01)
                continue
            
            consecutive_failures = 0  # Reset on successful read
            frame_count = 0  # Reset counter on successful read
            height, width, channels = frame.shape
            
            # SHOW FRAME IMMEDIATELY FIRST - don't wait for anything
            # Apply last detection result if available (draw boxes continuously on current frame)
            display_frame = frame.copy()
            current_time = time.time()
            
            # Check if background detection finished
            if self.detection_future and self.detection_future.done():
                try:
                    weapon_detected, boxes, confidences, class_ids = self.detection_future.result()
                    
                    # Update stability counter
                    if weapon_detected:
                        self.consecutive_detections += 1
                    else:
                        self.consecutive_detections = 0
                    
                    # Store result for continuous display (persistent boxes)
                    if weapon_detected:
                        self.last_detection_result = (boxes, confidences, class_ids, classes, colors, font)
                        self.detection_result_time = current_time  # Update timestamp
                    else:
                        # Keep last result for a short time (persistent boxes)
                        if (current_time - self.detection_result_time) > self.result_ttl:
                            self.last_detection_result = None
                    
                    self.is_detecting = False
                    self.detection_future = None
                except Exception as e:
                    print(f"Error retrieving detection result: {e}")
                    self.is_detecting = False
                    self.detection_future = None

            # Keep detection boxes visible for a short time (persistent boxes)
            if self.last_detection_result is not None and (current_time - self.detection_result_time) < self.result_ttl:
                # Draw boxes from last detection on current frame (continuous display)
                boxes, confidences, class_ids, classes, colors, font = self.last_detection_result
                if len(boxes) > 0:
                    indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.min_confidence, 0.3)
                    if len(indexes) > 0:
                        if isinstance(indexes, np.ndarray):
                            indexes = indexes.flatten()
                        for i in indexes:
                            if i < len(boxes):
                                x, y, w, h = boxes[i]
                                label = str(classes[class_ids[i]])
                                confidence = confidences[i]
                                color = (0, 0, 255)  # Bright red color for weapons
                                
                                # Draw thick, bright red rectangle (very visible)
                                cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 4)
                                
                                # Draw second rectangle for emphasis
                                cv2.rectangle(display_frame, (x + 2, y + 2), (x + w - 2, y + h - 2), color, 2)
                                
                                # Draw filled rectangle for label background (better visibility)
                                label_text = f"{label}: {confidence:.1%}"
                                font_scale = 0.9
                                thickness = 2
                                (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
                                
                                # Background rectangle for text
                                cv2.rectangle(display_frame, (x, y - text_height - 15), 
                                            (x + text_width + 15, y), color, -1)
                                
                                # Draw white text on red background (clear probability display)
                                cv2.putText(display_frame, label_text, (x + 8, y - 8), 
                                           font, font_scale, (255, 255, 255), thickness)
            
            # Show frame IMMEDIATELY (before detection processing)
            # Use high-quality scaling for clear video
            rgbImage = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            bytesPerLine = channels * width
            convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
            # High-quality smooth scaling for clear, near video
            p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.changePixmap.emit(p)
            
            # NOW start new detection in background if idle
            if not self.is_detecting:
                self.is_detecting = True
                # Make a copy for detection (don't block video display)
                detection_frame = frame.copy()
                # Submit task to executor
                self.detection_future = self.executor.submit(
                    self.run_detection_task, 
                    detection_frame, net, output_layers, width, height, classes, colors, font
                )
            
            # Play alarm only if confirmed detection
            if self.consecutive_detections >= self.detection_threshold:
                self.play_alarm()
            else:
                self.alarm_playing = False
            
            self.frame_counter += 1
            # Sleep slightly to maintain steady frame rate (prevent CPU hogging)
            time.sleep(0.005)
        
        cap.release()
    
    def process_detections_fast(self, frame, outs, width, height, classes, colors, font):
        """Process detection results and return data (fast version - no drawing)"""
        class_ids = []
        confidences = []
        boxes = []
        weapon_detected = False
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                # If detection confidence is above min_confidence a weapon was detected
                if confidence > self.min_confidence:
                    # Check if detected class is a weapon (Handgun or Knife)
                    class_name = classes[class_id] if class_id < len(classes) else "Unknown"
                    if class_name in ["Handgun", "Knife"]:
                        weapon_detected = True
                        
                        # Calculating coordinates
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        
                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

        return weapon_detected, boxes, confidences, class_ids
    
    def process_detections(self, frame, outs, width, height, classes, colors, font):
        """Process detection results and draw bounding boxes"""
        weapon_detected, boxes, confidences, class_ids = self.process_detections_fast(
            frame, outs, width, height, classes, colors, font)
        
        if len(boxes) > 0:
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)
            
            # Handle NMSBoxes return value (may be array or tuple)
            if len(indexes) > 0:
                if isinstance(indexes, np.ndarray):
                    indexes = indexes.flatten()
                elif isinstance(indexes, (list, tuple)):
                    indexes = [int(i) for i in indexes]
                
                # Draw boxes around detected objects
                for i in indexes:
                    if i < len(boxes):
                        x, y, w, h = boxes[i]
                        label = str(classes[class_ids[i]])
                        confidence = confidences[i]
                        color = (0, 0, 255)  # Red color for weapons
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, label + " {0:.1%}".format(confidence), (x, y - 20), font, 2, color, 2)
        
        return weapon_detected
