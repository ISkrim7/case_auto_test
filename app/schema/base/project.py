from pydantic import BaseModel, Field
from app.schema import PageSchema


class ProjectField(BaseModel):
    id: int | None = None
    uid: str | None = None
    title: str | None = None
    desc: str | None = None
    chargeId: int | None = None
    chargeName: str | None = None


class InsertProjectSchema(BaseModel):
    title: str
    desc: str
    chargeId: int


class UpdateProjectSchema(ProjectField):
    ...


class DeleteProjectSchema(ProjectField):
    projectId: int = Field(alias="id")


class PageProjectSchema(ProjectField, PageSchema):
    ...
