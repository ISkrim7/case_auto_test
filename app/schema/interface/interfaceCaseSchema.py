from typing import List

from app.schema import PageSchema
from pydantic import BaseModel

__all__ = [
    "InterfaceCaseSchema",
    "InsertInterfaceCaseBaseInfoSchema",
    "OptionInterfaceCaseSchema",
    "ExecuteInterfaceCaseSchema",
    "PageInterfaceCaseSchema",
    "AddInterfaceCaseCommonAPISchema",
    "AddInterfaceCaseCommonGROUPSchema",
    "AddInterfaceApi2Case",
    "RemoveInterfaceApi2Case",
    "ReorderInterfaceApi2Case",
]

from enums import ModuleEnum


class InterfaceCaseSchema(BaseModel):
    id: int | None = None
    uid: str | None = None
    title: str | None = None
    desc: str | None = None
    level: str | None = None
    status: str | None = None
    module_id: int | None = None
    project_id: int | None = None
    error_stop: int | None = None


class InsertInterfaceCaseBaseInfoSchema(InterfaceCaseSchema):
    title: str
    desc: str
    level: str
    status: str
    module_id: int
    project_id: int


class OptionInterfaceCaseSchema(InterfaceCaseSchema):
    id: int


class ExecuteInterfaceCaseSchema(InterfaceCaseSchema):
    caseId: int


class PageInterfaceCaseSchema(InterfaceCaseSchema, PageSchema):
    module_type: int = ModuleEnum.API_CASE


class AddInterfaceCaseCommonAPISchema(BaseModel):
    caseId: int
    commonApis: List[int]


class AddInterfaceCaseCommonGROUPSchema(BaseModel):
    caseId: int
    groupIds: List[int]


class AddInterfaceApi2Case(BaseModel):
    caseId: int
    apiId: int


class RemoveInterfaceApi2Case(AddInterfaceApi2Case):
    ...


class ReorderInterfaceApi2Case(BaseModel):
    caseId: int
    apiIds: List[int]
