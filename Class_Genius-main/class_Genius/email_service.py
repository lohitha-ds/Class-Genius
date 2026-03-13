import smtplib
from email.message import EmailMessage
from config import EMAIL_ADDRESS, EMAIL_APP_PASSWORD, EMAIL_DOMAIN

def send_email(roll_numbers, pdf_path):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)

    for roll in roll_numbers:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = roll + EMAIL_DOMAIN
        msg["Subject"] = "Class Genius - Class Notes"
        msg.set_content("Please find attached class notes PDF.")

        with open(pdf_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=pdf_path)

        server.send_message(msg)

    server.quit()