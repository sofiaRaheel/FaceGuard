# FaceGuard – Tamper-Proof Facial Attendance System with Blockchain Logging

### Secure, AI-powered, Immutable Records

---

## Project Overview

**FaceGuard** is a conceptual prototype that merges **face recognition** with **blockchain logging** to build a tamper-proof attendance system. Designed for educational or office environments, the system securely detects and logs attendance with cryptographic verification.


---

##  Objectives

- Detect and recognize faces from images
- Record attendance with secure timestamps
- Generate hashed identity logs
- Store attendance immutably on the blockchain
- Display attendance confirmation via a simple web UI


##  Tech Stack

| Technology         | Purpose                                 |
|--------------------|------------------------------------------|
| **Python**         | Core programming language                |
| **Streamlit**      | Web-based frontend                       |
| **OpenCV**         | Image preprocessing                      |
| **face_recognition** | Face encoding and comparison           |
| **Pillow (PIL)**   | Image handling in Python                 |
| **Web3.py**        | Smart contract interaction on blockchain |
| **Ganache / Local Blockchain** | Simulated Ethereum environment   |

---

## Key Concepts Explored

- Face detection and encoding
- Face comparison and recognition
- Hashing (SHA256) for identity verification
- Smart contracts for secure record storage
- UI interaction via Streamlit



## How It Works

1. **Face Registration**  
   Upload a face image and enter a name. The face is encoded and saved locally with the name.

2. **Take Attendance**  
   Upload an image. The system compares detected faces to known faces. If matched, attendance is recorded.

3. **Blockchain Logging**  
   Attendance data (name + timestamp) is hashed using SHA256 and logged immutably to the blockchain.

4. **View Records**  
   See all attendance records with validation status (i.e., hash verification).

---

