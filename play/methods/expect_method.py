from playwright.async_api import Page, expect, PageAssertions

from app.model.ui import UICaseStepsModel
from play.extract import ExtractManager
from play.methods.page_methods import PageMethods
from utils.io_sender import SocketSender


class ExpectMethod:

    @staticmethod
    async def invoke(page: Page, step: UICaseStepsModel, io: SocketSender, em: ExtractManager):
        """
       expectMethod = step method
        ("expect.to_have_title",
        "expect.to_have_attribute")
        :param page:
        :param step:
        :param io:
        :param em:
        :return:
        """
        expect.set_options(timeout=1000)
        method = step.method.split(".")[-1]
        # PageAssertions
        if method in PageAssertions.__dict__:
            await getattr(expect(page), method)(step.value)

        else:
            # LocatorAssertions
            locator = await PageMethods.get_locator(page, step)
            expect_method = getattr(expect(locator), method)
            expect_value = await em.transform_target(step.value)
            if expect_value:
                await io.send(f">>expect_value: {expect_value}")
            if isinstance(expect_value, (int, float)):
                expect_value = str(expect_value)
            await expect_method(expect_value) if step.value else await expect_method()
