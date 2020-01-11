import asyncio
from aiologger import Logger
from aiologger.handlers.base import Handler
from aiologger.formatters.base import Formatter
from aiologger.handlers.files import AsyncTimedRotatingFileHandler
from messenger import send_mail


class AsyncEmailHandler(Handler):
    def __init__(self, formatter=None, loop=None):
        super().__init__(loop=loop)
        if formatter is None:
            self.formatter = Formatter()
        self.terminator = "\r\n"

    async def handle(self, record):
        rv = self.filter(record)
        if rv:
            await self.emit(record)
        return rv

    async def emit(self, record):
        try:
            msg = self.formatter.format(record) + self.terminator
            await send_mail("开发邮件3", str(msg + "_你好，测试"))
        except Exception as exc:
            await self.handle_error(record, exc)

    async def close(self):
        return


class MyLogger(object):
    def __init__(self, filename=None, logger_name="file-logger"):
        if filename is None:
            self.handler = AsyncEmailHandler()
        else:
            self.handler = AsyncTimedRotatingFileHandler(filename=filename)
        self.name = logger_name

    def __call__(self):
        formatter = Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        self.handler.formatter = formatter
        logger = Logger.with_default_handlers(name=self.name)
        logger.add_handler(self.handler)
        return logger


async def main():
    logger = MyLogger(filename="test1.log")()
    await logger.info("debug")
    await logger.shutdown()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
