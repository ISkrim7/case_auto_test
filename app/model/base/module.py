from sqlalchemy import Column, String, Integer

from app.model import BaseModel


class Module(BaseModel):
    __tablename__ = 'module'

    title = Column(String(50), comment="用例模块")
    parent_id = Column(Integer, comment="父级模块")
    project_id = Column(Integer, comment="项目id")
    module_type = Column(Integer, comment="模块类型")
    order = Column(Integer, default=0, comment="排序字段")

    @property
    def map(self):
        return {
            "key": self.id,
            "title": self.title,
            "parent_id": self.parent_id,
            "project_id": self.project_id,
            "module_type": self.module_type,
            "order": self.order
        }

    def __repr__(self):
        return "<Module(title='%s', parent_id='%s', project_id='%s', order='%s')>" % (
            self.title, self.parent_id, self.project_id, self.order
        )
