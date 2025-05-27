from fastapi import APIRouter, Depends
from app.controller import Authentication
from app.mapper.interface.interfaceGroupMapper import InterfaceGroupMapper
from app.model.base import User
from app.response import Response
from app.schema.interface.interfaceGroupSchema import *
from interface.starter import APIStarter
from interface.runner import InterFaceRunner
from utils import MyLoguru, log

LOG = MyLoguru().get_logger()
router = APIRouter(prefix="/interface/group", tags=['自动化接口步骤'])


@router.post("/insert", description="添加组")
async def insert_group(group: InsertInterfaceGroupSchema, cr: User = Depends(Authentication())):
    group = await InterfaceGroupMapper.save(creatorUser=cr, **group.model_dump())
    return Response.success(group)


@router.get("/detail", description="添加组")
async def get_group(groupId: int, cr: User = Depends(Authentication())):
    group = await InterfaceGroupMapper.get_by_id(ident=groupId)
    return Response.success(group)


@router.post("/update", description="更新组")
async def update_group(group: UpdateInterfaceGroupSchema, cr: User = Depends(Authentication())):
    await InterfaceGroupMapper.update_by_id(updateUser=cr, **group.model_dump(exclude_unset=True,
                                                                        exclude_none=True, ))
    return Response.success()


@router.post("/page", description="组分页")
async def page_group(group: PageInterfaceGroupSchema, _: User = Depends(Authentication())):
    log.debug(group)
    data = await InterfaceGroupMapper.page_by_module(**group.model_dump(exclude_unset=True,
                                                                  exclude_none=True, ))
    return Response.success(data)


@router.post("/remove", description="删除")
async def remove_group(group: RemoveInterfaceGroupSchema, cr: User = Depends(Authentication())):
    await InterfaceGroupMapper.remove_group(group.id)
    return Response.success()


@router.post("/add_association/apis", description="关联apis")
async def association_apis(info: AssociationAPIS2GroupSchema, cr: User = Depends(Authentication())):
    await InterfaceGroupMapper.association_common_apis(**info.model_dump())
    return Response.success()


@router.post("/add_association/api", description="关联api")
async def association_apis(info: AssociationAPI2GroupSchema, cr: User = Depends(Authentication())):
    await InterfaceGroupMapper.association_api(**info.model_dump())
    return Response.success()


@router.post("/copy_association/api", description="关联api")
async def copy_association_apis(info: AssociationAPI2GroupSchema, cr: User = Depends(Authentication())):
    await InterfaceGroupMapper.copy_association_api(cr=cr, **info.model_dump())
    return Response.success()

@router.post("/copy", description="复制组")
async def copy_group(
        info: CopyInterfaceGroupSchema,  # 使用正确的Schema
        cr: User = Depends(Authentication())
):
    await InterfaceGroupMapper.copy_group(**info.model_dump(), creator=cr)
    return Response.success()


@router.get("/query_association/apis", description="关联api")
async def association_apis(groupId: int, cr: User = Depends(Authentication())):
    apis = await InterfaceGroupMapper.query_apis(groupId)
    return Response.success(apis)


@router.post("/remove_association/api", description="关联api")
async def association_apis(info: AssociationAPI2GroupSchema, cr: User = Depends(Authentication())):
    await InterfaceGroupMapper.remove_api(info.groupId, info.apiId)
    return Response.success()


@router.post("/reorder_association/apis", description="关联api")
async def association_apis(info: AssociationAPIS2GroupSchema, cr: User = Depends(Authentication())):
    await InterfaceGroupMapper.reorder_apis(**info.model_dump())
    return Response.success()


@router.get("/try", description="关联api")
async def try_group(groupId: int, user: User = Depends(Authentication())):
    _starter = APIStarter(user)
    resp = await InterFaceRunner(
        starter=_starter
    ).try_group(groupId)
    return Response.success(resp)
