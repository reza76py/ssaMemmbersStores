# # notifications/email_assignment.py

# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from data.db import get_connection

# SENDER_EMAIL = "reza761co@gmail.com"
# APP_PASSWORD = "lrkf cvlv uyjo xbct"  # Replace this during testing

# def send_assignment_emails():
#     conn = get_connection()
#     cursor = conn.cursor()

#     # Example SQL: adjust based on your visit plan table
#     cursor.execute("""
#         SELECT p.name, p.email, p.role, v.store_name, v.visit_date
#         FROM people p
#         JOIN visit_plan v ON p.id = v.person_id
#     """)
#     assignments = cursor.fetchall()

#     for name, email, role, store, visit_date in assignments:
#         subject = f"Your Assignment: {store} on {visit_date}"
#         body = f"""
#         Hi {name},

#         You have been assigned to visit **{store}** on **{visit_date}**.

#         Please confirm you have read this message by replying or clicking the checkbox (to be implemented).

#         Regards,
#         SSA Team
#         """
#         send_email(email, subject, body)

#     conn.close()

# def send_email(to_email, subject, body):
#     msg = MIMEMultipart()
#     msg["From"] = SENDER_EMAIL
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.attach(MIMEText(body, "plain"))

#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
#             smtp.starttls()
#             smtp.login(SENDER_EMAIL, APP_PASSWORD)
#             smtp.send_message(msg)
#             print(f"✅ Email sent to {to_email}")
#     except Exception as e:
#         print(f"❌ Failed to send email to {to_email}: {e}")









# notifications/email_assignment.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from data.db import get_connection
from urllib.parse import quote  # For generating confirmation URLs

SENDER_EMAIL = "reza761co@gmail.com"
APP_PASSWORD = "lrkf cvlv uyjo xbct"  # Replace this during testing

CONFIRMATION_BASE_URL = "http://localhost:8501/?confirm_read="  # Change if deploying

def send_assignment_emails():
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
        send_email(email, subject, body)

    conn.close()
    print("📤 Finished sending all assignment emails.")

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
