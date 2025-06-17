from pydantic import BaseModel


class ModuleSchemaField(BaseModel):
    id: int | None = None
    uid: str | None = None
    title: str | None = None
    project_id: int | None = None
    parent_id: int | None = None
    module_type: int | None = None


class InsertModuleSchema(ModuleSchemaField):
    title: str
    project_id: int
    module_type: int


class UpdateModuleSchema(BaseModel):
    title: str | None = None
    id: int


class RemoveModuleSchema(BaseModel):
    moduleId: int


class DropModuleSchema(BaseModel):
    id: int
    targetId: int | None = None
    new_order: int | None = None
