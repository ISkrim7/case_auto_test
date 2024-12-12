from app.schema import BaseSchema, PageSchema
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Literal


class InterfaceCaseTaskFieldSchema(BaseModel):
    id: int | None = None
    uid: str | None = None
    title: str | None = None
    desc: str | None = None
    cron: str | None = None
    switch: int | bool | None = None
    status: str | None = None
    level: str | None = None
    total_cases_num: int | None = 0
    part_id: int | None = None
    project_id: int | None = None


class PageInterfaceCaseTaskSchema(InterfaceCaseTaskFieldSchema, PageSchema):
    ...


class InsertInterfaceCaseTaskSchema(InterfaceCaseTaskFieldSchema):
    title: str
    desc: str
    switch: int | bool
    status: str
    level: str
    part_id: int
    project_id: int


class OptionInterfaceCaseTaskSchema(InterfaceCaseTaskFieldSchema):
    id: int


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
