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
        async with async_playwright() as playwright:
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
#

async def main():
    try:
        # 获取 BrowserContext 实例
        browser_context = await get_browser_context()
        log.info("BrowserContext instance obtained")

        # 创建一个新的页面
        page = await browser_context.get_page()
        log.info("New page created")

        # 导航到一个示例网站
        await page.goto("https://www.baidu.com")

        # 获取页面标题
        title = await page.title()
        log.info(f"Page title: {title}")

        # 关闭页面
        await BrowserContextSingleton.close_page(page)
        log.info("Page closed")

        # 关闭 BrowserContext
        await browser_context.shutdown()
        log.info("BrowserContext shutdown")

    except Exception as e:
        log.error(f"An error occurred: {e}")

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())

