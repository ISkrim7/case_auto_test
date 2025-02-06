import re

from playwright.async_api import Page, expect, PageAssertions

from app.model.ui import UICaseStepsModel, UIResultModel
from play.extract import ExtractManager
from play.methods.page_methods import PageMethods
from play.writer import Writer
from utils import GenerateTools, log
from utils.io_sender import SocketSender


class ExpectMethod:

    @staticmethod
    async def invoke(page: Page,
                     step: UICaseStepsModel,
                     io: SocketSender,
                     em: ExtractManager,
                     case_result: UIResultModel):
        """
       expectMethod = step method
        ("expect.to_have_title",
        "expect.to_have_attribute")
        :param page:
        :param step:
        :param io:
        :param em:
        :param case_result: 存储断言信息
        :return:
        """
        assertInfo = {
            "id": GenerateTools.getTime(3),
            "desc": step.description,
            "type": "UI",
            "stepName": step.name,
            "assertOpt": "==",
            "extraValueType": "-",
            "extraOpt": "-",
            "extraValue": step.method.split(".")[-1],
            "expect": step.value,

        }

        expect.set_options(timeout=1000)
        method = step.method.split(".")[-1]
        expect_value = await em.transform_target(step.value)
        if expect_value and isinstance(expect_value, (int, float)):
            expect_value = str(expect_value)
        assertInfo['expect'] = expect_value
        await io.send(f"断言信息：{assertInfo}")
        try:
            # PageAssertions
            if method == "to_have_title":
                await expect(page).to_have_title(expect_value)
                assertInfo["actual"] = await page.title()
            elif method == "to_have_url":
                await expect(page).to_have_url(expect_value)
                assertInfo["actual"] = page.url
            else:
                # LocatorAssertions
                locator = await PageMethods.get_locator(page, step)
                expect_method = getattr(expect(locator), method)
                await expect_method(expect_value) if step.value else await expect_method()
            assertInfo["result"] = True
        except AssertionError as e:
            assertInfo["result"] = False
            assertInfo["actual"] = await ExpectMethod.get_error_value(e)
            raise e
        finally:
            await Writer.write_assert_info(case_result, [assertInfo])

    @staticmethod
    async def get_error_value(e: AssertionError):
        err = str(e)
        if "Actual value:" in err:
            # 正则表达式匹配 Actual value 和 Call log 之间的内容
            pattern = r"Actual value:\s*(.*?)\s*Call log:"
            match = re.search(pattern, err, re.DOTALL)
            if match:
                actual_value = match.group(1).strip()
                return actual_value
            else:
                return ""
        return ""


