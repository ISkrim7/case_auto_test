from json import JSONDecodeError

from playwright.async_api import Page

from app.model.ui import UICaseStepsModel
from play.extract import ExtractManager
from utils import MyJsonPath, log
from utils.io_sender import SocketSender


class APIOn:

    @staticmethod
    async def invoke(page: Page,
                     step: UICaseStepsModel,
                     io: SocketSender,
                     em: ExtractManager,**kwargs):
        """
        interface 单次执行
        :param page:
        :param step:
        :param io:SocketSender
        :param em:ExtractManager
        :return:
        """
        method = step.method.strip().split(".")[-1]
        try:
            jpStr, variableName = step.value.strip().split(";")
        except ValueError:
            raise ValueError(f"输入值 {step.value}格式错误;请检查")

        async def on_response(response):
            if step.api_url in response.url:
                await io.send("监听成功✅")
                await io.send(f"status_code =  {response.status}")
                await io.send(f"url =  {response.url}")
                try:
                    _body = await response.json()
                    jp = MyJsonPath(_body, jpStr)
                    value = await jp.value()
                    await io.send(f"获取变量 >> ✅ {variableName} = {value}")
                    await em.add_var(variableName, value)
                    log.debug(em.variables)
                except JSONDecodeError as e:
                    await io.send(f"解析响应失败 ❌ >> {str(e)}")
                    await em.add_var(variableName, None)
                    return
                log.debug(_body)

        async def on_request(request):
            pass

        match method:
            case "request":
                page.on("request", on_request)
            case "response":
                await io.send(f"添加接口响应监听 >> {step.api_url}")
                page.on("response", on_response)
