from app.schema import BaseSchema, PageSchema
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Literal


class InterfaceCaseTaskFieldSchema(BaseModel):
    id: int | None = None
    uid: str | None = None
    title: str | None = None
    desc: str | None = None
    cron: str | None = None
    status: str | None = "WAIT"
    level: str | None = None
    total_cases_num: int | None = 0
    part_id: int | None = None
    project_id: int | None = None

    is_auto: int | None = 0
    is_send: int | None = 0
    retry: int | None = 0
    send_type: int | None = None
    send_key: str | None = None


class PageInterfaceCaseTaskSchema(InterfaceCaseTaskFieldSchema, PageSchema):
    ...


class InsertInterfaceCaseTaskSchema(InterfaceCaseTaskFieldSchema):
    title: str
    desc: str
    level: str
    part_id: int
    project_id: int


class OptionInterfaceCaseTaskSchema(InterfaceCaseTaskFieldSchema):
    id: int

class GetByTaskId(BaseModel):
    taskId:int

class AssocCasesSchema(BaseModel):
    taskId: int
    caseIds: List[int]


class RemoveAssocCasesSchema(BaseModel):
    taskId: int
    caseId: int


class AssocApisSchema(BaseModel):
    taskId: int
    apiIds: List[int]


class RemoveAssocApisSchema(BaseModel):
    taskId: int
    apiId: int
