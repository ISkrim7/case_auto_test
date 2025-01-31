from sqlalchemy import Column, INTEGER

from app.model import BaseModel


class UIConfig(BaseModel):

    __tablename__ = 'ui_config'

    timeout = Column(INTEGER, default=5000,comment="超时时间")
    slow = Column(INTEGER,default=500,comment="点击时间")


