import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote
from data.db import get_connection
import streamlit as st

# CONFIRMATION_BASE_URL = st.secrets.get("base_url", "http://localhost:8501") + "/?confirm_read="  # Update on deploy
CONFIRMATION_BASE_URL = os.getenv("BASE_URL", "http://localhost:8501") + "/?confirm_read="

def send_assignment_emails(sender_email, app_password):
    print("📧 Email sending process started...")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, p.email, p.role, v.store_name, v.visit_date
        FROM people p
        JOIN visit_plan v ON p.id = v.person_id
    """)
    assignments = cursor.fetchall()
    print(f"📦 Assignments fetched: {assignments}")

    for person_id, name, email, role, store, visit_date in assignments:
        token = f"{person_id}-{store}-{visit_date}"
        confirmation_url = CONFIRMATION_BASE_URL + quote(token)

        subject = f"Your Assignment: {store} on {visit_date}"
        body = f"""
        Hi {name},

        You have been assigned to visit **{store}** on **{visit_date}**.

        👉 Please confirm you have read this assignment:
        {confirmation_url}

        Regards,
        SSA Team
        """
        send_email(sender_email, app_password, email, subject, body)

    conn.close()
    print("📤 Finished sending all assignment emails.")


def send_email(sender_email, app_password, to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
