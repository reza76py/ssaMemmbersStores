# core/mailer.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔒 Replace with your Gmail and App Password
GMAIL_USER = "reza761co@gmail.com"
GMAIL_PASS = "lrkf cvlv uyjo xbct"  # Not your main Gmail password!

def send_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {to_address}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_address}: {e}")
        return False
