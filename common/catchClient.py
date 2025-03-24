import json
from datetime import timedelta
from typing import Any, Union, Optional

from utils import MyLoguru
from .redisClient import RedisClient

log = MyLoguru().get_logger()


class CatchClient(RedisClient):

    async def cache_get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            data = await self.r.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            log.error(f"缓存获取失败 {key}: {str(e)}")
            return None

    async def cache_set(
            self,
            key: str,
            value: Any,
            expire: Union[int, timedelta] = 60
    ) -> bool:
        """设置缓存数据"""
        try:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())

            # serialized = json.dumps(value)
            return await self.r.setex(key, expire, value)
        except Exception as e:
            log.error(f"缓存设置失败 {key}: {str(e)}")
            return False

    async def cache_delete(self, *keys: str) -> int:
        """删除缓存键"""
        try:
            return await self.r.delete(*keys)
        except Exception as e:
            log.error(f"缓存删除失败 {keys}: {str(e)}")
            return 0

    async def cache_delete_namespace(self, namespace: str) -> int:
        """删除指定命名空间的所有键"""
        try:
            keys = await self.r.keys(f"{namespace}:*")
            if keys:
                return await self.r.delete(*keys)
            return 0
        except Exception as e:
            log.error(f"命名空间缓存删除失败 {namespace}: {str(e)}")
            return 0

    async def cache_with_key(
            self,
            key: str,
            func: callable,
            expire: int = 60 * 24,
            *args,
            **kwargs
    ) -> Any:
        """高阶函数：带缓存的执行"""
        # 尝试从缓存获取
        cached = await self.cache_get(key)
        if cached is not None:
            return cached

        # 执行函数获取结果
        result = await func(*args, **kwargs)

        # 设置缓存
        if result is not None:
            await self.cache_set(key, result, expire)

        return result
