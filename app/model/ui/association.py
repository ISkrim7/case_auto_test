from sqlalchemy import Column, INTEGER, ForeignKey
from app.model.basic import base


class CaseStepAssociation(base):
    __tablename__ = "ui_case_steps_association"
    ui_case_id = Column(INTEGER, ForeignKey('ui_case.id'), primary_key=True)
    ui_case_step_id = Column(INTEGER, ForeignKey('ui_case_steps.id'), primary_key=True)
    step_order = Column(INTEGER)

    def __repr__(self):
        return f"<CaseStepAssociation(ui_case_id={self.ui_case_id}, ui_case_step_id={self.ui_case_step_id}, step_order={self.step_order})>"


class CaseTaskAssociation(base):
    __tablename__ = "ui_case_tasks_association"
    ui_case_id = Column(INTEGER, ForeignKey('ui_case.id'), primary_key=True)
    ui_task_id = Column(INTEGER, ForeignKey('ui_task.id'), primary_key=True)
    case_order = Column(INTEGER)

    def __repr__(self):
        return f"<CaseTaskAssociation(ui_case_id={self.ui_case_id},step_order={self.step_order}, task_id={self.ui_task_id}>"

class GroupStepAssociation(base):
    __tablename__ = "ui_group_step_association"
    ui_group_id = Column(INTEGER, ForeignKey("ui_step_group.id"),primary_key=True)
    ui_step_id =  Column(INTEGER, ForeignKey("ui_case_steps.id"),primary_key=True)
    step_order = Column(INTEGER)
