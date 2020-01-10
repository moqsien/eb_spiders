import abc
import asyncio
from downloader import request


class CrawlerBase(object):
    def __init__(self, start_url, loop):
        # 事件循环
        self.loop = loop
        # 要抓取的url
        self.url = None
        # 记录上次请求url
        self.last_page_url = None
        # 翻页用的url模板
        self.pattern_url = None
        # 翻页记录
        self.page = 1
        # 记录抓取总页数
        self.total_page_num = 0
        # 商品id
        self.item_id = None
        # 模块名
        self.module_ = self.__class__.__module__
        # 类名
        self.class_ = self.__class__.__name__

    async def get_response(self, url):
        resp = await request("GET", url)
        return resp

    @abc.abstractmethod
    def get_next_url(self, response):
        pass

    @abc.abstractmethod
    async def parse_item(self, data):
        pass

    @abc.abstractmethod
    async def parse_page(self, response):
        pass

    async def crawl(self, url=None):
        if url is not None:
            self.url = url
        assert self.url is not None, "请求第一页时，self.url不能为None，请在初始化方法中设置url或者在crawl方法调用时设置self.url"
        resp = await self.get_response(self.url)
        self.last_page_url = self.url
        self.spider_name = spider_name
        while True:
            print("========第{}页开始========".format(self.page))
            await self.parse_page(resp)
            print("========第{}页完成========".format(self.page))
            self.page += 1
            next_page_url = self.get_next_url(resp)
            # 如果下一页url为空，重置参数到默认值，修改参数，跳出循环
            if not next_page_url:
                self.pattern_url = None
                self.total_page_num = self.page
                self.page = 1
                break
            resp = await self.get_response(next_page_url)
            # 更新上一页url地址
            self.last_page_url = next_page_url
