import streamlit as st
from PIL import Image
import cv2
import numpy as np
import face_recognition
import hashlib
import os
from datetime import datetime
from blockchain_logger import BlockchainLogger

def prepare_image(pil_image):
    """
    Converts a PIL image to a proper NumPy RGB uint8 image for face_recognition.
    """
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")

    img_array = np.array(pil_image)

    if img_array.dtype != np.uint8:
        img_array = (255 * (img_array / np.max(img_array))).astype(np.uint8)

    if img_array.ndim != 3 or img_array.shape[2] != 3:
        raise ValueError("Image must have 3 color channels (RGB)")

    return img_array

class FaceGuard:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.attendance_records = []
        self.load_known_faces()

        # ✅ Initialize blockchain logger
        self.blockchain = BlockchainLogger(
            abi_path="Attendance_compData.json",
            contract_address="0xD7e59cF6A438EACB2a4AD8A6Cf9FA3Bf87a55264",
            private_key="0x99e22e0f50e07ef8ab19c2b1f93f9787733d19654f55bc2ecba9c9cbce391a70"
        )

    def load_known_faces(self):
        known_faces_dir = "known_faces"
        if not os.path.exists(known_faces_dir):
            os.makedirs(known_faces_dir)
            return

        for filename in os.listdir(known_faces_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                image_path = os.path.join(known_faces_dir, filename)
                image = cv2.imread(image_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                equalized = cv2.equalizeHist(gray)
                processed_image = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
                face_encodings = face_recognition.face_encodings(processed_image)

                if face_encodings:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])

    def register_new_face(self, name, image):
        try:
            img_array = prepare_image(image)
        except Exception as e:
            print(f"Image preparation failed: {e}")
            return False

        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        equalized = cv2.equalizeHist(gray)
        processed_img = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
        face_encodings = face_recognition.face_encodings(processed_img)

        if face_encodings:
            self.known_face_encodings.append(face_encodings[0])
            self.known_face_names.append(name)
            os.makedirs("known_faces", exist_ok=True)
            cv2.imwrite(f"known_faces/{name}.jpg", cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
            return True
        return False

    def recognize_face(self, image):
        try:
            img_array = prepare_image(image)
        except Exception as e:
            print(f"❌ Image preparation failed: {e}")
            return [], []

        try:
            face_locations = face_recognition.face_locations(img_array)
            face_encodings = face_recognition.face_encodings(img_array, face_locations)
        except Exception as e:
            print(f"❌ face_recognition failed: {e}")
            return [], []

        recognized_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if face_distances.size > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    self.record_attendance(name)
            recognized_names.append(name)

        return recognized_names, face_locations

    def record_attendance(self, name):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_hash = hashlib.sha256(f"{name}{timestamp}".encode()).hexdigest()
        record = {"name": name, "timestamp": timestamp, "hash": record_hash}
        self.attendance_records.append(record)

        try:
            tx_hash = self.blockchain.log_attendance(name, timestamp, record_hash)
            print(f"✔ Logged on-chain with tx: {tx_hash}")
        except Exception as e:
            print(f"❌ Blockchain log failed: {e}")

        return record

    def verify_identity(self, name, timestamp, record_hash):
        test_hash = hashlib.sha256(f"{name}{timestamp}".encode()).hexdigest()
        return test_hash == record_hash


def main():
    st.title("FaceGuard - Facial Attendance System")
    faceguard = FaceGuard()

    menu = ["Home", "Register Face", "Take Attendance", "View Records"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Welcome to FaceGuard")
        st.write("""
        - Register a face
        - Take attendance
        - View blockchain-logged records
        """)

    elif choice == "Register Face":
        st.subheader("Register New Face")
        name = st.text_input("Enter Name")
        img_file = st.file_uploader("Upload Face Image", type=["jpg", "png", "jpeg"])

        if img_file and name:
            image = Image.open(img_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_column_width=True)
            if st.button("Register Face"):
                if faceguard.register_new_face(name, image):
                    st.success(f"Face registered successfully for {name}!")
                else:
                    st.error("No face detected. Try another image.")

    elif choice == "Take Attendance":
        st.subheader("Take Attendance")
        img_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        if img_file:
            image = Image.open(img_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_column_width=True)
            if st.button("Recognize Faces"):
                names, _ = faceguard.recognize_face(image)
                if names:
                    for name in names:
                        if name != "Unknown":
                            st.success(f"Recognized: {name}")
                        else:
                            st.warning("Unknown face detected")
                else:
                    st.warning("No faces recognized.")

    elif choice == "View Records":
        st.subheader("Attendance Records")
        if not faceguard.attendance_records:
            st.info("No attendance records found.")
        else:
            for record in faceguard.attendance_records:
                st.write(f"**Name:** {record['name']}")
                st.write(f"**Time:** {record['timestamp']}")
                valid = faceguard.verify_identity(record['name'], record['timestamp'], record['hash'])
                status = "✅ Valid" if valid else "❌ Tampered"
                st.write(f"**Status:** {status}")
                st.markdown("---")

if __name__ == "__main__":
    main()
