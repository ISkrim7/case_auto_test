from config import Config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
class EmailClient:


    def send(self,body:str):
        recipient = "xx@163.com"
        # 设置邮件内容
        msg = MIMEMultipart()
        msg['From'] = Config.Email_Sender_Username
        msg['To'] = recipient
        msg['Subject'] = "subject"
        msg.attach(MIMEText(body, 'plain'))

        try:
            # 建立安全连接
            with smtplib.SMTP("smtp.163.com") as server:
                # server.starttls()  # 启用 TLS 加密
                server.set_debuglevel(1)  # 启用调试输出
                server.login(Config.Email_Sender_Username, Config.Email_Sender_Password)  # 登录到邮件服务器
                server.send_message(msg)

            return {"status": "success", "message": "邮件发送成功"}
        except Exception as e:
            print(f"Error: {e}")
