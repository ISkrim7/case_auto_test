from typing import Any

from pydantic import BaseModel

from app.schema import PageSchema


class GlobalSchemaField(BaseModel):
    id: int | None = None
    uid: str | None = None
    key: str = None
    value: str | None = None
    description: str | None = None
    project_id: int | None = None


class AddGlobalSchema(GlobalSchemaField):
    key: str
    value: str
    project_id: int


class UpdateGlobalSchema(GlobalSchemaField):
    uid: str
    key: str
    value: str
    project_id: int


class SetGlobalSchema(BaseModel):
    uid: str


class PageGlobalSchema(GlobalSchemaField, PageSchema):
    ...
