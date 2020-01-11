import logging
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailConfig(object):
    from_ = ""
    to_ = ""
    hostname_ = ""
    username_ = ""
    password_ = ""
    

async def send_mail(func_name, content):
    title = "[{}] has exceptions!".format(func_name)
    content = "<html><body>" + content + "</html></body>"
    msg = MIMEText(content, "html", "utf-8")
    msg["From"] = EmailConfig.from_
    msg["To"] = EmailConfig.to_
    msg["Subject"] = title
    try:
        async with aiosmtplib.SMTP(hostname=EmailConfig.hostname_, port=465, use_tls=True) as smtp:
            await smtp.login(EmailConfig.username_, EmailConfig.password_)
            await smtp.send_message(msg)
    except aiosmtplib.SMTPException as e:
        logging.error('sendemail:%s' % e)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_mail("测试邮件", "debug_你好"))
