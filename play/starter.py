from app.model.base import User
from enums import StarterEnum
from utils import MyLoguru
from utils.io_sender import SocketSender

log = MyLoguru().get_logger()

Event = "ui_message"


class UIStarter(SocketSender):

    def __init__(self, user: User | StarterEnum):
        self.logs = []
        super().__init__(event=Event, user=user)

    async def send(self, msg: str):
        try:
            msg = await self.set_msg(msg)
            # 将消息添加到日志列表中。
            self.logs.append(msg + "\n")
            return await super().send(msg)
        except Exception as e:
            # 记录发送过程中出现的错误。
            log.error(e)


    async def clear_logs(self):
        self.logs = []

