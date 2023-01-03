import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime


class EmailService:
    def __init__(self, sender, recipient, data):
        self.sender = sender
        self.recipient = recipient
        self.data = data

    def send_email(self):
        pkg_order = self.data['pkg_order']
        shop_name = self.data['shop']['name']
        message = MIMEMultipart("alternative")
        message["Subject"] = f'Đơn hàng {pkg_order} của bạn đã được giao thành công vào' \
                             f' ngày {str(datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"))}'
        message["From"] = self.sender
        message["To"] = self.recipient
        body = f"""
        Cám ơn bạn đã mua hàng tại {shop_name}! \n 
        Nếu bạn không hài lòng về sản phẩm. Bạn có thể gửi yêu cầu trả hàng trên ứng dụng {shop_name} 
        trong vòng 7 ngày kể từ khi nhận được email này."""

        part1 = MIMEText(body, 'plain', 'utf-8')
        message.attach(part1)
        with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
            server.login("7bb2dfbf44a33b", "653adf7a344ffb")
            server.sendmail(self.sender, self.recipient, message.as_string().encode('ascii'))
        print("Email Send")