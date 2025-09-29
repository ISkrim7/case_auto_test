import enum

from app.model.base import User


class TaskStatus:
    RUNNING = "RUNNING"
    DONE = "DONE"


class TaskResult:
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


class StarterEnum(enum.Enum):
    User = 1
    Jenkins = 2
    RoBot = 3

class ErrorStopPolicy(enum.IntEnum):
    """错误停止策略枚举"""
    CONTINUE = 0  # 继续执行后续用例
    STOP = 1      # 停止执行后续用例
    RETRY = 2     # 重试当前用例(暂未实现)