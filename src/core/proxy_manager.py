from typing import Optional

from src.core.config import generic_settings
from src.core.file_manager import FileManager
from src.core.redis_client import redis_client


class ProxyManager:
    def __init__(self):
        self.proxies_key = 'proxy_manager:proxies'

    async def init_proxies(self):
        await redis_client.delete(self.proxies_key)

        if not generic_settings.PROXIES_FILE_PATH:
            return

        proxy_list = await FileManager().load(file_path=generic_settings.PROXIES_FILE_PATH)
        proxy_list = [p.strip() for p in proxy_list.split('\n') if p.strip()]

        if proxy_list:
            await redis_client.rpush(self.proxies_key, *proxy_list)

    async def get_next_proxy(self) -> Optional[str]:
        proxy = await redis_client.execute_command("RPOPLPUSH", self.proxies_key, self.proxies_key)
        if proxy:
            return proxy.decode() if isinstance(proxy, bytes) else proxy
        return None

    async def remove_proxy(self, proxy_to_remove: str) -> bool:
        removed_count = await redis_client.lrem(self.proxies_key, 0, proxy_to_remove)
        return removed_count > 0

    async def return_proxy(self, proxy: str) -> None:
        proxies = await self.get_all_proxies()
        if proxy not in proxies:
            await redis_client.rpush(self.proxies_key, proxy)

    async def get_all_proxies(self) -> list[str]:
        proxies = await redis_client.lrange(self.proxies_key, 0, -1)
        return [p.decode() if isinstance(p, bytes) else p for p in proxies]
