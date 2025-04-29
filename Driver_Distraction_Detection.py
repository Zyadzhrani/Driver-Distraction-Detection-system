import RPi.GPIO as GPIO
import threading
import subprocess
import time
import datetime
import os
from ultralytics import YOLO
import cv2
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import rotate, translate

# === GPIO Setup ===
BUTTON_PIN = 22  # GPIO 22 (Pin 15) For the Push Button 
BUZZER_PIN = 27  # GPIO 27 (Pin 13) For the Buzzer

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# === Function to Trigger PDF_FILE.py ===
def trigger_pdf_script():
    print("📄 Starting PDF_FILE.py script...")
    subprocess.Popen(['python3', 'PDF_FILE.py'])  # Non-blocking call

# === Button Listener Thread ===
def button_listener():
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("🔘 Button PRESSED! Starting PDF_FILE.py...")
            trigger_pdf_script()
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Wait for release
                time.sleep(0.05)
            print("⚪ Button RELEASED!")
        time.sleep(0.1)

# === Start Button Listener Thread ===
button_thread = threading.Thread(target=button_listener, daemon=True)
button_thread.start()

# === Capture Image Function ===
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return None

    time.sleep(2)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Error: Can't receive frame.")
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"captured_{timestamp}.jpg"
    cv2.imwrite(image_path, frame)
    print(f"📸 Image captured: {image_path}")
    return image_path

# === OBB Functions ===
def obb_to_polygon(x_center, y_center, width, height, angle_deg):
    box = Polygon([
        (-width / 2, -height / 2),
        (width / 2, -height / 2),
        (width / 2, height / 2),
        (-width / 2, height / 2)
    ])
    rotated = rotate(box, angle_deg, use_radians=False)
    return translate(rotated, xoff=x_center, yoff=y_center)

def hand_overlap_with_wheel(hand_obb, wheel_obb):
    hand_poly = obb_to_polygon(*hand_obb)
    wheel_poly = obb_to_polygon(*wheel_obb)
    inter_area = hand_poly.intersection(wheel_poly).area
    hand_area = hand_poly.area
    percent_overlap = (inter_area / hand_area) * 100 if hand_area > 0 else 0
    return percent_overlap

# === Analyze Function ===
def Deiver_Distraction_Detection(results, hand_threshold=50):
    hand_obbs, wheel_obbs = [], []
    
    output = {
        "using_mobile_phone": False,
        "talking_on_phone_left": False,
        "talking_on_phone_right": False,
        "talking_to_passenger": False,
        "hands_not_on_wheel": False,
        "hand_wheel_overlap": []
    }

    for obb in results.obb:
        x, y, w, h, angle = obb.xywhr[0].cpu().numpy()
        cls = int(obb.cls[0].item())
        angle_deg = angle * 180 / np.pi
        box = [x, y, w, h, angle_deg]

        if cls == 3:
            output["using_mobile_phone"] = True
        elif cls == 6:
            output["talking_on_phone_left"] = True
        elif cls == 7:
            output["talking_on_phone_right"] = True
        elif cls == 0:
            output["talking_to_passenger"] = True
        elif cls == 1:
            hand_obbs.append(box)
        elif cls == 4:
            wheel_obbs.append(box)

    if not wheel_obbs:
        print("⚠️ No steering wheel detected.")
        return output

    wheel = wheel_obbs[0]

    hand_statuses = []
    for i, hand in enumerate(hand_obbs[:2]):
        percent = hand_overlap_with_wheel(hand, wheel)
        status = "Fully on the wheel" if percent >= hand_threshold else "Not on the wheel"
        hand_statuses.append(status)
        output["hand_wheel_overlap"].append({
            "hand": i + 1,
            "overlap_percent": round(percent, 1),
            "status": status
        })

    if len(hand_statuses) < 2 or any(s != "Fully on the wheel" for s in hand_statuses):
        output["hands_not_on_wheel"] = True

    return output

# === Main Loop ===
if __name__ == "__main__":
    model_path = "Yolov8s_OBB.pt" # Model Path
    model = YOLO(model_path)
    save_dir = "predictions" # a folder to save the annotate images 
    os.makedirs(save_dir, exist_ok=True)

    while True:
        log_file = "destraction_save.txt" # Text file for the recorded Distractions that help to generate the report 
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(now + "\n")
                f.write("0\n" * 4)
            print(f"📝 Created and initialized log file: {log_file}")

        img_path = capture_image()
        if img_path:
            results = model(img_path)[0]
            annotated_img = results.plot()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            annotated_path = os.path.join(save_dir, f"annotated_{timestamp}.jpg")
            cv2.imwrite(annotated_path, annotated_img)
            os.remove(img_path)
            print(f"📝 Annotated image saved: {annotated_path}")

            result = Deiver_Distraction_Detection(results,hand_threshold=48)
            with open(log_file, "r") as f:
                lines = f.readlines()
            count_mobile = int(lines[1].strip())
            count_phone = int(lines[2].strip())
            count_passenger = int(lines[3].strip())
            count_hands = int(lines[4].strip())
            if result['using_mobile_phone']:
                count_mobile += 1
            if result['talking_on_phone_left'] or result['talking_on_phone_right']:
                count_phone += 1
            if result['talking_to_passenger']:
                count_passenger += 1
            if result['hands_not_on_wheel']:
                count_hands += 1
            lines[1] = f"{count_mobile}\n"
            lines[2] = f"{count_phone}\n"
            lines[3] = f"{count_passenger}\n"
            lines[4] = f"{count_hands}\n"
            with open(log_file, "w") as f:
                f.writelines(lines)

            # === Trigger Buzzer if distraction ===
            if any([
                result['using_mobile_phone'],
                result['talking_on_phone_left'],
                result['talking_on_phone_right'],
                result['talking_to_passenger'],
                result['hands_not_on_wheel']
            ]):
                print("🚨 Distraction detected! Activating buzzer for 2 seconds...")
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(BUZZER_PIN, GPIO.LOW)

            print("\n Final Result:")
            print(" Using Mobile Phone:", result['using_mobile_phone'])
            print(" Talking on Phone (Left):", result['talking_on_phone_left'])
            print(" Talking on Phone (Right):", result['talking_on_phone_right'])
            print(" Talking to Passenger:", result['talking_to_passenger'])
            print(" Hands Not on Wheel:", result['hands_not_on_wheel'])
            print("\n Hand-Wheel Overlap Details:")
            for hand in result['hand_wheel_overlap']:
                print(f"  Hand {hand['hand']}: {hand['overlap_percent']}% → {hand['status']}")

        print("⏳ Finish one process\n")
        
