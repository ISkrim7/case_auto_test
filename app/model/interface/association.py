from app.model.basic import BaseModel, base
from sqlalchemy import Column, INTEGER, ForeignKey, Table

inter_case_association = Table('interface_case_association', BaseModel.metadata,
                               Column('interface_id', INTEGER, ForeignKey('interface.id')),
                               Column('inter_case_id', INTEGER, ForeignKey('interface_case.id')),
                               Column('step_order', INTEGER)  # 存储排序顺序
                               )

# 任务与用例关联表
case_task_association = Table('interface_task_association', BaseModel.metadata,
                              Column('inter_case_id', INTEGER, ForeignKey('interface_case.id')),
                              Column('task_id', INTEGER, ForeignKey('interface_task.id')),
                              Column('step_order', INTEGER)  # 存储排序顺序
                              )
# 任务与api关联表
api_task_association = Table('interface_api_task_association', BaseModel.metadata,
                             Column('api_id', INTEGER, ForeignKey('interface.id')),
                             Column('task_id', INTEGER, ForeignKey('interface_task.id')),
                             Column('step_order', INTEGER)  # 存储排序顺序
                             )
# group api
group_api_association = Table('interface_group_api_association', BaseModel.metadata,
                              Column('api_group_id', INTEGER, ForeignKey('interface_group.id')),
                              Column('api_id', INTEGER, ForeignKey('interface.id')),
                              Column('step_order', INTEGER))


# class InterCaseAssociation(base):
#     __tablename__ = "interface_case_association"
#
#     interface_id = Column(INTEGER, ForeignKey('interface.id'))
#     inter_case_id = Column(INTEGER, ForeignKey('interface_case.id'))
#     step_order = Column(INTEGER)
#
#     def __repr__(self):
#         return f"<InterCaseAssociation(interface_id={self.interface_id}, inter_case_id={self.inter_case_id}, step_order={self.step_order}) />"
#
#
# class CaseTaskAssociation(base):
#     __tablename__ = "interface_task_association"
#
#     inter_case_id = Column(INTEGER, ForeignKey('interface_case.id'))
#     task_id = Column(INTEGER, ForeignKey('interface_task.id'))
#     step_order = Column(INTEGER)
#
#     def __repr__(self):
#         return f"<CaseTaskAssociation(inter_case_id={self.inter_case_id}, task_id={self.task_id}, step_order={self.step_order}) />"
#
#
# class ApiTaskAssociation(base):
#     __tablename__ = "interface_api_task_association"
#
#     api_id = Column(INTEGER, ForeignKey('interface.id'))
#     task_id = Column(INTEGER, ForeignKey('interface_task.id'))
#     step_order = Column(INTEGER)
#
#     def __repr__(self):
#         return f"<ApiTaskAssociation(api_id={self.api_id}, task_id={self.task_id}, step_order={self.step_order}) />"
#
#
# class GroupApiAssociation(base):
#     __tablename__ = "interface_group_api_association"
#
#     api_group_id = Column(INTEGER, ForeignKey('interface_group.id'))
#     api_id = Column(INTEGER, ForeignKey('interface.id'))
#     step_order = Column(INTEGER)
#
#     def __repr__(self):
#         return f"<GroupApiAssociation(api_group_id={self.api_group_id}, api_id={self.api_id}, step_order={self.step_order}) />"
