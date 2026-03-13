"""
Face Recognition Integration Module for ClassGenius
Bridges the face recognition system with the Streamlit app
"""

import cv2
import os
import csv
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import time
from pathlib import Path


class FaceRecognitionBridge:
    """Manages face recognition operations for ClassGenius"""
    
    def __init__(self, base_path="../Face_recognition_based_attendance_system-master"):
        # Handle relative path
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        self.base_path = os.path.join(parent_dir, "Face_recognition_based_attendance_system-master")
        
        # Ensure base path exists
        os.makedirs(self.base_path, exist_ok=True)
        
        self.training_image_dir = os.path.join(self.base_path, "TrainingImage")
        self.training_label_dir = os.path.join(self.base_path, "TrainingImageLabel")
        self.attendance_dir = os.path.join(self.base_path, "Attendance")
        self.student_details_dir = os.path.join(self.base_path, "StudentDetails")
        self.student_details_path = os.path.join(self.student_details_dir, "StudentDetails.csv")
        self.haarcascade_path = os.path.join(self.base_path, "haarcascade_frontalface_default.xml")
        self.trainer_path = os.path.join(self.training_label_dir, "Trainner.yml")
        
        # Create directories if they don't exist
        self._ensure_directories()

        # Try to import DB helpers
                # Try to import DB helpers
                # Import CSV helpers instead of database
        try:
            from .csv_helpers import insert_or_update_student, get_all_students
        except Exception:
            from csv_helpers import insert_or_update_student, get_all_students

        self._db_insert_or_update_student = insert_or_update_student
        self._db_get_all_students = get_all_students
    def _ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.training_image_dir, exist_ok=True)
        os.makedirs(self.training_label_dir, exist_ok=True)
        os.makedirs(self.attendance_dir, exist_ok=True)
        os.makedirs(self.student_details_dir, exist_ok=True)
    
    def get_next_serial_number(self):
        """Get the next serial number for student"""
        try:
            students = self._db_get_all_students()
            if students:
                max_serial = max([int(s[0]) for s in students if s[0] is not None])
                return int(max_serial) + 1
            return 1
        except Exception as e:
            print(f"Error getting serial number: {e}")
            return 1
    
    def get_existing_students(self):
        """Get list of existing students"""
        students = []
        try:
            rows = self._db_get_all_students()
            for r in rows:
                serial_no, student_id, name, email = r
                students.append({
                    'serial': int(serial_no) if serial_no is not None else None,
                    'id': student_id,
                    'name': name,
                    'email': email or ''
                })
        except Exception as e:
            print(f"Error reading students: {e}")
        
        return students
    
    def add_student(self, student_id, name, email):
        """Add a new student to the roster"""
        try:
            # Insert into DB (preserve serial if possible)
            serial = self.get_next_serial_number()
            self._db_insert_or_update_student(student_id, name, email, serial_no=serial)

            return {'success': True, 'serial': serial, 'message': f'Student {name} added successfully'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error adding student: {e}'}
    
    def capture_student_photos(self, student_id, num_samples=30, sample_interval=100):
        """Capture training photos for a student"""
        try:
            # Get student serial number
            students = self.get_existing_students()
            student = next((s for s in students if s['id'] == student_id), None)

            if not student:
                return {'success': False, 'message': f'Student {student_id} not found'}

            serial = student['serial']
            
            # Load cascade classifier
            if not os.path.exists(self.haarcascade_path):
                # Use the default cascade from OpenCV
                haarcascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            else:
                haarcascade_path = self.haarcascade_path
            
            face_cascade = cv2.CascadeClassifier(haarcascade_path)
            
            if face_cascade.empty():
                return {'success': False, 'message': 'Failed to load face cascade classifier'}
            
            cam = cv2.VideoCapture(0)
            
            if not cam.isOpened():
                return {'success': False, 'message': 'Cannot access webcam. Please check webcam connection.'}
            
            # Set camera properties for better quality
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            count = 0
            frame_skip = 0
            captured_count = 0
            
            import time
            start_time = time.time()
            
            while captured_count < num_samples:
                ret, frame = cam.read()
                
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        frame_skip += 1
                        
                        if frame_skip % sample_interval == 0:
                            # Save the captured image
                            img_path = os.path.join(
                                self.training_image_dir,
                                f"{student_id}.{serial}.{captured_count}.jpg"
                            )
                            cv2.imwrite(img_path, gray[y:y+h, x:x+w])
                            captured_count += 1
                            
                            # Draw rectangle on frame
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, f'Captured: {captured_count}/{num_samples}',
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, 'No face detected! Look at camera.',
                              (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Add progress bar
                cv2.putText(frame, f'Progress: {captured_count}/{num_samples}',
                          (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow("Capturing Photos - Press 'q' to stop", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Timeout after 5 minutes
                if time.time() - start_time > 300:
                    break
                
                count += 1
            
            cam.release()
            cv2.destroyAllWindows()
            
            if captured_count == 0:
                return {'success': False, 'message': 'No photos captured. Please check webcam and lighting.'}
            
            return {
                'success': True,
                'message': f'Successfully captured {captured_count} samples for {student_id}',
                'samples_captured': captured_count
            }
        
        except Exception as e:
            import traceback
            return {'success': False, 'message': f'Error capturing photos: {str(e)}\n{traceback.format_exc()}'}
    
    def train_model(self):
        """Train the face recognition model"""
        try:
            # Get training images
            path = self.training_image_dir
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            # Read training images
            faces = []
            ids = []
            
            for imageName in os.listdir(path):
                imagePath = os.path.join(path, imageName)
                img = Image.open(imagePath).convert('L')
                imgarray = np.array(img, 'uint8')
                id_num = int(os.path.split(imageName)[-1].split(".")[1])
                
                faces.append(imgarray)
                ids.append(id_num)
            
            # Train the model
            recognizer.train(faces, np.array(ids))
            recognizer.save(self.trainer_path)
            
            return {'success': True, 'message': f'Model trained successfully with {len(faces)} samples'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error training model: {e}'}
    
    def take_attendance(self, confidence_threshold=150):
        """Take attendance using face recognition"""
        try:
            if not os.path.exists(self.trainer_path):
                return {'success': False, 'message': 'Model not trained. Please train the model first.'}
            
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(self.trainer_path)
            
            # Load haarcascade with fallback
            if os.path.exists(self.haarcascade_path):
                face_cascade = cv2.CascadeClassifier(self.haarcascade_path)
            else:
                # Use OpenCV's default haarcascade
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if face_cascade.empty():
                return {'success': False, 'message': 'Could not load face detection model'}
            cam = cv2.VideoCapture(0)
            
            if not cam.isOpened():
                return {'success': False, 'message': 'Cannot access webcam'}
            
            # Get student details from DB
            rows = self._db_get_all_students()
            # Map serial -> (student_id, name)
            serial_map = {}
            for r in rows:
                serial_no, student_id, name, _ = r
                if serial_no is not None:
                    serial_map[int(serial_no)] = (student_id, name)

            # Load student details into a DataFrame for lookups (fallback to DB rows)
            df = None
            try:
                if os.path.exists(self.student_details_path):
                    df = pd.read_csv(self.student_details_path)
            except Exception:
                df = None

            if df is None or df.empty:
                data = []
                for r in rows:
                    serial_no, student_id, name, _ = r
                    data.append({
                        'SERIAL NO.': int(serial_no) if serial_no is not None else None,
                        'ID': student_id,
                        'NAME': name
                    })
                df = pd.DataFrame(data)
            
            # Prepare attendance file
            today = datetime.now().strftime('%d-%m-%Y')
            attendance_file = os.path.join(self.attendance_dir, f"Attendance_{today}.csv")
            
            marked_ids = set()
            recognized_students = []
            
            while True:
                ret, frame = cam.read()
                
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    try:
                        serial, conf = recognizer.predict(gray[y:y+h, x:x+w])
                    except Exception as e:
                        print(f"Prediction error: {e}")
                        continue
                    
                    if conf < confidence_threshold:
                        student_row = df[df['SERIAL NO.'] == serial]
                        if len(student_row) > 0:
                            student_id = student_row['ID'].values[0]
                            name = student_row['NAME'].values[0]
                            
                            if student_id not in marked_ids:
                                # Record attendance
                                time_str = datetime.now().strftime('%H:%M:%S')
                                
                                # Record attendance into DB (and also append CSV for compatibility)
                                try:
                                    self._db_add_attendance_record(student_id, name, today, time_str)
                                except Exception:
                                    pass

                                file_exists = os.path.exists(attendance_file)
                                with open(attendance_file, 'a', newline='') as f:
                                    writer = csv.writer(f)
                                    if not file_exists:
                                        writer.writerow(['Id', '', 'Name', '', 'Date', '', 'Time'])
                                    writer.writerow([student_id, '', name, '', today, '', time_str])

                                marked_ids.add(student_id)
                                recognized_students.append({
                                    'id': student_id,
                                    'name': name,
                                    'time': time_str
                                })
                            
                            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                cv2.imshow("Taking Attendance", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cam.release()
            cv2.destroyAllWindows()
            
            return {
                'success': True,
                'message': f'Attendance recorded for {len(recognized_students)} students',
                'students': recognized_students,
                'attendance_file': attendance_file
            }
        
        except Exception as e:
            return {'success': False, 'message': f'Error taking attendance: {e}'}
    
    def get_today_attendance_list(self):
        """Get list of students marked present today"""
        try:
            today = datetime.now().strftime('%d-%m-%Y')
            attendance_file = os.path.join(self.attendance_dir, f"Attendance_{today}.csv")
            
            if not os.path.exists(attendance_file):
                return {'success': True, 'present': [], 'message': 'No attendance recorded yet'}
            
            df = pd.read_csv(attendance_file)
            present_students = df['Id'].unique().tolist()
            present_students = [s for s in present_students if pd.notna(s) and s != '']
            
            return {
                'success': True,
                'present': present_students,
                'count': len(present_students)
            }
        
        except Exception as e:
            return {'success': False, 'message': f'Error reading attendance: {e}'}
