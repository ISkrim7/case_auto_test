#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2024/11/20
# @Author : Zulu
# @File : mockApi
# @Software: PyCharm
# @Desc: Mock接口功能实现

from fastapi import APIRouter, Depends, BackgroundTasks, Response as FastResponse, Form, UploadFile, File, HTTPException, Query, Request
from interface.mock import mock_request_checker
from app.controller import Authentication
from app.mapper.interface.mockMapper import MockRuleMapper, MockConfigMapper
from app.model.base import User
import json
from app.response import Response
from app.schema.interface import *
from utils import MyLoguru, log
from utils.fileManager import FileManager
from typing import Optional, List, Dict, Sequence, Union
from pydantic import validator
from app.exception import NotFind
from app.model import async_session
from interface.mock import get_mock_manager

router = APIRouter(prefix="/mock", tags=['Mock接口'])

class CreateMockSchema(BaseSchema):
    """创建Mock规则请求体"""
    path: str = Field(..., min_length=1, max_length=500, description="接口路径")
    mockname: Optional[str] = Field(None, max_length=100, description="Mock接口名称")
    method: str = Field("GET", description="请求方法", pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    status_code: int = Field(200, description="响应状态码", ge=200, le=599, alias="statusCode")
    response: Optional[Union[dict, str]] = Field(None, description="响应内容")
    delay: Optional[float] = Field(None, description="延迟响应(毫秒)", ge=0, le=10000)
    description: Optional[str] = Field(None, max_length=200, description="规则描述")
    headers: Optional[dict] = Field(None, description="响应头")
    cookies: Optional[dict] = Field(None, description="响应Cookies")
    content_type: Optional[str] = Field(None, description="响应内容类型")
    script: Optional[str] = Field(None, description="前置/后置脚本")
    interface_id: Optional[int] = Field(None, description="关联接口ID")

    @validator('response')
    def parse_response(cls, v):
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                return {"raw": v}
        return v

class MockResponseSchema(BaseSchema):
    """Mock规则响应体"""
    path: str
    method: str
    status_code: int
    response: Optional[dict]
    delay: Optional[float]
    description: Optional[str]

class LinkInterfaceSchema(BaseModel):
    """关联接口请求体"""
    interface_id: int = Field(..., description="接口ID")
    path: str = Field(..., min_length=1, max_length=500, description="Mock路径")
    method: str = Field("GET", description="请求方法", pattern="^(GET|POST|PUT|DELETE|PATCH)$")

@router.post("/create",
            description="创建Mock接口规则",
            responses={
                400: {"description": "参数验证失败"},
                409: {"description": "规则已存在"},
                500: {"description": "服务器内部错误"}
            })
async def create_mock_rule(
    rule: CreateMockSchema,
    user: User = Depends(Authentication())
):
    """创建当前用户的Mock接口规则"""
    try:
        async with async_session() as session:
            async with session.begin():
                # 1. 检查规则是否已存在
                existing_rule = await MockRuleMapper.get_by_path_method(
                    path=rule.path,
                    method=rule.method,
                    user_id=user.id,
                    session=session
                )

                if existing_rule:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "code": 409,
                            "message": f"该路径({rule.path})和方法({rule.method})的Mock规则已存在",
                            "data": {
                                "existing_rule_id": existing_rule.id,
                                "suggestion": "您可以选择更新现有规则或删除后重新创建"
                            }
                        }
                    )

                # 2. 创建新规则
                mock_rule = await MockRuleMapper.save(
                    session=session,
                    user_id=user.id,
                    path=rule.path,
                    mockname=rule.mockname,
                    method=rule.method,
                    status_code=rule.status_code,
                    response=rule.response,
                    delay=rule.delay,
                    description=rule.description,
                    headers=rule.headers,
                    cookies=rule.cookies,
                    content_type=rule.content_type,
                    script=rule.script,
                    interface_id=rule.interface_id,
                    creator=user.id,
                    creatorName=user.username
                )

                # 3. 获取完整规则数据
                await session.refresh(mock_rule)  # 确保获取最新数据
                rule_data = mock_rule.to_dict()

                # 4. 刷新缓存
                manager = await get_mock_manager(user.id, session)
                manager.user_rules.pop(user.id, None)  # 清除用户规则缓存

                log.info(f"用户{user.username}创建Mock规则成功: ID={rule_data['id']}")
                return Response.success(
                    data=rule_data,
                    #message="Mock规则创建成功"
                )

    except HTTPException as he:
        log.warning(f"用户{user.username}创建Mock规则时发生HTTP异常: {he.detail}")
        raise he
    except Exception as e:
        log.exception(f"用户{user.username}创建Mock规则失败: {str(e)}")
        if "validation" in str(e).lower():
            raise HTTPException(status_code=400, detail="参数验证失败，请检查请求参数格式")
        raise HTTPException(
            status_code=500,
            detail=f"创建Mock规则失败: {str(e)}"
        )

class PageMockSchema(BaseSchema):
    """Mock规则分页查询参数"""
    current: int = Field(1, ge=1, description="页码")
    pageSize: int = Field(10, ge=1, le=100, description="每页数量")
    path: Optional[str] = Field(None, description="接口路径过滤")
    mockname: Optional[str] = Field(None, description="Mock名称过滤")
    method: Optional[str] = Field(None, description="请求方法过滤")
    status_code: Optional[int] = Field(None, description="状态码过滤")
    enable: Optional[bool] = Field(None, description="启用状态过滤")

@router.post("/page",
           description="分页查询Mock规则",
           responses={
               500: {"description": "服务器内部错误"}
           })
async def page_mock_rules(
    query: PageMockSchema,
    user: User = Depends(Authentication())  # 获取用户
    #_: User = Depends(Authentication())
):
    """分页查询Mock规则"""
    try:
        result = await MockRuleMapper.page_query(
            user_id=user.id,  # 传递用户ID
            **query.model_dump(
                exclude_unset=True,
                exclude_none=True
            )
        )
        return Response.success({
            "total": result["total"],
            "items": result["items"]
        })
    except Exception as e:
        log.exception(f"分页查询Mock规则失败: {e}")
        raise HTTPException(status_code=500, detail="分页查询Mock规则失败")

@router.get("/list",
           description="获取Mock规则列表，可指定interface_id进行过滤",
           responses={
               500: {"description": "服务器内部错误"}
           })
async def list_mock_rules(
    interface_id: Optional[int] = None,
    user: User = Depends(Authentication())
):
    """获取当前用户的Mock规则列表

    Args:
        interface_id: 可选，指定接口ID进行过滤
    """
    try:
        async with async_session() as session:
            async with session.begin():
                # 获取当前用户的所有规则
                rules = await MockRuleMapper.query_all(
                    user_id=user.id,
                    session=session
                )

                # 按接口ID过滤
                if interface_id is not None:
                    rules = [
                        rule for rule in rules
                        if rule.interface_id == interface_id
                    ]

                # 转换为字典格式
                result = [rule.to_dict() for rule in rules]

                log.info(f"用户{user.username}获取了{len(result)}条Mock规则")
                return Response.success(result)

    except Exception as e:
        log.exception(f"用户{user.username}获取Mock规则列表失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取Mock规则列表失败: {str(e)}"
        )

class MockRuleDetailSchema(BaseModel):
    """Mock规则详情响应体"""
    id: int
    interface_id: Optional[int]
    path: str
    mockname: Optional[str]
    method: str
    status_code: int
    response: Optional[dict]
    delay: Optional[float]
    enable: bool
    description: Optional[str]
    creator: Optional[int]
    creatorName: Optional[str]
    headers: Optional[dict]
    cookies: Optional[dict]
    content_type: Optional[str]
    script: Optional[str]

# @router.get("/detail",
#             description="根据ID获取Mock规则详情",
#             responses={
#                 400: {"description": "参数验证失败"},
#                 404: {"description": "Mock规则不存在"},
#                 500: {"description": "服务器内部错误"}
#             },
#             response_model=MockRuleDetailSchema)
# async def get_mock_rule_by_id(
#     rule_id: int = Query(..., description="Mock规则ID", gt=0),
#     _: User = Depends(Authentication())
# ):
#     """
#     根据ID获取Mock规则详情
#     :param rule_id: Mock规则ID
#     :return: Mock规则详情
#     """
#     try:
#         log.info(f"开始查询Mock规则详情，rule_id: {rule_id}")
#         rule = await MockRuleMapper.get_by_id(rule_id)
#         if not rule:
#             log.warning(f"未找到ID为{rule_id}的Mock规则")
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"未找到ID为{rule_id}的Mock规则"
#             )
#
#         rule_dict = rule.to_dict()
#         log.debug(f"查询到Mock规则详情: {rule_dict}")
#         return Response.success(rule_dict)
#     except HTTPException:
#         raise
#     except Exception as e:
#         log.exception(f"查询Mock规则详情失败: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"查询Mock规则详情失败: {str(e)}"
#         )
@router.get("/detail",
            description="根据ID获取Mock规则详情",
            responses={
                400: {"description": "参数验证失败"},
                404: {"description": "Mock规则不存在"},
                500: {"description": "服务器内部错误"}
            })  # 关键修改：移除 response_model
async def get_mock_rule_by_id(
        rule_id: int = Query(..., description="Mock规则ID", gt=0),
        #_: User = Depends(Authentication())
        user: User = Depends(Authentication())  # 确保获取当前用户
):
    try:
        log.info(f"请求Mock规则详情，rule_id: {rule_id}")
        async with async_session() as session:
            async with session.begin():
                rule = await MockRuleMapper.get_by_id(
                    rule_id,
                    user_id=user.id,  # 新增
                    session=session,
                    raise_error=True
                )
                # 在会话关闭前转换为字典
                rule_dict = rule.to_dict()
                log.debug(f"成功获取规则详情: PID={rule.id}, Path={rule.path}")
                return Response.success(data=rule_dict)  # 保持项目统一响应格式

    except NotFind as nf:
        log.warning(f"未找到ID为{rule_id}的Mock规则: {nf}")
        raise HTTPException(status_code=404, detail=str(nf))

    except HTTPException as he:
        raise he

    except Exception as e:
        log.critical(f"未处理的异常: {e}")
        raise HTTPException(status_code=500, detail="系统内部错误，请联系管理员")

class BatchRemoveMockSchema(BaseModel):
    """批量删除Mock规则请求体"""
    rules: List[Dict[str, str]] = Field(..., description="要删除的规则列表，每个规则包含path和method字段")


class UpdateMockByIdSchema(BaseModel):
    """根据ID更新Mock规则请求体"""
    rule_id: int = Field(..., description="规则ID")
    path: Optional[str] = Field(None, description="接口路径")
    method: Optional[str] = Field(None, description="请求方法", pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    status_code: Optional[int] = Field(None, description="响应状态码", ge=200, le=599, alias="statusCode")
    mockname: Optional[str] = Field(None, description="Mock接口名称")
    description: Optional[str] = Field(None, description="规则描述")
    response: Optional[Union[dict, str]] = Field(None, description="响应内容")
    headers: Optional[dict] = Field(None, description="响应头")
    delay: Optional[float] = Field(None, description="延迟响应(毫秒)", ge=0, le=10000)

    @validator('response')
    def parse_response(cls, v):
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                return {"raw": v}
        return v

class RemoveMockSchema(BaseModel):
    """删除Mock规则请求体"""
    rule_id: int = Field(..., description="要删除的规则ID")

@router.put("/updateById",
            description="根据ID更新Mock规则",
            responses={
                400: {"description": "参数验证失败"},
                403: {"description": "无权限修改此规则"},
                404: {"description": "Mock规则不存在"},
                409: {"description": "规则已存在"},
                500: {"description": "服务器内部错误"}
            })
async def update_mock_rule_by_id(
    data: UpdateMockByIdSchema,
    user: User = Depends(Authentication())
):
    """更新当前用户的Mock规则"""
    try:
        async with async_session() as session:
            async with session.begin():
                # 1. 获取并验证规则
                rule = await MockRuleMapper.get_by_id(
                    rule_id=data.rule_id,
                    user_id=user.id,
                    session=session,
                    raise_error=True
                )

                # 2. 验证用户所有权
                if rule.user_id != user.id:
                    log.warning(f"用户{user.username}尝试修改无权限的规则ID={data.rule_id}")
                    raise HTTPException(
                        status_code=403,
                        detail="无权限修改此规则"
                    )

                # 3. 检查路径和方法冲突
                if data.path or data.method:
                    new_path = data.path or rule.path
                    new_method = (data.method or rule.method).upper()

                    existing_rule = await MockRuleMapper.get_by_path_method(
                        path=new_path,
                        method=new_method,
                        user_id=user.id,
                        session=session
                    )

                    if existing_rule and existing_rule.id != data.rule_id:
                        raise HTTPException(
                            status_code=409,
                            detail={
                                "code": 409,
                                "message": f"该路径({new_path})和方法({new_method})的Mock规则已存在",
                                "data": {
                                    "existing_rule_id": existing_rule.id,
                                    "suggestion": "您可以选择更新现有规则或删除后重新创建"
                                }
                            }
                        )

                # 4. 准备更新数据
                update_data = data.model_dump(
                    exclude_unset=True,
                    exclude={"rule_id"}
                )
                if "statusCode" in update_data:
                    update_data["status_code"] = update_data.pop("statusCode")

                # 5. 执行更新
                await MockRuleMapper.update_by_id(
                    rule_id=data.rule_id,
                    values=update_data,
                    user_id=user.id,
                    session=session
                )

                # 6. 获取更新后的规则
                updated_rule = await MockRuleMapper.get_by_id(
                    rule_id=data.rule_id,
                    user_id=user.id,
                    session=session,
                    raise_error=True
                )
                rule_data = updated_rule.to_dict()

                # 7. 刷新缓存
                manager = await get_mock_manager(user.id, session)
                manager.user_rules.pop(user.id, None)

                log.info(f"用户{user.username}更新Mock规则成功: ID={data.rule_id}")
                return Response.success(
                    data=rule_data,
                    #message="Mock规则更新成功"
                )

    except HTTPException as he:
        log.warning(f"用户{user.username}更新Mock规则时发生HTTP异常: {he.detail}")
        raise he
    except NotFind as nf:
        log.warning(f"用户{user.username}尝试更新不存在的Mock规则ID={data.rule_id}: {nf}")
        raise HTTPException(status_code=404, detail=str(nf))
    except Exception as e:
        log.exception(f"用户{user.username}更新Mock规则ID={data.rule_id}失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"更新Mock规则失败: {str(e)}"
        )

@router.post("/remove",
            description="删除Mock规则",
            responses={
                400: {"description": "缺少必要参数rule_id"},
                404: {"description": "Mock规则不存在"},
                500: {"description": "服务器内部错误"}
            })
async def remove_mock_rule(
    data: RemoveMockSchema,
    user: User = Depends(Authentication())
):
    """根据ID删除Mock规则"""
    try:
        # await MockRuleMapper.remove_by_id(
        #     rule_id=data.rule_id,
        #     user_id=user.id
        # )
        # return Response.success()
        async with async_session() as session:  # 创建数据库会话
            async with session.begin():  # 开启事务
                # 调用数据访问层方法，传递会话和当前用户ID
                await MockRuleMapper.remove_by_id(
                    rule_id=data.rule_id,
                    user_id=user.id,  # 传递用户ID
                    session=session  # 传递会话对象
                )
        return Response.success()
    except Exception as e:
        log.error(f"删除Mock规则失败: {e}")
        raise HTTPException(status_code=500, detail="删除Mock规则失败")

@router.post("/batchRemove",
            description="批量删除Mock规则",
            responses={
                404: {"description": "部分Mock规则不存在"},
                500: {"description": "服务器内部错误"}
            })
async def batch_remove_mock_rules(
    request: Request,
    user: User = Depends(Authentication())
):
    """根据ID列表批量删除Mock规则"""
    try:
        body = await request.json()
        if isinstance(body, dict) and "rule_ids" in body:
            rule_ids = body["rule_ids"]
        elif isinstance(body, list):
            rule_ids = body
        else:
            raise HTTPException(status_code=400, detail="参数格式错误，应为数组或包含rule_ids字段的对象")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"参数解析失败: {str(e)}")
    try:
        # success_count = 0
        # fail_count = 0
        # for rule_id in rule_ids:
        #     try:
        #         await MockRuleMapper.remove_by_id(
        #             rule_id=rule_id,
        #             user_id=user.id
        #         )
        #         success_count += 1
        #     except Exception:
        #         fail_count += 1
        #
        # if fail_count > 0:
        #     return Response.success({
        #         "success_count": success_count,
        #         "fail_count": fail_count
        #     }, message=f"成功删除{success_count}条规则，失败{fail_count}条")
        # return Response.success(message=f"成功删除{success_count}条规则")
        success_count = 0
        async with async_session() as session:
            async with session.begin():
                for rule_id in rule_ids:
                    try:
                        await MockRuleMapper.remove_by_id(
                            rule_id=rule_id,
                            user_id=user.id,
                            session=session
                        )
                        success_count += 1
                    except Exception:
                        # 记录错误但继续处理其他规则
                        continue
        return Response.success(msg=f"成功删除{success_count}条规则")
    except Exception as e:
        log.error(f"批量删除Mock规则失败: {e}")
        raise HTTPException(status_code=500, detail="批量删除Mock规则失败")

class ToggleMockRuleSchema(BaseModel):
    """切换Mock规则状态请求体"""
    rule_id: int = Field(..., description="规则ID")
    enabled: bool = Field(..., description="启用状态")

@router.post("/rule/enable",
            description="切换单个Mock规则启用状态",
            responses={
                403: {"description": "无权限操作此规则"},
                404: {"description": "Mock规则不存在"},
                500: {"description": "服务器内部错误"}
            })
async def toggle_mock_rule(
    data: ToggleMockRuleSchema,
    user: User = Depends(Authentication())
):
    # """切换单个Mock规则的启用状态"""
    # try:
    #     # 检查规则是否存在
    #     rule = await MockRuleMapper.get_by_id(data.rule_id)
    #     if not rule:
    #         raise HTTPException(status_code=404, detail="Mock规则不存在")
    #
    #     # 更新启用状态
    #     await MockRuleMapper.update_by_id(
    #         data.rule_id,
    #         {"enable": data.enabled, "updater": user.id, "updaterName": user.username}
    #     )
    #
    #     log.info(f"用户{user.username}修改Mock规则状态: id={data.rule_id}, enabled={data.enabled}")
    #     return Response.success()
    # """切换单个Mock规则的启用状态"""
    # try:
    #     # 1. 获取规则并验证用户所有权
    #     async with async_session() as session:
    #         async with session.begin():
    #             rule = await MockRuleMapper.get_by_id(
    #                 rule_id=data.rule_id,
    #                 user_id=user.id,  # 添加当前用户ID
    #                 session=session
    #             )
    #
    #             if not rule or rule.user_id != user.id:
    #                 log.warning(f"用户{user.username}尝试访问无权限的规则ID={data.rule_id}")
    #                 raise HTTPException(
    #                     status_code=403,
    #                     detail="无权限操作此规则"
    #                 )
    #
    #             # 2. 更新启用状态
    #             await MockRuleMapper.update_by_id(
    #                 rule_id=data.rule_id,
    #                 values={
    #                     "enable": data.enabled,
    #                     "updater": user.id,
    #                     "updaterName": user.username
    #                 },
    #                 user_id=user.id,  # 添加用户ID
    #                 session=session
    #             )
    #
    #             # 3. 刷新缓存
    #             manager = await get_mock_manager(user.id)
    #             manager.user_rules.pop(user.id, None)
    #
    #             log.info(f"用户{user.username}修改Mock规则状态: id={data.rule_id}, enabled={data.enabled}")
    #             return Response.success()
    """切换单个Mock规则的启用状态"""
    try:
        async with async_session() as session:
            async with session.begin():  # 确保使用事务
                # 1. 获取规则并验证用户所有权
                rule = await MockRuleMapper.get_by_id(
                    rule_id=data.rule_id,
                    user_id=user.id,
                    session=session
                )

                if not rule:
                    log.warning(f"规则不存在: ID={data.rule_id}")
                    raise HTTPException(
                        status_code=404,
                        detail="Mock规则不存在"
                    )

                if rule.user_id != user.id:
                    log.warning(f"用户{user.username}尝试访问无权限的规则ID={data.rule_id}")
                    raise HTTPException(
                        status_code=403,
                        detail="无权限操作此规则"
                    )

                # 2. 更新启用状态
                update_result = await MockRuleMapper.update_by_id(
                    rule_id=data.rule_id,
                    values={
                        "enable": data.enabled,
                        "updater": user.id,
                        "updaterName": user.username
                    },
                    user_id=user.id,  # 重要：传递用户ID
                    session=session
                )

                # 添加详细日志
                log.debug(f"更新操作结果: {update_result} 行受影响")

                # 3. 刷新规则对象以获取最新数据
                await session.refresh(rule)
                log.info(f"规则状态已更新: ID={data.rule_id}, Enable={rule.enable}")

                # 4. 刷新缓存
                manager = await get_mock_manager(user.id, session)
                manager.user_rules.pop(user.id, None)  # 清除用户规则缓存

                log.info(f"用户{user.username}修改Mock规则状态: id={data.rule_id}, enabled={data.enabled}")
                return Response.success()
    except HTTPException as he:
        raise he
    except Exception as e:
        log.exception(f"切换Mock规则状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"切换Mock规则状态失败: {str(e)}")

@router.get("/rule/status")
async def get_rule_status(
        rule_id: int = Query(..., gt=0),
        user: User = Depends(Authentication())
):
    """获取规则当前状态（直接查数据库）"""
    try:
        async with async_session() as session:
            rule = await MockRuleMapper.get_by_id(
                rule_id=rule_id,
                user_id=user.id,
                session=session
            )

            if not rule:
                return Response.error("规则不存在", code=404)

            return Response.success({
                "id": rule.id,
                "enable": rule.enable,
                "last_update": rule.update_time
            })
    except Exception as e:
        return Response.error(f"获取规则状态失败: {str(e)}")

@router.post("/enable",
            description="启用Mock功能",
            responses={
                500: {"description": "服务器内部错误"}
            })
# async def enable_mock(user: User = Depends(Authentication())):
#     """启用全局Mock功能"""
#     log.info(f"用户{user.username}(ID:{user.id})尝试启用Mock功能")
#     async with async_session() as session:
#         async with session.begin():
#             try:
#                 log.debug("开始更新Mock全局状态为启用")
#                 result = await MockConfigMapper.update_global_status(
#                     True,
#                     creatorUser=user,
#                     user_id=user.id,
#                     session=session
#                 )
#                 # 刷新缓存
#                 manager = await get_mock_manager(user.id)
#                 manager.user_status.pop(user.id, None)
#                 log.info(f"Mock功能已启用，更新结果: {result}")
#                 return Response.success()
#             except HTTPException as he:
#                 log.error(f"启用Mock功能HTTP异常: {he.detail}")
#                 raise
#             except Exception as e:
#                 log.exception(f"启用Mock功能失败: {e}")
#                 raise HTTPException(
#                     status_code=500,
#                     detail=f"启用Mock功能失败: {str(e)}"
#                 )
async def enable_mock(user: User = Depends(Authentication())):
    """启用全局Mock功能"""
    log.info(f"用户{user.username}(ID:{user.id})尝试启用Mock功能")
    try:
        async with async_session() as session:
            # 显式开始事务
            async with session.begin():
                # 检查状态
                enabled = await MockConfigMapper.is_mock_enabled(user.id, session)
                if enabled:
                    log.info(f"用户{user.username}的Mock功能已处于启用状态")
                    return Response.success(message="Mock功能已启用")

                # 启用Mock - 确保使用显式更新方法
                await MockConfigMapper.update_global_status(
                    True,
                    creatorUser=user,
                    user_id=user.id,
                    session=session
                )

            # 事务已提交，刷新缓存
            manager = await get_mock_manager(user.id)
            manager.user_status.pop(user.id, None)
            return Response.success()
    except HTTPException as he:
        log.error(f"启用Mock功能HTTP异常: {he.detail}")
        raise he
    except Exception as e:
        log.exception(f"启用Mock功能失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"启用Mock功能失败: {str(e)}"
        )

@router.post("/disable",
            description="禁用Mock功能",
            responses={
                500: {"description": "服务器内部错误"}
            })
async def disable_mock(user: User = Depends(Authentication())):
    """禁用全局Mock功能"""
    log.info(f"用户{user.username}(ID:{user.id})尝试禁用Mock功能")
    try:
        async with async_session() as session:
            # 使用显式事务管理
            async with session.begin():
                log.debug("开始更新Mock全局状态为禁用")

                # 更新数据库状态
                result = await MockConfigMapper.update_global_status(
                    False,
                    creatorUser=user,
                    user_id=user.id,
                    session=session
                )

                log.info(f"Mock功能禁用，更新结果: {result}")

                # 确保提交事务（begin()上下文管理器会自动提交）

            # 事务提交后刷新缓存
            manager = await get_mock_manager(user.id)
            manager.user_rules.pop(user.id, None)
            manager.user_status.pop(user.id, None)

            log.info(f"Mock功能已禁用，清除缓存完成")
            return Response.success()
    except HTTPException as he:
        log.error(f"禁用Mock功能HTTP异常: {he.detail}")
        raise
    except Exception as e:
        log.exception(f"禁用Mock功能失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"禁用Mock功能失败: {str(e)}"
        )

@router.get("/status",
           description="获取Mock状态",
           responses={
               500: {"description": "服务器内部错误"}
           })
async def get_mock_status(user: User = Depends(Authentication())):
    """获取Mock功能状态"""
    try:
        # enabled = await MockConfigMapper.is_mock_enabled(user.id)
        # return Response.success({"enabled": enabled})
        async with async_session() as session:
            enabled = await MockConfigMapper.is_mock_enabled(user.id, session)
            return Response.success({
                "enabled": enabled,
                "user_id": user.id,
                "username": user.username
            })
    except Exception as e:
        log.error(f"获取Mock状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取Mock状态失败")

@router.post("/link",
            description="关联已有接口",
            responses={
                404: {"description": "接口不存在"},
                500: {"description": "服务器内部错误"}
            })
async def link_interface(
    data: LinkInterfaceSchema,
    user: User = Depends(Authentication())
):
    """关联已有接口到Mock规则"""
    try:
        from app.mapper.interface.interfaceMapper import InterfaceMapper
        interface = await InterfaceMapper.get_by_id(data.interface_id)
        if not interface:
            raise HTTPException(status_code=404, detail="接口不存在")

        await MockRuleMapper.save(
            path=data.path,
            method=data.method,
            interface_id=data.interface_id,
            status_code=200,
            creator=user.id,
            creatorName=user.username
        )
        return Response.success()
    except Exception as e:
        log.error(f"关联接口失败: {e}")
        raise HTTPException(status_code=500, detail="关联接口失败")

class ImportMockSchema(BaseModel):
    """导入Mock规则请求体"""
    file_type: str = Field("json", description="文件类型(json/yaml)")
    override: bool = Field(False, description="是否覆盖现有规则")

@router.post("/import",
            description="导入Mock规则",
            responses={
                400: {"description": "文件格式错误"},
                500: {"description": "导入失败"}
            })
async def import_mock_rules(
    file_type: str = Form(...),
    override: bool = Form(False),
    file: UploadFile = File(...),
    _: User = Depends(Authentication())
):
    """导入Mock规则"""
    try:
        content = await file.read()
        rules = FileManager.parse_mock_file(content, file_type)

        if override:
            await MockRuleMapper.delete_all()

        for rule in rules:
            await MockRuleMapper.save(**rule)

        return Response.success(data={"message": f"成功导入{len(rules)}条规则"})
    except Exception as e:
        log.error(f"导入Mock规则失败: {e}")
        raise HTTPException(status_code=500, detail="导入Mock规则失败")

@router.get("/export",
           description="导出Mock规则",
           responses={
               500: {"description": "导出失败"}
           })
async def export_mock_rules(
    file_type: str = "json",
    _: User = Depends(Authentication())
):
    """导出Mock规则"""
    try:
        rules = await MockRuleMapper.query_all()
        export_data = [rule.to_dict() for rule in rules]

        content = FileManager.generate_mock_file(export_data, file_type)
        media_type = "application/json" if file_type == "json" else "text/yaml"
        file_name = f"mock_rules.{file_type}"

        return FastResponse(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except Exception as e:
        log.error(f"导出Mock规则失败: {e}")
        raise HTTPException(status_code=500, detail="导出Mock规则失败")

@router.get("/interfaces",
           description="获取所有接口的mock规则",
           responses={
               500: {"description": "服务器内部错误"}
           })
async def get_mock_interfaces(_: User = Depends(Authentication())):
    """获取所有接口的mock规则"""
    try:
        rules = await MockRuleMapper.query_all()
        return Response.success([rule.to_dict() for rule in rules])
    except Exception as e:
        log.error(f"获取mock接口列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取mock接口列表失败")

@router.api_route("/{full_path:path}",
                 methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                 include_in_schema=False)
async def mock_endpoint(full_path: str, request: Request, user: User = Depends(Authentication())):
    """Mock接口端点"""
    # 检查mock请求头
    if request.headers.get("X-Mock-Request", "").lower() != "true":
        return FastResponse(
            status_code=404,
            content=json.dumps({
                "code": 404,
                "message": "非Mock请求",
                "suggestion": "如需Mock请求，请添加X-Mock-Request: true请求头"
            }),
            media_type="application/json"
        )

    try:
        method = request.method
        log.info(f"Mock端点接收请求: {method} {full_path}")

        async with async_session() as session:
            manager = await get_mock_manager(user.id, session)
            response = await manager.mock_response(full_path, method, user.id, session)

            if response is None:
                log.warning(f"未找到匹配的Mock规则: {method} {full_path}")
                return FastResponse(
                    status_code=404,
                    content=json.dumps({
                        "code": 404,
                        "message": f"未找到Mock规则: {full_path}",
                        "suggestion": "请检查路径和方法是否正确"
                    }),
                    media_type="application/json"
                )

            return response

    except Exception as e:
        log.exception(f"Mock处理失败: {str(e)}")
        return FastResponse(
            status_code=500,
            content=json.dumps({"error": str(e)})
        )