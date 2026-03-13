Smart Classroom – Class Genius

Overview

Class Genius is a smart classroom management system that integrates face recognition, OCR, attendance tracking, and automated notifications. The system allows automatic student attendance using facial recognition and provides additional features like PDF generation, email notifications for absentee students, and document text extraction.

This project demonstrates the integration of computer vision, automation, and a web-based interface to improve classroom management and reduce manual work.

---

Features

## 1. Face Recognition Attendance

* Detects and recognizes student faces using a webcam.
* Automatically marks attendance when a student is identified.
* Stores trained face data for recognition.

## 2. Student Registration

* Register students with ID and name.
* Capture multiple face images during registration for training.

## 3. Attendance Management

* Automatic attendance recording.
* Attendance stored and managed in the system.

## 4. Absentee Notification

* Automatically detects absent students.
* Sends email notifications to inform about absentee status.

## 5. OCR Document Processing

* Extracts text from images or PDF documents.
* Useful for converting lecture notes into digital text.

## 6. PDF Report Generation

* Generates reports of attendance or processed data.
* Allows downloading reports in PDF format.

## 7. Web-Based Interface

* Interactive interface for managing features like attendance, OCR, and notifications.

---

# Technologies Used

Python
Streamlit
OpenCV
NumPy
Pillow
Tesseract OCR
FPDF
SMTP
Pandas
Requests
BeautifulSoup
SQLite

---

# Project Structure

```
ClassGenius/
│
├── app.py
├── attendance_ui.py
├── face_recognition_ui.py
├── database.py
├── email_service.py
├── absentee_notification.py
├── attendance_integration.py
├── ocr_pdf.py
├── web_scrape.py
├── config.py
│
├── StudentDetails/
│   └── StudentDetails.csv
│
├── TrainingImageLabel/
│   └── Trainner.yml
│
├── notes/
│   ├── lecture1.pdf
│   ├── maths.pdf
│
└── classgenius.db
```

---

# Installation

### 1. Clone the Repository

```
git clone <repository-url>
cd ClassGenius
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Install OCR Engine

Install Tesseract OCR and configure the path in the system.

---

# Running the Application

Run the Streamlit application:

```
streamlit run app.py
```

The application will open in the browser where you can access:

* Face recognition attendance
* OCR text extraction
* Email notification system
* Attendance management

---

# Future Improvements

* Use a more advanced deep learning face recognition model.
* Replace CSV-based student storage with a scalable database.
* Improve UI design and add authentication.
* Deploy the application as a cloud-based service.

---
