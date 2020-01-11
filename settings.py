import asyncio
from base import EmailConfig, send_mail



EmailConfig.from_ = "moqsien@163.com"
EmailConfig.to_ = "moqsien@foxmail.com"
EmailConfig.hostname_ = "smtp.163.com"
EmailConfig.username_ = "moqsien"
EmailConfig.password_ = "spider2019"


loop = asyncio.get_event_loop()
loop.run_until_complete(send_mail("这是测试邮件", "内容为空，什么都可以"))
