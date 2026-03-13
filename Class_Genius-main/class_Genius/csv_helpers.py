import os
import csv

STUDENT_DETAILS_PATH = "../Face_recognition_based_attendance_system-master/StudentDetails/StudentDetails.csv"

def get_all_students():
    """Get all students from CSV - returns list of tuples (serial, id, name, email)"""
    students = []
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, STUDENT_DETAILS_PATH)
        if os.path.exists(path):
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row and row.get('ID'):
                        students.append((
                            row.get('SERIAL NO.', ''),
                            row.get('ID', ''),
                            row.get('NAME', ''),
                            row.get('EMAIL', '')
                        ))
    except Exception as e:
        print(f"Error reading student details: {e}")
    return students

def insert_or_update_student(student_id, name, email, serial_no=None):
    """Add/update student in CSV"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, STUDENT_DETAILS_PATH)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        students = []
        if os.path.exists(path):
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                students = list(reader)
        
        # Find if exists
        found = False
        for s in students:
            if s.get('ID') == student_id:
                s['NAME'] = name
                s['EMAIL'] = email
                found = True
                break
        
        if not found:
            serial = serial_no if serial_no else len(students) + 1
            students.append({
                'SERIAL NO.': str(serial),
                'ID': student_id,
                'NAME': name,
                'EMAIL': email
            })
        
        # Write back
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['SERIAL NO.', 'ID', 'NAME', 'EMAIL'])
            writer.writeheader()
            writer.writerows(students)
    except Exception as e:
        print(f"Error updating student: {e}")