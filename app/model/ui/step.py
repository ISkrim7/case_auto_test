from sqlalchemy import Column, String, BOOLEAN, ForeignKey, INTEGER, JSON
from sqlalchemy.orm import relationship

from app.model import BaseModel


class SubStepModel(BaseModel):
    __tablename__ = "ui_case_sub_step"
    name = Column(String(40), nullable=False, comment="子步骤名称")
    description = Column(String(40), nullable=False, comment="子步骤描述")
    method = Column(String(40), nullable=True, comment="子步骤方法")
    locator = Column(String(100), nullable=True, comment="子步骤元素定位器")
    value = Column(String(100), nullable=True, comment="子步骤输入的值")
    iframe_name = Column(String(100), nullable=True, comment="子步骤是否是iframe")
    new_page = Column(BOOLEAN, default=False, comment="子步骤是否打开新页面")
    is_ignore = Column(BOOLEAN, default=False, comment="子步骤忽略异常")
    stepId = Column(INTEGER, ForeignKey("ui_case_steps.id", ondelete="CASCADE", ), nullable=False)
    order = Column(INTEGER, nullable=False, comment="排序")

    def __repr__(self):
        return f"<SubStep {self.name}>"


class UICaseStepsModel(BaseModel):
    """
    ui case step 模型
    """
    __tablename__ = "ui_case_steps"
    name = Column(String(40), nullable=False, comment="步骤名称")
    description = Column(String(40), nullable=False, comment="步骤描述")
    method = Column(String(40), nullable=True, comment="步骤方法")
    locator = Column(String(100), nullable=True, comment="步骤元素定位器")
    value = Column(String(100), nullable=True, comment="输入的值")
    iframe_name = Column(String(100), nullable=True, comment="是否是iframe")
    new_page = Column(BOOLEAN, default=False, comment="是否打开新页面")
    api_url = Column(String(100), nullable=True, comment="监听接口")
    is_common_step = Column(BOOLEAN, default=False, comment="是否是公共步骤")
    is_ignore = Column(BOOLEAN, default=False, comment="忽略异常")
    has_api = Column(INTEGER, default=0, nullable=True, comment="是否是api 1有0无")
    has_sql = Column(INTEGER, default=0, nullable=True, comment="是否是sql 1有0无")
    has_condition = Column(INTEGER, default=0, nullable=True, comment="是否是条件 1有0无")
    condition = Column(JSON, nullable=True, comment="条件")
    api = relationship("UIStepAPIModel",
                       cascade="all, delete-orphan",
                       backref="interface", lazy="dynamic")
    sql = relationship("UIStepSQLModel",
                       cascade="all, delete-orphan",
                       backref="sql", lazy="dynamic")
    is_group = Column(BOOLEAN, default=False, comment="是否是组")
    group_Id = Column(INTEGER,
                      nullable=True, comment="所属组id")

    def __str__(self):
        return f"用例步骤 id={self.id} name={self.name} description={self.description} method={self.method}..."

    def __repr__(self):
        return (
            f"<UICaseStepsModel(id={self.id}"
            f" name='{self.name}',"
            f" description='{self.description}',"
            f" method='{self.method}',"
            f" locator='{self.locator}',"
            f"value={self.value}, "
            f"iframeName='{self.iframe_name}',"
            f" new_page='{self.new_page}"
            f"' ignore={self.is_ignore})>"
        )
