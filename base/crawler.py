import abc
import asyncio
from exceptioner import retry
from exceptioner import ExceptionHandler
from downloader import request


class BaseMeta(type):
    def __new__(cls, name, bases, attrs):
        parse_retry_times = attrs.get("parse_retry_times", 1)
        parse_exc_handler = attrs.get("parse_exc_handler", ExceptionHandler)
        crawl_exc_handler = attrs.get("crawl_exc_handler", ExceptionHandler)
        if "retry" in attrs and "parse_item" in attrs:
            attrs["parse_item"] = attrs["retry"](
                retry_times=parse_retry_times,
                exc_handler=parse_exc_handler
            )(
                attrs["parse_item"]
            )
        if "retry" in attrs and "crawl" in attrs:
            attrs["crawl"] = attrs["retry"](
                retry_times=1,
                exc_handler=crawl_exc_handler
            )(
                attrs["crawl"]
            )
        return super(BaseMeta, cls).__new__(cls, name, bases, attrs)


class Base(metaclass=BaseMeta):
    retry = retry
    parse_retry_times = 3
    parse_exc_handler = ExceptionHandler
    crawl_exc_handler = ExceptionHandler

    def __init__(self):
        self.url = None
        self.page_cursor = 1
        self.total_page = 100
        self.url_pattern = None
        self._module = self.__class__.__module__
        self._class = self.__class__.__name__

    async def get_response(self, url):
        content, _ = await request("GET", url)
        return content

    @abc.abstractmethod
    def get_total_page_num(self, response):
        """
        获取总页码数
        Arguments:
            response {[str]} -- [页面响应字符串或json]
        """
        self.total_page = 100

    @abc.abstractmethod
    def get_url(self, page_num):
        """
        根据页码获取要抓取的url
        Arguments:
            page_num {[int]} -- [页码数]
        """
        assert self.url_pattern
        return self.url_pattern.format(page_num)

    @abc.abstractmethod
    async def parse_item(self, data):
        """
        解析每一条数据
        Arguments:
            data {[dict]} -- [商品数据]
        """
        pass

    @abc.abstractmethod
    async def parse_page(self, response):
        """
        解析每一页数据
        Arguments:
            response {[str]} -- [页面响应字符串或者json]
        """
        pass

    def gen_req_task(self, page_num):
        url = self.get_url(page_num)
        task = asyncio.ensure_future(self.get_response(url))
        return task

    def gen_parse_task(self, result):
        return asyncio.ensure_future(self.parse_page(result))

    async def crawl(self, url=None, url_pattern=None, max_reqs=5):
        self.url = url
        self.url_pattern = url_pattern
        resp = await self.get_response(url)
        self.get_total_page_num(resp)
        while self.page_cursor <= self.total_page:
            tasks = [
                self.gen_req_task(page) for page in range(self.page_cursor,
                                                          self.page_cursor + max_reqs)
            ]
            results = await asyncio.gather(*tasks)
            tasks_ = [
                self.gen_parse_task(result) for result in results
            ]
            await asyncio.gather(*tasks_)
            self.page_cursor += max_reqs
