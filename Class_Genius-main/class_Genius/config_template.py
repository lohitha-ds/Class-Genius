"""
Configuration File for ClassGenius + Face Recognition Integration
Configure email settings and system parameters here
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

# ============ EMAIL CONFIGURATION ============
# Gmail SMTP settings for sending notes to absentees

# Your Gmail address
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "your_email@gmail.com")

# Gmail App Password (NOT your regular password)
# Generate from: https://myaccount.google.com/apppasswords
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "your_app_password_here")

# Email domain suffix for student emails
# If students use corporate domain: "@company.com"
# If using Gmail: "@gmail.com"
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN", "@company.com")

# ============ ATTENDANCE SYSTEM CONFIGURATION ============

# Path to Face Recognition attendance directory
ATTENDANCE_DIR = os.getenv(
    "ATTENDANCE_DIR",
    "../Face_recognition_based_attendance_system-master/Attendance"
)

# Path to StudentDetails.csv
STUDENT_DETAILS_PATH = os.getenv(
    "STUDENT_DETAILS_PATH",
    "../Face_recognition_based_attendance_system-master/StudentDetails/StudentDetails.csv"
)

# ============ STREAMLIT CONFIGURATION ============

# Database file location
DATABASE_PATH = os.getenv("DATABASE_PATH", "classgenius.db")

# Notes directory
NOTES_DIR = os.getenv("NOTES_DIR", "notes")

# ============ EMAIL TEMPLATE SETTINGS ============

# Email subject template
EMAIL_SUBJECT_TEMPLATE = "Class Genius - Class Notes ({date})"

# Email body template
EMAIL_BODY_TEMPLATE = """
Dear {student_name},

You were marked absent on {date}. Please find attached the class notes for that day.

{reason_section}

Please reach out to your instructor if you have any questions.

Best regards,
Class Genius Admin
"""

# Email signature
EMAIL_SIGNATURE = "ClassGenius - Smart Classroom Management System"

# ============ NOTIFICATION SETTINGS ============

# Send notifications automatically on note upload (True/False)
AUTO_SEND_ON_UPLOAD = False

# Delay before sending (in seconds)
SEND_DELAY = 0

# Maximum retries for failed email sends
MAX_EMAIL_RETRIES = 3

# ============ LOGGING CONFIGURATION ============

# Enable detailed logging
ENABLE_LOGGING = True

# Log file location
LOG_FILE = os.getenv("LOG_FILE", "classgenius.log")

# ============ SYSTEM PREFERENCES ============

# Default attendance date format (JAVA SimpleDateFormat)
DATE_FORMAT = "%d-%m-%Y"

# Time format for logs
TIME_FORMAT = "%d-%m-%Y %H:%M:%S"

# Enable admin approval before sending to absentees
REQUIRE_APPROVAL = True

# Automatically create new tables if missing
AUTO_CREATE_TABLES = True

# ============ DEBUG MODE ============

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

if DEBUG:
    print("⚠️ DEBUG MODE ENABLED - Check sensitive information before committing")
