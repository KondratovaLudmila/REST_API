import redis.asyncio as redis

from src.conf.config import settings

async def get_cache():
    return await redis.Redis(host=settings.redis.host, 
                             port=settings.redis.port, 
                             db=0,)