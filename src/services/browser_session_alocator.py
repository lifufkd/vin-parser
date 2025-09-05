import asyncio
from loguru import logger

from src.core.exceptions import SolidBanError
from src.core.proxy_manager import ProxyManager
from src.core.utils import format_proxy
from src.core.config import browser_settings


class BrowserSessionLocator:
    def __init__(self, browser_session):
        self.browser_session = browser_session

    async def allocate(self, func, *args, **kwargs):
        extracted_proxy = False
        browser_tab = None
        proxy = None
        proxy_manager = ProxyManager()

        selected_proxy = await proxy_manager.get_next_proxy() if browser_settings.USE_PROXY_BROWSER else None
        client_kwargs = {
            "user_agent": browser_settings.USER_AGENT
        }

        if selected_proxy:
            proxy = format_proxy(selected_proxy)
            client_kwargs["proxy"] = proxy

        for attempt in range(browser_settings.FETCH_RETRIES_COUNT):
            if selected_proxy:
                logger.debug(f"Try {attempt + 1}/{browser_settings.FETCH_RETRIES_COUNT}. Run with proxy: {proxy}")
            else:
                logger.debug(f"Try {attempt + 1}/{browser_settings.FETCH_RETRIES_COUNT}")

            try:
                context = await self.browser_session.new_context(
                    **client_kwargs
                )
                browser_tab = await context.new_page()

                result = await func(*args, browser_tab=browser_tab, **kwargs)
                if extracted_proxy and selected_proxy:
                    await proxy_manager.return_proxy(selected_proxy)

                return result
            except SolidBanError:
                if selected_proxy:
                    logger.warning(f"Request limit is reached for proxy: {selected_proxy}, existing...")
                else:
                    logger.warning(f"Request limit is reached, existing...")

                if not extracted_proxy and selected_proxy:
                    await proxy_manager.remove_proxy(selected_proxy)
                    extracted_proxy = True

                break
            except Exception:
                if not extracted_proxy and selected_proxy:
                    await proxy_manager.remove_proxy(selected_proxy)
                    extracted_proxy = True

                backoff = browser_settings.FETCH_RETRY_DELAY * (2 ** attempt)
                if selected_proxy:
                    logger.warning(f"Proxy {selected_proxy} has been temporarily banned, retry after {backoff} seconds")
                else:
                    logger.warning(f"Request error, retry after {backoff} seconds")

                await asyncio.sleep(backoff)
            finally:
                if browser_tab:
                    await browser_tab.close()

        if selected_proxy:
            logger.error(f"Giving up, proxy {selected_proxy} has been banned")
        else:
            logger.error(f"Giving up, to many requests")

        return None
