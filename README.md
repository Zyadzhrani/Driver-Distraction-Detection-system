# 🚗 Driver Distraction Detection System

A real-time embedded system for detecting driver distractions using computer vision and deep learning on the Jetson Nano 4GB. This project was developed as part of the EE 499 Senior Design Project at King Abdulaziz University.

## 📘 Project Overview
Driver distraction is a major cause of road accidents. Our system detects four critical types of distractions:
1. Using a mobile phone
2. Talking on the phone (left or right hand)
3. Talking to passengers
4. Not holding the steering wheel

The system is designed to run on the Jetson Nano using a YOLOv8s-OBB model. It issues real-time buzzer alerts and logs all distractions, generating reports for fleet managers.

## 🔧 Hardware Components
- Jetson Nano 4GB
- Arducam 1080p RGB-IR Camera
- Buzzer (with transistor circuit)
- Push Button (for generating PDF reports)
- Buzzer for alerts
- 12V car power adapter
- Custom 3D printed mounts and case

## 🧠 Software & Tools
- YOLOv8s-OBB from Ultralytics
- OpenCV (Image capture and display)
- Shapely (Geometric calculations for OBB)
- Jetson.GPIO for GPIO interaction
- Threading + Subprocess for multitasking
- Python 3.8
- JetPack SDK + PyTorch + CUDA/cuDNN

## 🗂️ Features
- Real-time image capture every 30 seconds
- YOLOv8s-OBB based object detection with rotated bounding boxes
- Custom distraction analysis logic
- 2-second buzzer alert when a distraction is detected
- Button trigger to generate `PDF_FILE.py` report in a separate thread
- Automatic logging of distraction types and counts
- Deletes captured image after use to save disk space

## 📸 Classes Detected
| Class ID | Class Name               |
|----------|--------------------------|
| 0        | Talking to Passenger     |
| 1        | Hands                    |
| 3        | Using Mobile Phone       |
| 4        | Steering Wheel           |
| 6        | Talking on Phone (Left)  |
| 7        | Talking on Phone (Right) |
| 8        | Normal Face              |

## 🧪 Validation
- Achieved over **91% mAP@0.5**
- Successfully deployed on Jetson Nano for real-time performance
- Robust under both day and night conditions using RGB + IR camera

## 📝 Report Generation
- A push button connected to GPIO 22 allows the user to trigger `PDF_FILE.py`, which generates a summary report of the logged distractions.

## 🛡️ Standards Followed
- ISO 15005:2017 (Ergonomics for driver feedback)
- ISO 11452 (EMC for automotive systems)
- USB-IF compliance for storage
- Operating range: -10°C to 70°C, vibration-resistant

## ⚙️ Future Work
- Expand distraction classes (e.g., eating, drowsiness)
- Add dashboard for remote fleet management
- Integrate haptic or visual alerts
- Optimize for Jetson Orin Nano

---

## 📜 License
This project is part of the EE 499 Senior Design Course at King Abdulaziz University. Use is permitted for educational and non-commercial purposes only.
