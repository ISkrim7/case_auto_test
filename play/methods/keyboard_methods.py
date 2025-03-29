from playwright.async_api import  Keyboard

from app.model.ui import UICaseStepsModel
from play.starter import UIStarter


class KeyboardMethods:

    @staticmethod
    async def invoke(step: UICaseStepsModel,
                     starter: UIStarter):
        """
        异步调用键盘操作。

        该方法根据传入的步骤信息，调用相应的键盘操作方法。它首先提取步骤中的方法名，
        然后通过反射机制从Keyboard类中获取该方法并调用它。

        参数:
        - page: 当前的页面对象，尚未使用。
        - step: 包含操作信息的UI测试步骤模型，包括方法名和值。
        - io: 用于发送消息的Socket发送器。
        - em: 提取管理器，尚未使用。

        返回:
        返回键盘操作方法的调用结果。如果没有提供值，则直接调用方法。
        """
        # 提取并发送将要使用的键盘方法名
        method = step.method.strip().split(".")[-1]
        await starter.send(f"use keyboard {method}")

        # 通过反射获取Keyboard类中的指定方法
        attr = await getattr(Keyboard, method)

        # 根据是否有值，调用相应的方法并返回结果
        return attr(step.value) if step.value else attr()