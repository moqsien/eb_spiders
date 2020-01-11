import asyncio
import platform
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
        else:
            self.formatter = formatter
        self.terminator = "\r\n"

    async def handle(self, record):
        rv = self.filter(record)
        if rv:
            await self.emit(record)
        return rv

    async def emit(self, record):
        try:
            title, content = self.formatter.format(record)
            await send_mail(title, content)
        except Exception as exc:
            await self.handle_error(record, exc)

    async def close(self):
        return


class EmailFormatter(object):
    def format(self, record):
        module = record.module
        path = record.pathname
        filename = record.filename
        lineno = record.lineno
        funcname = record.funcName
        levelname = record.levelname
        msg = record.msg

        title = "测试[{}]-[{}] in [{}{}]".format(levelname, funcname, module, filename)
        content = """
        <b>HOST_NAME:</b> <br /> <font size="2" color="red">{}</font>
        <br />
        <br />
        <b>LINE_NO:</b> <br /> <font size="2" color="red">{}[line:{}]</font>
        <br />
        <br />
        <b>ERRORS:</b> <br /> <font size="2" color="blue">{}</font>
        """.format(platform.uname()[1], path, lineno, msg)
        return title, content


class MyLogger(object):
    def __init__(self, filename=None, logger_name="file-logger"):
        if filename is None:
            self.handler = AsyncEmailHandler(formatter=EmailFormatter())
        else:
            formatter = Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
            self.handler = AsyncTimedRotatingFileHandler(filename=filename)
            self.handler.formatter = formatter
        self.name = logger_name

    def __call__(self):
        logger = Logger.with_default_handlers(name=self.name)
        logger.add_handler(self.handler)
        return logger


async def main():
    logger = MyLogger(logger_name="email-logger")()
    await logger.info("debug")
    await logger.shutdown()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
