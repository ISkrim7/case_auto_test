from app.model.basic import BaseModel, base
from sqlalchemy import Column, INTEGER, ForeignKey, select


class InterCaseAssociation(base):
    """
    接口 业务用例 中间表
    """
    __tablename__ = "interface_case_association"

    interface_id = Column(INTEGER, ForeignKey('interface.id'), primary_key=True)
    inter_case_id = Column(INTEGER, ForeignKey('interface_case.id'), primary_key=True)
    step_order = Column(INTEGER)

    def __repr__(self):
        return f"<InterCaseAssociation(interface_id={self.interface_id}, inter_case_id={self.inter_case_id}, step_order={self.step_order}) />"



class CaseTaskAssociation(base):
    """
    业务用例与任务中间表
    """
    __tablename__ = "interface_task_association"

    inter_case_id = Column(INTEGER, ForeignKey('interface_case.id'), primary_key=True)
    task_id = Column(INTEGER, ForeignKey('interface_task.id'), primary_key=True)
    step_order = Column(INTEGER)

    def __repr__(self):
        return f"<CaseTaskAssociation(inter_case_id={self.inter_case_id}, task_id={self.task_id}, step_order={self.step_order}) />"


#
class ApiTaskAssociation(base):
    """
    接口 任务中间表
    """
    __tablename__ = "interface_api_task_association"

    api_id = Column(INTEGER, ForeignKey('interface.id'), primary_key=True)
    task_id = Column(INTEGER, ForeignKey('interface_task.id'), primary_key=True)
    step_order = Column(INTEGER)

    def __repr__(self):
        return f"<ApiTaskAssociation(api_id={self.api_id}, task_id={self.task_id}, step_order={self.step_order}) />"


class GroupApiAssociation(base):
    """
    接口 接口组 中间表
    """
    __tablename__ = "interface_group_api_association"

    api_group_id = Column(INTEGER, ForeignKey('interface_group.id'), primary_key=True)
    api_id = Column(INTEGER, ForeignKey('interface.id'), primary_key=True)
    step_order = Column(INTEGER)

    def __repr__(self):
        return f"<GroupApiAssociation(api_group_id={self.api_group_id}, api_id={self.api_id}, step_order={self.step_order}) />"
