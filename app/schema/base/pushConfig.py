from pydantic import BaseModel

from app.schema import PageSchema


class PushConfigSchema(BaseModel):
    id: int | None = None
    uid: str | None = None
    push_name: str | None = None
    push_desc: str | None = None
    push_type: str | None = None
    push_value: str | None = None


class InsertPushSchema(PushConfigSchema):
    push_name: str
    push_desc: str | None = None
    push_type: str
    push_value: str


class OptPushSchema(PushConfigSchema):
    id: int


class PagePushSchema(PushConfigSchema, PageSchema):
    ...
