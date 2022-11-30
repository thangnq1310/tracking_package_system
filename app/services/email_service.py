import os
import smtplib


class EmailService:
    def __init__(self):
        self.host = os.getenv('EMAIL_HOST', 'server.smtp.com')
        self.server = smtplib.SMTP(self.host)
        self.sender = "testpython@test.com"
        self.recipient = "bla@test.com"

    def send_email(self):
        body = "Subject: Test email python\n\nBody of your message!"
        self.server.sendmail(self.sender, self.recipient, body)
        self.server.quit()
        print("Email Send")