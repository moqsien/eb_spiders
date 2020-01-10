import asyncio
from functools import wraps


class ExceptionHandler(object):
    def __init__(self, att):
        self.att = att

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_instance, tracebacks):
        if exc_type is None:
            return True
        if issubclass(exc_type, KeyError):
            return True
        elif issubclass(exc_type, ValueError):
            return True
        elif issubclass(exc_type, IndexError):
            return True
        elif issubclass(exc_type, AttributeError):
            return True
        elif issubclass(exc_type, TypeError):
            return True
        return True


def retry(retry_times=6, exc_handler=ExceptionHandler):
    def outter(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            att = 0
            while att <= retry_times:
                async with exc_handler(att):
                    result = await func(*args, **kwargs)
                    return result
                att += 1
            return
        return inner
    return outter
