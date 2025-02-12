from typing import List

from pydantic import Field, BaseModel

from app.schema import PageSchema


class InterfaceApiGroupFieldSchema(BaseModel):
    """
    接口步骤字段
    """
    id: int | None = None
    uid: str | None = None
    name: str | None = None
    description: str | None = None
    api_num: int = 0


class InsertInterfaceGroupSchema(InterfaceApiGroupFieldSchema):
    name: str
    description: str


class UpdateInterfaceGroupSchema(InterfaceApiGroupFieldSchema):
    id: int


class RemoveInterfaceGroupSchema(InterfaceApiGroupFieldSchema):
    id: int


class PageInterfaceGroupSchema(InterfaceApiGroupFieldSchema, PageSchema):
    ...


class AssociationAPI2GroupSchema(BaseModel):
    apis: List[int]
    groupId: int


class InterfaceGroupDetailSchema(BaseModel):
    groupId: int
