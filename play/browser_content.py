# browser_context.py
import asyncio

from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from config import Config
from utils import log


class BrowserContextSingleton:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self, playwright: Playwright, browser: Browser, context: BrowserContext):
        self.playwright = playwright
        self.browser = browser
        self.context = context

    @classmethod
    async def get_instance(cls):
        if not cls._instance:
            async with cls._lock:
                if not cls._instance:
                    cls._instance = await cls._create_context()
        return cls._instance

    @classmethod
    async def _create_context(cls):
        playwright =  await async_playwright().start()
        browser = await playwright.chromium.launch(headless=Config.UI_Headless,
                                                       timeout=Config.UI_Timeout,
                                                       slow_mo=Config.UI_SLOW)
        context = await browser.new_context()
        context.set_default_timeout(Config.UI_Timeout)
        log.info("BrowserContext initialized")
        return cls(playwright, browser, context)

    async def get_page(self) -> Page:
        return await self.context.new_page()

    @staticmethod
    async def close_page(page: Page):
        await page.close()

    async def shutdown(self):
        try:
            await self.context.close()
        except Exception as e:
            log.error(f"Error closing context: {e}")
        try:
            await self.browser.close()
        except Exception as e:
            log.error(f"Error closing browser: {e}")
        try:
            await self.playwright.stop()
        except Exception as e:
            log.error(f"Error stopping playwright: {e}")
        log.info("BrowserContext shutdown")



# 获取 BrowserContext 实例
async def get_browser_context():
    return await BrowserContextSingleton.get_instance()
