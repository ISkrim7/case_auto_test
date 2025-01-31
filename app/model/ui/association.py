from sqlalchemy import Table, Column, INTEGER, ForeignKey

from app.model import BaseModel

case_step_association = Table('ui_case_steps_association', BaseModel.metadata,
                              Column('ui_case_id', INTEGER, ForeignKey('ui_case.id')),
                              Column('ui_case_step_id', INTEGER, ForeignKey('ui_case_steps.id')),
                              Column('step_order', INTEGER))
