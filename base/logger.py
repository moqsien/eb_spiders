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
            print(msg)
            await send_mail("开发邮件3", str(msg + "_你好，测试"))
        except Exception as exc:
            await self.handle_error(record, exc)

    async def close(self):
        return


handler = AsyncTimedRotatingFileHandler(filename="test.log")
handler_ = AsyncEmailHandler()


class MyLogger(object):
    handlers = dict(
        AsyncFile=handler,
        AsyncEmail=handler_
    )
    def __init__(self, handler="AsyncFile"):
        self.handler = self.handlers[handler]
        
    def __call__(self, name="eb-logger"):
        logger = Logger.with_default_handlers(name=name)
        logger.add_handler(self.handler)
        return logger


async def main():
    logger = MyLogger("AsyncEmail")()
    await logger.debug("debug")
    await logger.shutdown()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
