import asyncio
import aiomongo
import aioredis
from aiomysql import create_pool


class MySQLConfig(object):
    username = ""
    password = ""
    hostname = ""
    port = 3306
    database = ""
    minsize = 1
    maxsize = 10


class MongoConfig(object):
    mongouri = ""
    database = ""


class RedisConfig(object):
    redisuri = ""


class Client(object):
    def __init__(self, loop=None):
        self.loop = loop
        self.engine = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.engine is not None:
            self.engine.close()
            await self.engine.wait_closed()
        if exc_type is None:
            return True
        else:
            return False
        return True


class MySQLClient(Client):
    def __init__(self, loop):
        super().__init__(loop)

    async def __aenter__(self):
        print(MySQLConfig.username)
        self.engine = await create_pool(
            minsize=MySQLConfig.minsize,
            maxsize=MySQLConfig.maxsize,
            user=MySQLConfig.username,
            password=MySQLConfig.password,
            db=MySQLConfig.database,
            host=MySQLConfig.hostname,
            port=MySQLConfig.port,
            loop=self.loop
        )
        return self.engine


class MongoClient(Client):
    def __init__(self, loop):
        super().__init__(loop)

    async def __aenter__(self):
        self.engine = await aiomongo.create_client(
            MongoConfig.mongouri,
            loop=self.loop
        )
        db = self.engine[MongoConfig.database]
        return db


class RedisClient(Client):
    def __init__(self):
        super().__init__()

    async def __aenter__(self):
        self.engine = await aioredis.create_redis_pool(
            RedisConfig.redisuri
        )
        return self.engine


async def test(sql, loop):
    async with MySQLClient(loop) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                r = await cur.fetchone()
                print(r)


async def test_mongo(loop):
    async with MongoClient(loop) as db:
        async with db.items.find() as cursor:
            async for c in cursor:
                print(c)


async def test_redis():
    async with RedisClient() as db:
        r = await db.get("tb_h5")
        print(r)


if __name__ == "__main__":
    sql = "select * from tb_item where item_id=526898603880;"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_redis())
