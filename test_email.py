# test_email.py

from core.mailer import send_email

# Replace with your email for testing
to = "reza76mgp@gmail.com"

subject = "Test Email from SSA App"
body = """
Hi there,

This is a test email from the SSA Assignment system.
If you received this, the mailer works correctly.

✅ Thanks!
"""

send_email(to, subject, body)
