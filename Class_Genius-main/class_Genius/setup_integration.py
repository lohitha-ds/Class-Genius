#!/usr/bin/env python3
"""
ClassGenius + Face Recognition Integration Setup Script
Helps configure the integration between both systems
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def setup_email_config():
    """Setup email configuration"""
    print_header("EMAIL CONFIGURATION SETUP")
    
    print_info("You need to configure Gmail for sending emails.")
    print("""
Steps to generate App Password:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not enabled)
3. Search for "App passwords"
4. Select "Mail" and "Windows Computer"
5. Generate app password (16 characters)
6. Copy the password below
    """)
    
    email = input("Enter your Gmail address: ").strip()
    app_password = input("Enter Gmail App Password: ").strip()
    email_domain = input("Enter email domain (e.g., @company.com or @gmail.com): ").strip()
    
    # Create or update config.py
    config_content = f'''"""
Email Configuration for ClassGenius
Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

EMAIL_ADDRESS = "{email}"
EMAIL_APP_PASSWORD = "{app_password}"
EMAIL_DOMAIN = "{email_domain}"
'''
    
    with open("config.py", "w") as f:
        f.write(config_content)
    
    print_success("Email configuration saved to config.py")
    return email, app_password, email_domain

def check_face_recognition_system():
    """Check if face recognition system is properly set up"""
    print_header("CHECKING FACE RECOGNITION SYSTEM")
    
    # Check for StudentDetails.csv
    student_details_path = "../Face_recognition_based_attendance_system-master/StudentDetails/StudentDetails.csv"
    
    if os.path.exists(student_details_path):
        print_success(f"Found StudentDetails.csv at {student_details_path}")
        
        # Check content
        with open(student_details_path, 'r') as f:
            lines = f.readlines()
            student_count = len(lines) - 1  # Exclude header
            print_info(f"Found {student_count} students registered")
            
            if student_count == 0:
                print_warning("No students found in StudentDetails.csv")
                print_info("Please register students in the face recognition system first")
                return False
        
        return True
    else:
        print_error(f"StudentDetails.csv not found at {student_details_path}")
        print_info("Please set up the face recognition system first:")
        print_info("1. Run Face_recognition_based_attendance_system-master/main.py")
        print_info("2. Register students and train the model")
        return False

def check_attendance_data():
    """Check if attendance data exists"""
    print_header("CHECKING ATTENDANCE DATA")
    
    attendance_dir = "../Face_recognition_based_attendance_system-master/Attendance"
    
    if os.path.exists(attendance_dir):
        attendance_files = [f for f in os.listdir(attendance_dir) if f.startswith("Attendance_")]
        print_success(f"Found {len(attendance_files)} attendance records")
        
        if len(attendance_files) > 0:
            print_info(f"Latest: {sorted(attendance_files)[-1]}")
        else:
            print_warning("No attendance records found yet")
            print_info("Run the face recognition system to generate attendance")
        
        return True
    else:
        print_warning(f"Attendance directory not found at {attendance_dir}")
        return False

def setup_database():
    """Setup or verify database"""
    print_header("SETTING UP DATABASE")
    
    db_path = "classgenius.db"
    
    if os.path.exists(db_path):
        print_warning(f"Database already exists at {db_path}")
        backup = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(db_path, backup)
        print_success(f"Backup created: {backup}")
    
    try:
        # Import and run database initialization
        from database import conn, c
        print_success("Database initialized successfully")
        print_info("Tables created:")
        print_info("  - users")
        print_info("  - notes")
        print_info("  - notes_sent_to_absentees")
        print_info("  - student_cache")
        return True
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        return False

def test_email_connection(email, app_password):
    """Test email connection"""
    print_header("TESTING EMAIL CONNECTION")
    
    try:
        import smtplib
        print_info("Attempting to connect to Gmail SMTP...")
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(email, app_password)
        server.quit()
        
        print_success("Email connection test passed!")
        print_info("You can send emails to absentees successfully")
        return True
    except Exception as e:
        print_error(f"Email connection test failed: {e}")
        print_warning("Please check your email credentials")
        return False

def verify_dependencies():
    """Verify all required packages are installed"""
    print_header("VERIFYING DEPENDENCIES")
    
    required_packages = {
        'streamlit': 'Streamlit (web framework)',
        'pillow': 'Pillow (image processing)',
        'cv2': 'OpenCV (computer vision)',
        'pandas': 'Pandas (data analysis)',
        'numpy': 'NumPy (numerical computing)',
        'fpdf': 'FPDF (PDF generation)',
        'pytesseract': 'Pytesseract (OCR)',
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print_success(f"Found {name}")
        except ImportError:
            print_error(f"Missing {name}")
            missing.append(package)
    
    if missing:
        print_warning(f"\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    else:
        print_success("All dependencies installed!")
        return True

def create_sample_files():
    """Create sample files for testing"""
    print_header("CREATING SAMPLE FILES")
    
    # Create notes directory if not exists
    os.makedirs("notes", exist_ok=True)
    print_success("Notes directory ready")
    
    # Create .env template
    env_template = """# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password_here
EMAIL_DOMAIN=@company.com

# System paths
ATTENDANCE_DIR=../Face_recognition_based_attendance_system-master/Attendance
STUDENT_DETAILS_PATH=../Face_recognition_based_attendance_system-master/StudentDetails/StudentDetails.csv

# Debug mode
DEBUG=False
"""
    
    with open(".env.template", "w") as f:
        f.write(env_template)
    print_success("Created .env.template for environment variables")

def main():
    """Main setup function"""
    print("\n")
    print_header("CLASS GENIUS + FACE RECOGNITION INTEGRATION SETUP")
    print("""
This setup wizard will help you configure the integration between:
- ClassGenius (Admin Notes Management)
- Face Recognition Based Attendance System

The system will automatically send class notes to students marked absent.
    """)
    
    setup_steps = [
        ("Verify Dependencies", verify_dependencies),
        ("Check Face Recognition System", check_face_recognition_system),
        ("Setup Email Configuration", lambda: setup_email_config() and True),
        ("Setup Database", setup_database),
        ("Check Attendance Data", check_attendance_data),
        ("Create Sample Files", create_sample_files),
    ]
    
    results = {}
    
    for step_name, step_func in setup_steps:
        try:
            result = step_func()
            results[step_name] = "✅ PASS" if result else "⚠️ WARNING"
        except Exception as e:
            print_error(f"Step failed: {e}")
            results[step_name] = "❌ FAILED"
    
    # Summary
    print_header("SETUP SUMMARY")
    for step, status in results.items():
        print(f"{status} - {step}")
    
    # Test email if config was successful
    if results.get("Setup Email Configuration") == "✅ PASS":
        should_test = input("\n\nTest email connection? (y/n): ").strip().lower() == 'y'
        if should_test:
            from config import EMAIL_ADDRESS, EMAIL_APP_PASSWORD
            test_email_connection(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
    
    print_header("SETUP COMPLETE")
    print("""
Next steps:
1. Edit config.py with your email settings
2. Ensure face recognition system has students registered
3. Run attendance at least once with face recognition system
4. Start ClassGenius with: streamlit run app.py
5. Go to Attendance Integration tab to send notes to absentees

For more details, see: INTEGRATION_GUIDE.md
    """)

if __name__ == "__main__":
    # Change to class_Genius directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(script_dir) != "class_Genius":
        class_genius_path = os.path.join(script_dir, "class_Genius")
        if os.path.exists(class_genius_path):
            os.chdir(class_genius_path)
    
    main()
