from typing import Callable

from playwright.async_api import Locator, Page

from app.model.ui import UICaseStepsModel

from utils import MyLoguru

log = MyLoguru().get_logger()


class PageMethods:
    """
    PlayWright API
    """

    @staticmethod
    async def execute_locator_method(locator_func: Callable, value: str = None):
        """
        locator().fun(） 执行
        :param locator_func:
        :param value:
        :return:
        """
        return await locator_func(value) if value else await locator_func()

    @staticmethod
    async def play(page: Page,
                   step: UICaseStepsModel):
        """
        页面元素操作
        区分操作方式是否要输入值
        :param page: Page
        :param step: UICaseStepsModel
        :return:
        """
        try:
            locator = await PageMethods.get_locator(page, step)
            # 找到元素方法
            element_method = getattr(locator, step.method)
            # 执行方法
            return await PageMethods.execute_locator_method(element_method, step.value)
        except Exception as e:
            raise e

    @staticmethod
    async def new_page(page: Page, step: UICaseStepsModel):
        """
        actions On New Page
        :param page:
        :param step:
        :return:
        """
        try:
            async with page.expect_popup() as p:
                locator = await PageMethods.get_locator(page, step)
                # 找到元素方法
                element_method = getattr(locator, step.method)
                # 执行方法
                await PageMethods.execute_locator_method(element_method, step.value)
            return await p.value
        except Exception as e:
            log.error(e)
            raise e

    @staticmethod
    async def get_locator(page: Page, step: UICaseStepsModel) -> Locator:
        """
        获取 page locator
        区分是否在iframe上
        并滚动到对应元素
        :param page: Page
        :param step: 步骤
        :return: Locator
        """

        try:
            if step.iframe_name:
                element_locator = page.frame_locator(step.iframe_name).locator(step.locator)
            else:
                element_locator = page.locator(step.locator)

            await PageMethods.to_scroll(element_locator)
            return element_locator
        except Exception as e:
            raise e

    @staticmethod
    async def to_scroll(locator: Locator):
        try:
            await locator.scroll_into_view_if_needed()
        except Exception as e:
            pass
