import json
import os
import hashlib

# File to store user data
USER_DATA_FILE = "users.json"

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(firstname, lastname, password):
    """Register a new user"""
    users = load_users()
    
    # Create username from firstname and lastname
    username = f"{firstname.lower()}_{lastname.lower()}"
    
    # Check if user already exists
    if username in users:
        return False, "User already exists"
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Store user
    users[username] = {
        'firstname': firstname,
        'lastname': lastname,
        'password': hashed_password
    }
    
    save_users(users)
    return True, username

def login_user(username, password):
    """Login user"""
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    hashed_password = hash_password(password)
    
    if users[username]['password'] == hashed_password:
        return True, users[username]
    else:
        return False, "Incorrect password"

