"""
Attendance Integration Module
Connects Face Recognition System with ClassGenius to send notes to absentees
"""

import csv
import os
from datetime import datetime
from pathlib import Path

class AttendanceManager:
    """Manages attendance data from face recognition system"""
    
    def __init__(self, attendance_dir="../Face_recognition_based_attendance_system-master/Attendance"):
        self.attendance_dir = attendance_dir
        self.student_details_path = "../Face_recognition_based_attendance_system-master/StudentDetails/StudentDetails.csv"
    
    def get_today_attendance(self):
        """Get list of students who marked attendance today"""
        today = datetime.now().strftime('%d-%m-%Y')
        attendance_file = os.path.join(self.attendance_dir, f"Attendance_{today}.csv")
        
        marked_students = set()
        
        if os.path.exists(attendance_file):
            try:
                with open(attendance_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row and row.get('Id'):
                            marked_students.add(row['Id'].strip())
            except Exception as e:
                print(f"Error reading attendance file: {e}")
        
        return marked_students
    
    def get_all_students(self):
        """Get list of all registered students"""
        all_students = {}
        
        if os.path.exists(self.student_details_path):
            try:
                with open(self.student_details_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row and row.get('ID'):
                            student_id = row['ID'].strip()
                            all_students[student_id] = {
                                'name': row.get('NAME', ''),
                                'email': row.get('EMAIL', ''),
                                'serial': row.get('SERIAL NO.', '')
                            }
            except Exception as e:
                print(f"Error reading student details: {e}")
        
        return all_students
    
    def get_absentees(self):
        """Get list of absentees for today"""
        marked_students = self.get_today_attendance()
        all_students = self.get_all_students()
        
        absentees = {}
        for student_id, details in all_students.items():
            if student_id not in marked_students:
                absentees[student_id] = details
        
        return absentees
    
    def get_absentees_for_date(self, date_str):
        """Get list of absentees for a specific date (format: DD-MM-YYYY)"""
        marked_students = set()
        attendance_file = os.path.join(self.attendance_dir, f"Attendance_{date_str}.csv")
        
        if os.path.exists(attendance_file):
            try:
                with open(attendance_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row and row.get('Id'):
                            marked_students.add(row['Id'].strip())
            except Exception as e:
                print(f"Error reading attendance file: {e}")
        
        all_students = self.get_all_students()
        
        absentees = {}
        for student_id, details in all_students.items():
            if student_id not in marked_students:
                absentees[student_id] = details
        
        return absentees
    
    def get_attendance_percentage(self, student_id):
        """Calculate attendance percentage for a student"""
        if not os.path.exists(self.attendance_dir):
            return 0
        
        total_classes = 0
        present_classes = 0
        
        for filename in os.listdir(self.attendance_dir):
            if filename.startswith('Attendance_') and filename.endswith('.csv'):
                total_classes += 1
                filepath = os.path.join(self.attendance_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row and row.get('Id') and row['Id'].strip() == student_id:
                                present_classes += 1
                                break
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
        
        if total_classes == 0:
            return 0
        
        return (present_classes / total_classes) * 100
