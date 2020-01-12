import asyncio
import aiohttp
from lxml import etree
from user_agent import generate_user_agent


OS_TYPE = {
    True: "android",
    False: ("mac", "win")
}


async def request(method, url=None, is_mobile=False, **kwargs):
    kwargs.setdefault("timeout", aiohttp.ClientTimeout(10))
    if "headers" in kwargs:
        kwargs["headers"].setdefault("user-agent", generate_user_agent(os=OS_TYPE[is_mobile]))
    else:
        kwargs["headers"] = {
            "user-agent": generate_user_agent(os=OS_TYPE[is_mobile])
        }
    resp = None
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, **kwargs) as r:
            resp = r
            content_type = r.content_type
            if "text" in content_type or "html" in content_type:
                content = await r.text(encoding=r.charset)
                resp.xpath = etree.HTML(content).xpath
            elif "json" in content_type:
                resp = await r.json(encoding=r.charset)
            else:
                resp = await r.read()
    return resp


def main():
    method = "GET"
    url = "http://www.baidu.com"
    # url = "http://www.google.com"
    coro = request(method, url=url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coro)
    loop.close()


if __name__ == "__main__":
    main()
