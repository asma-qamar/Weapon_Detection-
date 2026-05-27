# Weapon_Detection-
Real-time weapon detection system using OpenCV and phone camera with alarm alert.
# Weapon Detection System Using OpenCV and YOLOv4

A real-time weapon detection system built using Python, OpenCV, and YOLOv4.  
This project detects weapons from a live camera feed and generates an alarm alert when a weapon is detected.

The system can work with a laptop webcam or a mobile phone camera connected through an IP camera application.

---

## Project Overview

The main purpose of this project is to detect weapons in real-time using computer vision and deep learning.

The system captures live video frames from a camera, processes those frames using OpenCV, and uses the YOLOv4 object detection model to identify weapons. When a weapon is detected, the system shows the detection result and generates an alarm alert.

This project is useful for:

- Security monitoring
- Surveillance systems
- Smart camera systems
- Computer vision learning
- AI-based safety projects
- Final year projects

---

## Features

- Real-time weapon detection
- Live camera feed support
- Mobile phone camera/IP camera support
- YOLOv4-based object detection
- OpenCV-based video processing
- Alarm alert when a weapon is detected
- User interface for system interaction
- Login and registration interface
- Fast frame processing
- Bounding box display on detected objects
- Suitable for security and surveillance use cases

---

## Technologies Used

- Python
- OpenCV
- YOLOv4
- NumPy
- PyQt5 / Qt Designer
- Deep Learning
- Computer Vision

---

## What is YOLO?

YOLO stands for **You Only Look Once**.

YOLO is a deep learning object detection algorithm. It is used to detect objects in images and videos. Unlike some older detection methods, YOLO looks at the image only once and predicts object locations and class labels very quickly.

Because of its speed, YOLO is commonly used in real-time applications such as:

- CCTV surveillance
- Traffic monitoring
- Face detection
- Object detection
- Weapon detection
- Security alert systems

---

## Why YOLOv4 is Used in This Project

YOLOv4 is used in this project because it is fast and accurate for real-time object detection.

In this project, YOLOv4 helps to:

- Detect weapons from camera frames
- Identify the location of the weapon
- Draw a bounding box around the detected weapon
- Show the confidence score
- Trigger an alarm when a weapon is detected

YOLOv4 is suitable for this project because weapon detection requires fast response and real-time processing.

---

## How the System Works

1. The user starts the application.
2. The camera feed is opened using OpenCV.
3. The system captures frames from the live video.
4. Each frame is passed to the YOLOv4 detection model.
5. YOLOv4 checks whether a weapon is present in the frame.
6. If a weapon is detected, the system draws a bounding box.
7. The detected weapon name and confidence score are displayed.
8. An alarm alert is generated to notify the user.

---

## YOLOv4 Files Used in This Project

This project uses the following YOLO-related files:

```text
yolov4.cfg
yolov4.weights
obj.names
```

### 1. yolov4.cfg

The `yolov4.cfg` file contains the YOLOv4 model configuration.

It defines:

- Model layers
- Convolutional layers
- Detection layers
- Input size
- Network structure

In this project, the file is located at:

```text
Client_Side/cfg/yolov4.cfg
```

---

### 2. yolov4.weights

The `yolov4.weights` file contains the trained model weights.

This file is responsible for the actual detection ability of the YOLO model. Without this file, the model configuration cannot detect objects properly.

In this project, the required path should be:

```text
Client_Side/weights/yolov4.weights
```

Important:

The `yolov4.weights` file is not uploaded to this GitHub repository because it is a large file.

File size:

```text
Approximately 244 MB
```

GitHub does not allow large files to be uploaded normally, so the weights file must be downloaded separately.

---

### 3. obj.names

The `obj.names` file contains the class names that the YOLO model can detect.

Example:

```text
weapon
gun
knife
```

In this project, the file is located at:

```text
Client_Side/obj.names
```

The detection output depends on the classes written inside this file.

---

## Important Note About YOLO Weights

The YOLOv4 weights file is required to run the detection system.

Required file:

```text
yolov4.weights
```

Required location:

```text
Client_Side/weights/yolov4.weights
```

If the `weights` folder does not exist, create it manually inside `Client_Side`.

Final path should look like this:

```text
Weapon_Detection/
└── Client_Side/
    └── weights/
        └── yolov4.weights
```

Download link for YOLO weights:

```text
Add your Google Drive link here
```

Example:

```text
https://drive.google.com/your-yolov4-weights-link
```

---

## Project Structure

```text
Weapon_Detection/
│
├── Client_Side/
│   │
│   ├── cfg/
│   │   └── yolov4.cfg
│   │
│   ├── UI/
│   │   ├── detection_window.ui
│   │   ├── login_window.ui
│   │   ├── main_window.ui
│   │   └── register_window.ui
│   │
│   ├── weights/
│   │   └── yolov4.weights
│   │
│   ├── detection.py
│   ├── detection_window.py
│   ├── login_window.py
│   ├── main.py
│   ├── main_window.py
│   ├── obj.names
│   ├── register_window.py
│   ├── requirements.txt
│   ├── run.bat
│   ├── user_storage.py
│   └── users.json
│
├── .gitattributes
├── .gitignore
└── README.md
```

Note:

The `weights` folder and `yolov4.weights` file may not be available directly in the repository. You need to add the weights file manually after downloading it.

---

## Requirements

Before running the project, install the required Python libraries.

Install dependencies using:

```bash
pip install -r Client_Side/requirements.txt
```

Common libraries used in this project:

```text
opencv-python
numpy
PyQt5
```

---

## How to Run the Project

### Step 1: Clone the Repository

```bash
git clone https://github.com/asma-qamar/Weapon_Detection-.git
```

---

### Step 2: Open the Project Folder

```bash
cd Weapon_Detection-
```

---

### Step 3: Install Required Libraries

```bash
pip install -r Client_Side/requirements.txt
```

---

### Step 4: Add YOLOv4 Weights File

Download the `yolov4.weights` file and place it inside:

```text
Client_Side/weights/
```

The final path must be:

```text
Client_Side/weights/yolov4.weights
```

---

### Step 5: Run the Application

Run the main Python file:

```bash
python Client_Side/main.py
```

Or run the batch file:

```bash
Client_Side/run.bat
```

---

## Phone Camera Setup

This project can also use a mobile phone camera as a live camera source.

To use a phone camera:

1. Install an IP camera application on your mobile phone.
2. Connect your phone and laptop to the same Wi-Fi network.
3. Start the camera server from the mobile app.
4. Copy the camera stream URL.
5. Add that URL in the Python code where camera source is used.

Example IP camera URL:

```python
http://192.168.1.5:8080/video
```

Example OpenCV camera connection:

```python
import cv2

camera_url = "http://192.168.1.5:8080/video"
cap = cv2.VideoCapture(camera_url)
```

For laptop webcam, the camera source is usually:

```python
cap = cv2.VideoCapture(0)
```

---

## Detection Output

When a weapon is detected, the system can display:

- Weapon name
- Confidence score
- Bounding box around the weapon
- Alarm alert

Example detection result:

```text
Weapon Detected
Confidence: 87%
Alarm Triggered
```

---

## Alarm System

The alarm system is used to alert the user when a weapon is detected.

When YOLOv4 detects a weapon in the camera frame, the project triggers an alert. This can help security staff or users respond quickly.

The alarm may be generated using:

- Audio alert
- Warning message
- Detection window notification

---

## Use Cases

This project can be used in:

- Security systems
- CCTV monitoring
- Public safety applications
- Smart surveillance systems
- Office security
- Campus security
- AI and computer vision research
- Final year project demonstrations

---

## Limitations

This project has some limitations:

- Accuracy depends on the trained YOLOv4 model.
- Poor lighting can reduce detection accuracy.
- Blurry video may affect detection results.
- Small or hidden weapons may not be detected properly.
- False positives may occur in some cases.
- The YOLO weights file must be downloaded separately.
- System performance depends on laptop/PC hardware.

---

## Future Improvements

Possible future improvements:

- Add email alert system
- Add SMS notification system
- Add WhatsApp alert
- Add CCTV camera support
- Add detection history database
- Add admin dashboard
- Add detection logs
- Improve YOLO model accuracy
- Train model on more weapon images
- Add multiple camera support
- Add cloud storage for alerts
- Add face recognition with weapon detection

---

## Safety and Legal Disclaimer

This project is developed for educational, academic, and security research purposes only.

The system should be used responsibly and only in legal and authorized environments. The developer is not responsible for any misuse of this project.

---

## Author

Developed by:

```text
asma-qamar
```

GitHub Profile:

```text
https://github.com/asma-qamar
```

---

## Repository Link

```text
https://github.com/asma-qamar/Weapon_Detection-
```

---

## Conclusion

This Weapon Detection System demonstrates how computer vision and deep learning can be used for real-time security applications. By using OpenCV and YOLOv4, the system can detect weapons from a live camera feed and generate an alarm alert when a weapon appears.

This project is a practical example of AI-based surveillance and real-time object detection.
