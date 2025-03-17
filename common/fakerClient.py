
from faker import Faker
import time
from datetime import datetime, timedelta

from utils import log


class FakerClient:
    faker = Faker(locale="zh_CN")

    def value(self, script: str):
        log.info(f"script = {script}")
        if script.startswith("f_"):
            _script = script.split("f_")[-1]
            return self._get_faker_value(_script)
        else:
            try:
                value = getattr(self, script)()
                return value
            except AttributeError as e:
                return ""

    def _get_faker_value(self, script: str):
        try:
            value = getattr(self.faker, script)()
            return value
        except AttributeError as e:
            return ""

    def timestamp(self) -> int | None:
        """
        返回对应时间戳
        ：param t +1s 秒  +1m 分 +1h分钟
        """
        return int(time.time() * 1000)

    def today(self) -> str | None:
        current_date = datetime.today().strftime("%Y-%m-%d")
        return current_date

    def now(self) -> str:
        current_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        return current_date

    def yesterday(self) -> str:
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        return yesterday_str

    def monthFirst(self) -> str:
        """
        获取当月1号
        :return:
        """
        current_date = datetime.now()
        # 构造当月1号日期
        first_day_of_month = current_date.replace(day=1)
        return first_day_of_month.strftime("%Y-%m-%d")


if __name__ == '__main__':
    f = FakerClient()
    f.value("monthFddasirst")
