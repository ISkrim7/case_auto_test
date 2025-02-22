from app.model.basic import BaseModel
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
