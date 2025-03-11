from sqlalchemy import Column, Integer, String

from app.model import BaseModel


class PushModel(BaseModel):
    __tablename__ = 'push_config'

    push_type = Column(Integer, nullable=False, comment='推送类型')
    push_name = Column(String(50), nullable=False, comment='推送名')
    push_desc = Column(String(100), nullable=False, comment='推送描述')
    push_value = Column(String(255), nullable=False, comment='推送token')

    def __repr__(self):
        return f"<PushModel(push_type={self.push_type}, push_name={self.push_name}, push_desc={self.push_desc}, push_value={self.push_value})>"