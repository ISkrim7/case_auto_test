from app.model.basic import BaseModel
from sqlalchemy import Column, String, INTEGER, ForeignKey, JSON, Table, BOOLEAN


class EnvModel(BaseModel):
    __tablename__ = 'env'

    name = Column(String(50), nullable=False, comment="环境名称")
    desc = Column(String(200), nullable=True, comment="环境描述")
    host = Column(String(200), nullable=False, comment="环境host")
    port = Column(String(20), nullable=True, comment="环境host")
    project_id = Column(INTEGER,
                        ForeignKey('project.id', ondelete='CASCADE'),
                        nullable=False, comment="项目所属")

    def __repr__(self):
        return f"<{EnvModel.__name__} {self.name} host={self.host} port={self.port}>"
