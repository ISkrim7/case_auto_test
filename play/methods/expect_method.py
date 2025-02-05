from playwright.async_api import Page, expect, PageAssertions

from app.model.ui import UICaseStepsModel, UIResultModel
from play.extract import ExtractManager
from play.methods.page_methods import PageMethods
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

        }


        expect.set_options(timeout=1000)
        method = step.method.split(".")[-1]
        expect_value = await em.transform_target(step.value)
        if expect_value:
            await io.send(f">>expect_value: {expect_value}")
        if isinstance(expect_value, (int, float)):
            expect_value = str(expect_value)
        try:
            # PageAssertions
            if method in PageAssertions.__dict__:
                await getattr(expect(page), method)(expect_value)
            else:
                # LocatorAssertions
                locator = await PageMethods.get_locator(page, step)
                expect_method = getattr(expect(locator), method)
                await expect_method(expect_value) if step.value else await expect_method()
            assertInfo["result"] = True
            case_result.asserts_info.append(assertInfo)
            log.debug(case_result.asserts_info)
        except Exception as e:
            assertInfo["result"] = False
            assertInfo["actual"] = str(e)

        # [{"id": 1738547896726, "desc": "断言code", "type": "API", "actual": 0, "expect": "0", "result": true, "extraOpt": "jsonpath", "stepName": "test", "assertOpt": "==", "extraValue": "$.code", "extraValueType": "integer"}]
