from app.model.base import User
from utils import GenerateTools, MyLoguru
from app.ws import io

log = MyLoguru().get_logger()


class SocketSender:
    uid: str = None
    starterId:int =None
    user:User=None
    prefix: str = ""

    def __init__(self, user: User = None):
        self.logs = []
        if user is not None:
            self.user = user
            self.uid = user.uid


    async def setCasePrefix(self, uid: str):
        self.prefix = self.prefix + "caseId = {uid}"

    async def send(self, msg: str):
        try:
            msg = f"{GenerateTools.getTime(1)} 🚀 🚀 🟰🟰 {msg} \n"
            log.info(msg)
            await io.log_emit(msg, uid=self.uid)
        except Exception as e:
            log.error(e)

    async def over(self, reportId: int = None):
        return await io.log_emit_over(rId=reportId, uid=self.uid)

    async def clear_logs(self):
        self.logs = []
