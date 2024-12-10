from typing import List

from app.schema import PageSchema
from pydantic import BaseModel


class InterfaceCaseSchema(BaseModel):
    id: int | None = None
    uid: str | None = None
    title: str | None = None
    desc: str | None = None
    level: str | None = None
    status: str | None = None
    part_id: int | None = None
    project_id: int | None = None


class InsertInterfaceCaseBaseInfoSchema(InterfaceCaseSchema):
    title: str
    desc: str
    level: str
    status: str
    part_id: int
    project_id: int


class OptionInterfaceCaseSchema(InterfaceCaseSchema):
    id: int


class ExecuteInterfaceCaseSchema(InterfaceCaseSchema):
    caseId: int


class PageInterfaceCaseSchema(InterfaceCaseSchema, PageSchema):
    ...


class AddInterfaceCaseCommonAPISchema(BaseModel):
    caseId: int
    commonApis: List[int]


class AddInterfaceApi2Case(BaseModel):
    caseId: int
    apiId: int


class RemoveInterfaceApi2Case(AddInterfaceApi2Case):
    ...


class ReorderInterfaceApi2Case(BaseModel):
    caseId: int
    apiIds: List[int]
