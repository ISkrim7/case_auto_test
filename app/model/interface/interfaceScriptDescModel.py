from app.model.basic import BaseModel
from sqlalchemy import Column, String



class InterfaceScriptDesc(BaseModel):
    __tablename__ = 'interface_scriptDesc'

    title = Column(String(100), nullable=False, comment="标题")
    subTitle = Column(String(100), nullable=True, comment="副标题")
    args = Column(String(100), nullable=True, comment="参数")
    desc = Column(String(100), nullable=True, comment="描述")
    example = Column(String(200), nullable=True, comment="例子")
    returnContent = Column(String(200), nullable=True, comment="返回")



a = """
  {
    title: 'timestamp(day:str = None)-> str 获取时间戳',
    subTitle: 'Func',
    args: ['+1s', '-1s', '+1m', '-1m', '+1h', '-1h'],
    description: '获取不同时间的时间戳',
    example:
      "例子: ts = timestamp() 返回当前时间戳 ts = timestamp('+1s') 返回1秒后的时间戳",
    returnContent: ':return 1705114614000',
  },
  """


