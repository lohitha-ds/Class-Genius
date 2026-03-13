"""
Absentee Notification Service
Automatically sends class notes to students marked absent by the face recognition system
"""

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path
from email_service import send_email
from attendance_integration import AttendanceManager


class AbsenteeNotificationService:
    """Sends notes to absentees based on face recognition attendance"""
    
    def __init__(self, config=None):
        self.attendance_manager = AttendanceManager()
        self.config = config or {}
    
    def send_notes_to_absentees_for_date(self, note_pdf_path, attendance_date=None, reason=""):
        """
        Send notes to all absentees for a specific date
        
        Args:
            note_pdf_path: Path to the PDF file to send
            attendance_date: Date in format DD-MM-YYYY (defaults to today)
            reason: Reason for sending notes (e.g., "Missed class on 07-01-2026")
        
        Returns:
            dict: Summary of sending operation with success/failure count
        """
        
        if not os.path.exists(note_pdf_path):
            return {
                'success': False,
                'message': f'PDF file not found: {note_pdf_path}',
                'sent_count': 0,
                'failed_count': 0
            }
        
        if attendance_date is None:
            attendance_date = datetime.now().strftime('%d-%m-%Y')
        
        # Get absentees for the specified date
        absentees = self.attendance_manager.get_absentees_for_date(attendance_date)
        
        if not absentees:
            return {
                'success': True,
                'message': 'No absentees found for this date',
                'sent_count': 0,
                'failed_count': 0
            }
        
        # Prepare email list
        email_list = []
        for student_id, details in absentees.items():
            if details.get('email'):
                email_list.append({
                    'student_id': student_id,
                    'email': details['email'],
                    'name': details.get('name', 'Student')
                })
        
        if not email_list:
            return {
                'success': True,
                'message': 'No valid email addresses found for absentees',
                'sent_count': 0,
                'failed_count': len(absentees)
            }
        
        # Send emails to absentees
        sent_count = 0
        failed_count = 0
        
        for recipient in email_list:
            try:
                self._send_email_to_student(
                    recipient['email'],
                    recipient['name'],
                    note_pdf_path,
                    attendance_date,
                    reason
                )
                
                # Log in database
                self._log_note_sent(
                    note_id=self._get_note_id(note_pdf_path),
                    student_id=recipient['student_id'],
                    attendance_date=attendance_date,
                    status='sent'
                )
                
                sent_count += 1
                
            except Exception as e:
                print(f"Failed to send email to {recipient['email']}: {e}")
                
                # Log failure
                self._log_note_sent(
                    note_id=self._get_note_id(note_pdf_path),
                    student_id=recipient['student_id'],
                    attendance_date=attendance_date,
                    status='failed'
                )
                
                failed_count += 1
        
        return {
            'success': True,
            'message': f'Sent to {sent_count} absentees, {failed_count} failed',
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_absentees': len(absentees),
            'absentee_emails_sent': sent_count
        }
    
    def _send_email_to_student(self, email, student_name, pdf_path, date, reason=""):
        """Send email with PDF attachment to a student"""
        from config import EMAIL_ADDRESS, EMAIL_APP_PASSWORD
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = f"Class Genius - Class Notes ({date})"
        
        body = f"""
        Dear {student_name},
        
        You were marked absent on {date}. Please find attached the class notes for that day.
        
        {f"Reason: {reason}" if reason else ""}
        
        Please reach out to your instructor if you have any questions.
        
        Best regards,
        Class Genius Admin
        """
        
        msg.set_content(body)
        
        # Attach PDF
        with open(pdf_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(pdf_path)
            )
        
        server.send_message(msg)
        server.quit()
    
    def _get_note_id(self, pdf_filename):
        """Get note ID from database for a given filename"""
        try:
            # Extract just filename if full path is provided
            filename = os.path.basename(pdf_filename)
            c.execute("SELECT id FROM notes WHERE filename = ?", (filename,))
            result = c.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting note ID: {e}")
            return None
    
    def _log_note_sent(self, note_id, student_id, attendance_date, status):
        """Log note sent to absentee in database"""
        try:
            sent_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            c.execute(
                """
                INSERT INTO notes_sent_to_absentees 
                (note_id, student_id, attendance_date, sent_date, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (note_id, student_id, attendance_date, sent_date, status)
            )
            conn.commit()
        except Exception as e:
            print(f"Error logging note sent: {e}")
    
    def get_notification_history(self, student_id=None, note_id=None, days=30):
        """Get history of notes sent to absentees"""
        try:
            if student_id:
                c.execute(
                    """
                    SELECT * FROM notes_sent_to_absentees 
                    WHERE student_id = ? 
                    ORDER BY sent_date DESC
                    """,
                    (student_id,)
                )
            elif note_id:
                c.execute(
                    """
                    SELECT * FROM notes_sent_to_absentees 
                    WHERE note_id = ? 
                    ORDER BY sent_date DESC
                    """,
                    (note_id,)
                )
            else:
                c.execute(
                    """
                    SELECT * FROM notes_sent_to_absentees 
                    ORDER BY sent_date DESC
                    """
                )
            
            return c.fetchall()
        except Exception as e:
            print(f"Error fetching notification history: {e}")
            return []
    
    def update_student_cache(self):
        """Update student cache from StudentDetails.csv"""
        try:
            from attendance_integration import AttendanceManager
            am = AttendanceManager()
            students = am.get_all_students()
            
            for student_id, details in students.items():
                c.execute(
                    """
                    INSERT OR REPLACE INTO student_cache 
                    (student_id, name, email, serial_no, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        details.get('name', ''),
                        details.get('email', ''),
                        details.get('serial', ''),
                        datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                    )
                )
            
            conn.commit()
            return {'success': True, 'message': 'Student cache updated'}
        except Exception as e:
            return {'success': False, 'message': f'Error updating cache: {e}'}
