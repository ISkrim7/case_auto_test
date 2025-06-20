from app.model.base import User
from enums import StarterEnum
from utils import MyLoguru, GenerateTools
from utils.io_sender import SocketSender

log = MyLoguru().get_logger()

Event = "ui_message"


class UIStarter(SocketSender):
    _event = "ui_message"
    _ns = "/ui_namespace"
    def __init__(self, user: User | StarterEnum):
        self.logs = []
        super().__init__(event=Event, user=user)

    async def send(self, msg: str):
        try:
            # 格式化消息，添加时间戳。
            msg = f"{GenerateTools.getTime(1)} 🚀 🚀  {msg}"

            # 记录格式化后的消息。
            log.info(msg)

            # 将消息添加到日志列表中。
            self.logs.append(msg + "\n")

            # 准备发送的数据。
            data = {"code": 0, 'data': msg}

            return await super().send(msg)
        except Exception as e:
            # 记录发送过程中出现的错误。
            log.error(e)


    async def clear_logs(self):
        self.logs = []

