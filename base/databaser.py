import asyncio
import sqlalchemy as sa
import aiomongo
import aioredis
from aiomysql.sa import create_engine


class MySQLConfig(object):
    username = ""
    password = ""
    hostname = ""
    database = ""


class MongoConfig(object):
    mongouri = ""
    database = ""


class RedisConfig(object):
    redisuri = ""


class Client(object):
    def __init__(self, loop):
        self.loop = loop
        self.engine = None


class MySQLClient(Client):
    def __init__(self, loop):
        super().__init__(loop)

    async def __aenter__(self):
        self.engine = await create_engine(
            user=MySQLConfig.username,
            password=MySQLConfig.password,
            db=MySQLConfig.database,
            host=MySQLConfig.hostname,
            loop=self.loop
        )
        return self.engine

    async def __aexit__(self, exc_type, exc, tb):
        if self.engine is not None:
            self.engine.close()
            await self.engine.wait_closed()
        return True


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

    async def __aexit__(self, exc_type, exc, tb):
        if self.engine is not None:
            self.engine.close()
            await self.engine.wait_closed()
        return True


class RedisClient(Client):
    def __init__(self, loop):
        super().__init__(loop)

    async def __aenter__(self):
        self.engine = await aioredis.create_connection(
            RedisConfig.redisuri
        )
        return self.engine

    async def __aexit__(self, exc_type, exc, tb):
        if self.engine is not None:
            self.engine.close()
            await self.engine.wait_closed()
        return True


async def test(sql, loop):
    async with MySQLClient(loop) as engine:
        async with engine.acquire() as conn:
            r = await conn.execute(sql)
            r = await r.fetchall()
            print(r)


async def test_mongo(loop):
    async with MongoClient(loop) as db:
        async with db.items.find() as cursor:
            async for c in cursor:
                print(c)


async def test_redis(loop):
    async with RedisClient(loop) as db:
        db.get("cookie")


if __name__ == "__main__":
    sql = "select * from tb_item where item_id=526898603880;"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_redis(loop))
