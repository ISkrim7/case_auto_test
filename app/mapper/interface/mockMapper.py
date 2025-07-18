#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2024/11/20
# @Author : Zulu
# @File : mockMapper
# @Software: PyCharm
# @Desc: Mock功能数据访问层

from typing import List, Dict, Optional, Sequence, Any
from fastapi.exceptions import HTTPException
from sqlalchemy import select, and_, update, delete, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.interface.mockModel import MockRuleModel, MockConfigModel
from app.mapper import Mapper
from app.model import async_session
from app.model.base import User
from utils import MyLoguru, log
from app.schema import PageSchema
from app.exception import NotFind

class MockRuleMapper(Mapper):
    """Mock规则数据访问"""
    __model__ = MockRuleModel

    @classmethod
    async def get_by_interface(cls, interface_id: int, session: AsyncSession = None) -> List[MockRuleModel]:
        """根据接口ID获取mock规则"""
        query = select(MockRuleModel).where(MockRuleModel.interface_id == interface_id)
        query = query.with_only_columns(
            MockRuleModel.interface_id,
            MockRuleModel.path,
            MockRuleModel.mockname,
            MockRuleModel.method,
            MockRuleModel.status_code,
            MockRuleModel.response,
            MockRuleModel.delay,
            MockRuleModel.enable,
            MockRuleModel.description,
            MockRuleModel.creator,
            MockRuleModel.creatorName,
            MockRuleModel.create_time,
            MockRuleModel.update_time,
            MockRuleModel.headers,
            MockRuleModel.cookies,
            MockRuleModel.content_type,
            MockRuleModel.script,
            MockRuleModel.id,
            MockRuleModel.uid
        )
        if not session:
            async with async_session() as session:
                async with session.begin():
                    result = await session.execute(query)
                    return result.scalars().all()
        result = await session.execute(query)
        return result.scalars().all()

    # @classmethod
    # async def get_by_id(cls, rule_id: int, session: AsyncSession = None) -> Optional[MockRuleModel]:
    #     """
    #     根据ID获取mock规则详情
    #     :param rule_id: 规则ID
    #     :param session: 可选数据库会话
    #     :return: MockRuleModel对象或None
    #     """
    #     try:
    #         query = select(MockRuleModel).where(MockRuleModel.id == rule_id)
    #         if not session:
    #             async with async_session() as session:
    #                 async with session.begin():
    #                     result = await session.execute(query)
    #                     return result.scalar_one_or_none()
    #         result = await session.execute(query)
    #         return result.scalar_one_or_none()
    #     except Exception as e:
    #         log.exception(f"根据ID查询mock规则失败: {e}")
    #         raise
    @classmethod
    async def get_by_id(
            cls,
            rule_id: int,
            user_id: int,
            session: AsyncSession = None,
            raise_error: bool = True,
            **kwargs
    ) -> Optional[MockRuleModel]:

        """
        根据ID获取Mock规则详情（重构版）

        优化点：
        1. 更清晰的错误处理逻辑
        2. 支持可选的外部会话管理
        3. 添加raise_error参数控制是否抛出异常
        4. 更完善的日志记录
        5. 确保资源安全释放
        """
        # # 验证输入参数
        # if not isinstance(rule_id, int) or rule_id <= 0:
        #     error_msg = f"无效的规则ID: {rule_id} (必须是正整数)"
        #     log.error(error_msg)
        #     if raise_error:
        #         raise ValueError(error_msg)
        #     return None
        #
        # try:
        #     # 构建查询
        #     query = select(MockRuleModel).where(
        #         MockRuleModel.id == rule_id,
        #         MockRuleModel.user_id == user_id
        #     )
        #
        #     # 使用外部会话或创建新会话
        #     if session:
        #         result = await session.execute(query)
        #         rule = result.scalar_one_or_none()
        #     else:
        #         async with async_session() as new_session:
        #             async with new_session.begin():
        #                 result = await new_session.execute(query)
        #                 rule = result.scalar_one_or_none()
        #
        #     # 处理查询结果
        #     if not rule and raise_error:
        #         error_msg = f"未找到ID为 {rule_id} 的Mock规则"
        #         log.warning(error_msg)
        #         raise NotFind(error_msg)
        #
        #     return rule
        #
        # except NotFind as nf:
        #     # 已处理的未找到异常
        #     if raise_error:
        #         raise nf
        #     return None
        """安全获取规则方法"""
        try:
            # 验证输入参数
            if not isinstance(rule_id, int) or rule_id <= 0:
                raise ValueError("规则ID必须为正整数")

            # 构建安全查询
            query = select(MockRuleModel).where(
                MockRuleModel.id == rule_id,
                MockRuleModel.user_id == user_id  # 用户过滤
            )

            result = await session.execute(query)
            rule = result.scalars().first()

            if not rule and raise_error:
                raise NotFind(f"未找到ID为 {rule_id} 的Mock规则")

            return rule

        except NotFind as nf:
            if raise_error:
                raise nf
            return None

        except Exception as e:
            log.error(f"获取Mock规则失败: {str(e)}")
            if raise_error:
                raise HTTPException(
                    status_code=500,
                    detail="获取规则详情失败"
                )
            return None

    @classmethod
    async def enable_for_interface(cls, interface_id: int, enable: bool = True, session: AsyncSession = None) -> int:
        """启用/禁用接口的mock规则"""
        return await cls.update_by(interface_id=interface_id, values={"enable": enable}, session=session)

    @classmethod
    async def get_active_rules(cls,user_id: int, session: AsyncSession = None) -> List[MockRuleModel]:
        # """获取指定用户启用的mock规则"""
        # query = select(MockRuleModel).where(
        #     MockRuleModel.enable == True,
        #     MockRuleModel.user_id == user_id  # 按用户过滤
        # )
        # """获取所有启用的mock规则"""
        # #query = select(MockRuleModel).where(MockRuleModel.enable == True)
        # query = query.with_only_columns(
        #     MockRuleModel.interface_id,
        #     MockRuleModel.path,
        #     MockRuleModel.mockname,
        #     MockRuleModel.method,
        #     MockRuleModel.status_code,
        #     MockRuleModel.response,
        #     MockRuleModel.delay,
        #     MockRuleModel.enable,
        #     MockRuleModel.description,
        #     MockRuleModel.creator,
        #     MockRuleModel.creatorName,
        #     MockRuleModel.create_time,
        #     MockRuleModel.update_time,
        #     MockRuleModel.headers,
        #     MockRuleModel.cookies,
        #     MockRuleModel.content_type,
        #     MockRuleModel.script,
        #     MockRuleModel.id,
        #     MockRuleModel.uid
        # )
        # if not session:
        #     async with async_session() as session:
        #         async with session.begin():
        #             result = await session.execute(query)
        #             return result.scalars().all()
        # result = await session.execute(query)
        # return result.scalars().all()
        """可靠获取用户启用的mock规则"""
        try:
            log.debug(f"获取用户{user_id}启用的Mock规则")
            query = select(MockRuleModel).where(
                MockRuleModel.enable == True,
                MockRuleModel.user_id == user_id
            )

            result = await session.execute(query)
            rules = result.scalars().all()

            # 验证结果类型
            if rules and not isinstance(rules[0], MockRuleModel):
                log.error(f"返回结果类型错误: {type(rules[0])}")
                raise TypeError("查询结果不是MockRuleModel实例")

            log.info(f"找到{len(rules)}条启用的Mock规则")
            return rules

        except Exception as e:
            log.exception(f"获取启用的Mock规则失败: {str(e)}")
            return []

    @classmethod
    async def page_query(
        cls,
        user_id: int,  # 新增用户ID参数
        current: int = 1,
        pageSize: int = 10,
        path: Optional[str] = None,
        mockname: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        enable: Optional[bool] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """分页查询mock规则"""
        #conditions = []
        conditions = [MockRuleModel.user_id == user_id]  # 用户过滤
        if path:
            conditions.append(MockRuleModel.path.like(f"%{path}%"))
        if mockname:
            conditions.append(MockRuleModel.mockname.like(f"%{mockname}%"))
        if method:
            conditions.append(MockRuleModel.method == method.upper())
        if status_code:
            conditions.append(MockRuleModel.status_code == status_code)
        if enable is not None:
            conditions.append(MockRuleModel.enable == enable)

        query = select(MockRuleModel).where(and_(*conditions)) if conditions else select(MockRuleModel)
        if not session:
            async with async_session() as session:
                async with session.begin():
                    return await cls._do_page_query(session, query, current, pageSize)
        return await cls._do_page_query(session, query, current, pageSize)

    @classmethod
    async def _execute_page_query(
        cls,
        query,
        current: int,
        pageSize: int,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """执行分页查询"""
        if not session:
            async with async_session() as session:
                async with session.begin():
                    return await cls._do_page_query(session, query, current, pageSize)
        return await cls._do_page_query(session, query, current, pageSize)

    @classmethod
    async def _do_page_query(
        cls,
        session: AsyncSession,
        query,
        current: int,
        pageSize: int
    ) -> Dict[str, Any]:
        """实际执行分页查询"""
        # 获取总数
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        offset = (current - 1) * pageSize

        # 执行分页查询并转换为字典
        result = await session.execute(query.limit(pageSize).offset(offset))
        items = result.scalars().all()

        # 在Session上下文中将对象转换为字典
        item_dicts = [item.to_dict() for item in items] if items else []

        return {
            "items": item_dicts,
            "total": total,
            "current": current,
            "pageSize": pageSize
        }
    @classmethod
    async def get_by_path_method(
            cls,
            path: str,
            method: str,
            user_id: int,  # 新增用户ID参数
            session: AsyncSession = None
    ) -> Optional[MockRuleModel]:
        """
        根据路径和方法获取mock规则
        :param path: 接口路径
        :param method: 请求方法
        :param session: 数据库会话
        :return: MockRuleModel对象或None
        """
        try:
            query = select(MockRuleModel).where(
                and_(
                    MockRuleModel.path == path,
                    MockRuleModel.method == method.upper(),
                    MockRuleModel.user_id == user_id  # 添加用户过滤
                )
            )

            # if session:
            #     result = await session.execute(query)
            #     return result.scalar_one_or_none()
            # else:
            #     async with async_session() as new_session:
            #         async with new_session.begin():
            #             result = await new_session.execute(query)
            #             return result.scalar_one_or_none()
            # 直接使用传入的会话执行查询
            result = await session.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            log.exception(f"根据路径和方法查询mock规则失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"查询Mock规则失败: {str(e)}"
            )

    @classmethod
    async def save(
        cls,
        path: str,
        method: str,
        status_code: int,
        user_id: int,
        mockname: Optional[str] = None,
        response: Optional[dict] = None,
        delay: Optional[float] = None,
        description: Optional[str] = None,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
        content_type: Optional[str] = None,
        params: Optional[dict] = None,
        request_headers: Optional[dict] = None,
        body_type: int = 0,
        raw_type: Optional[str] = None,
        body: Optional[dict] = None,
        data: Optional[dict] = None,
        script: Optional[str] = None,
        interface_id: Optional[int] = None,
        creator: Optional[int] = None,
        creatorName: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> MockRuleModel:
        """保存mock规则
        优化点：
        1. 增加path格式校验
        2. 增强path去重逻辑（统一转换为小写比较）
        3. 使用数据库事务确保并发安全
        4. 修复Session绑定问题
        """
        try:
            # # 校验path格式
            # if not path or not path.startswith('/'):
            #     raise ValueError("path必须以/开头且不能为空")
            #
            # # 统一转换为小写比较路径和方法，避免大小写不一致导致的重复
            # normalized_path = path.lower()
            # normalized_method = method.lower()
            #
            # # 检查是否已存在相同路径和方法的规则
            # if session:
            #     existing_rule = await cls.get_by_path_method(path, method, session)
            # else:
            #     async with async_session() as temp_session:
            #         existing_rule = await cls.get_by_path_method(path, method, temp_session)
            #
            # if existing_rule:
            #     # 如果规则已存在，直接返回友好错误
            #     raise HTTPException(
            #         status_code=409,
            #         detail=f"该路径({path})和方法({method})的Mock规则已存在，请勿重复创建"
            #     )
            #
            # # 准备创建数据
            # kwargs = {
            #     "path": path,
            #     "mockname": mockname,
            #     "method": method,
            #     "status_code": status_code,
            #     "response": response,
            #     "delay": delay,
            #     "description": description,
            #     "headers": headers,
            #     "cookies": cookies,
            #     "content_type": content_type,
            #     "script": script,
            #     "interface_id": interface_id,
            #     "user_id": user_id,
            #     "creator": creator,
            #     "creatorName": creatorName
            # }
            #
            # # 使用事务确保创建操作的原子性
            # if session:
            #     return await cls.save_no_session(session=session, **kwargs)
            # else:
            #     async with async_session() as temp_session:
            #         async with temp_session.begin():
            #             return await cls.save_no_session(session=temp_session, **kwargs)
            # 检查是否已存在相同规则
            existing_rule = await cls.get_by_path_method(
                path=path,
                method=method,
                user_id=user_id,
                session=session  # 传递同一个会话
            )

            if existing_rule:
                raise HTTPException(
                    status_code=409,
                    detail=f"该路径({path})和方法({method})的Mock规则已存在"
                )
            if not path.startswith('/'):
                path = '/' + path

            # 移除结尾斜杠
            path = path.rstrip('/')
            # 创建新规则
            rule = MockRuleModel(
                user_id=user_id,
                path=path,
                method=method.upper(),
                status_code=status_code,
                mockname=mockname,
                response=response,
                #delay=int(delay * 1000) if delay else None,
                delay=int(delay) if delay else None,
                description=description,
                headers=headers,
                cookies=cookies,
                content_type=content_type,
                params=params,
                request_headers=request_headers,
                body_type=body_type,
                raw_type=raw_type,
                body=body,
                data=data,
                script=script,
                interface_id=interface_id,
                creator=creator,
                creatorName=creatorName
            )

            session.add(rule)
            await session.flush()  # 刷新但不提交
            await session.refresh(rule)  # 刷新获取ID等字段

            return rule

        except HTTPException:
            raise  # 直接抛出已有的HTTPException
        except ValueError as ve:
            log.error(f"参数验证失败: {ve}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            log.exception(f"保存mock规则失败: {e}")
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail=f"该路径({path})和方法({method})的Mock规则已存在，请勿重复创建"
                )
            raise HTTPException(
                status_code=500,
                detail=f"保存Mock规则失败: {str(e)}"
            )

    @classmethod
    async def remove_by_interface(cls, interface_id: int, session: AsyncSession = None):
        """根据接口ID删除mock规则"""
        try:
            if session:
                await session.execute(delete(MockRuleModel).where(MockRuleModel.interface_id == interface_id))
            else:
                async with async_session() as session:
                    async with session.begin():
                        await session.execute(delete(MockRuleModel).where(MockRuleModel.interface_id == interface_id))
        except Exception as e:
            log.exception(f"删除mock规则失败: {e}")
            raise

    @classmethod
    async def remove_by_id(cls, rule_id: int, user_id: int, session: AsyncSession = None):
        """根据规则ID删除mock规则"""
        where_conditions = [
            MockRuleModel.id == rule_id,
            MockRuleModel.user_id == user_id
        ]
        try:
            # if session:
            #     await session.execute(delete(MockRuleModel).where(MockRuleModel.id == rule_id))
            # else:
            #     async with async_session() as session:
            #         async with session.begin():
            #             await session.execute(delete(MockRuleModel).where(MockRuleModel.id == rule_id))
            # 使用传入的会话执行删除操作
            await session.execute(
                delete(MockRuleModel).where(and_(*where_conditions))
            )
            return True
        except Exception as e:
            log.exception(f"根据ID删除mock规则失败: {e}")
            raise

    @classmethod
    async def update_by_id(
        cls,
        rule_id: int,
        values: dict,
        user_id: int,  # 新增用户ID参数
        session: AsyncSession = None
    ) -> int:
        # """
        # 根据规则ID更新mock规则
        # :param rule_id: 规则ID
        # :param values: 更新字段字典
        # :param session: 可选数据库会话
        # :return: 影响的行数
        # """
        # where_conditions = [
        #     MockRuleModel.id == rule_id,
        #     MockRuleModel.user_id == user_id
        # ]
        # try:
        #     if not values:
        #         return 0
        #
        #     if session:
        #         # result = await session.execute(
        #         #     update(MockRuleModel)
        #         #     .where(MockRuleModel.id == rule_id)
        #         #     .values(**values)
        #         # )
        #         result = await session.execute(
        #             update(MockRuleModel)
        #             .where(and_(*where_conditions))
        #             .values(**values)
        #         )
        #         return result.rowcount
        #     else:
        #         async with async_session() as session:
        #             async with session.begin():
        #                 result = await session.execute(
        #                     update(MockRuleModel)
        #                     .where(MockRuleModel.id == rule_id)
        #                     .values(**values)
        #                 )
        #                 return result.rowcount
        try:
            # 详细日志
            log.debug(f"更新规则ID={rule_id}, 用户ID={user_id}, 值={values}")

            # 准备更新条件
            where_conditions = [
                MockRuleModel.id == rule_id,
                MockRuleModel.user_id == user_id
            ]

            if not values:
                log.warning("更新值为空，跳过操作")
                return 0

            # 执行更新
            stmt = update(MockRuleModel).where(and_(*where_conditions)).values(**values)
            result = await session.execute(stmt)
            affected_rows = result.rowcount

            if affected_rows == 0:
                log.error(f"更新失败: 规则ID={rule_id} 用户ID={user_id} 未匹配到记录")
            else:
                log.info(f"成功更新规则: ID={rule_id}, 影响行数={affected_rows}")

            return affected_rows
        except Exception as e:
            log.exception(f"更新规则失败: ID={rule_id}, 错误={str(e)}")
            raise

class MockConfigMapper(Mapper):
    """Mock配置数据访问"""
    __model__ = MockConfigModel

    @classmethod
    async def get_config(cls, name: str, user_id: int,session: AsyncSession = None) -> Optional[MockConfigModel]:
        """获取用户的配置项"""
        query = select(MockConfigModel).where(
            MockConfigModel.name == name,
            MockConfigModel.user_id == user_id
        )
        """获取配置项"""
        return await cls.get_by(name=name, session=session)

    @classmethod
    async def set_config(cls, name: str, value: str, creatorUser: User, user_id: int, session: AsyncSession = None) -> int:
        """设置配置项"""
        try:
            # config = await cls.get_by(name=name, user_id=user_id, session=session)
            # if config:
            #     # return await cls.update_by_id(
            #     #     id=config.id,
            #     #     values={"value": value},
            #     #     updateUser=creatorUser,
            #     #     session=session
            #     # )
            #     # 更新现有配置
            #     # await session.execute(
            #     #     update(MockConfigModel)
            #     #     .where(
            #     #         MockConfigModel.id == config.id,
            #     #         MockConfigModel.user_id == user_id
            #     #     )
            #     #     .values(value=value)
            #     # )
            #     # return 1
            #     # 更新现有配置
            #     config.value = value
            #     session.add(config)
            #     return 1
            # else:
            #     # if session:
            #     #     return await cls.save(creatorUser=creatorUser, session=session, name=name, value=value)
            #     # else:
            #     #     async with async_session() as new_session:
            #     #         async with new_session.begin():
            #     #             return await cls.save(creatorUser=creatorUser, session=new_session, name=name, value=value)
            #     # 创建新配置
            #     new_config = MockConfigModel(
            #         user_id=user_id,
            #         name=name,
            #         value=value,
            #         description="用户Mock配置",
            #         creator=creatorUser.id,          # 使用正确字段名
            #         creatorName=creatorUser.username  # 使用正确字段名
            #     )
            #     session.add(new_config)
            #     return 1
            # 使用更可靠的查询方法
            query = select(MockConfigModel).where(
                MockConfigModel.name == name,
                MockConfigModel.user_id == user_id
            )
            result = await session.execute(query)
            config = result.scalars().first()

            if config:
                # 更新现有配置
                config.value = value
                # session.add(config)
                # await session.commit()  # 确保事务提交
                # return 1
            else:
                # 创建新配置
                new_config = MockConfigModel(
                    user_id=user_id,
                    name=name,
                    value=value,
                    description="用户Mock配置",
                    creator=creatorUser.id,
                    creatorName=creatorUser.username
                )
                session.add(new_config)
                # await session.commit()  # 确保事务提交
            return 1
        except Exception as e:
            log.exception(f"设置配置项失败: {e}")
            # 添加唯一约束冲突的专门处理
            if "unique constraint" in str(e).lower() or "duplicate entry" in str(e).lower():
                raise HTTPException(
                    status_code=409,
                    detail="配置项已存在"
                )
            raise

    @classmethod
    async def is_mock_enabled(cls, user_id: int, session: AsyncSession = None) -> bool:
        """检查全局mock是否启用"""
        if session is None:
            log.error("检查Mock启用状态失败: session参数不能为None")
            return False

        try:
            query = select(MockConfigModel).where(
                MockConfigModel.name == "mock_enabled",
                MockConfigModel.user_id == user_id
            )
            result = await session.execute(query)
            config = result.scalars().first()

            if config:
                log.debug(f"用户{user_id}的Mock状态: {config.value}")
                return config.value.lower() == "true"
            log.debug(f"用户{user_id}没有Mock配置记录")
            return False
        except Exception as e:
            log.error(f"检查Mock启用状态失败: {e}")
            return False

    @classmethod
    async def init_default_configs(cls, session: AsyncSession = None):
        """初始化默认配置"""
        try:
            if session:
                for config in MockConfigModel.get_default_configs():
                    exists = await session.scalar(
                        select(MockConfigModel).where(
                            MockConfigModel.name == config["name"]
                        )
                    )
                    if not exists:
                        await cls.save(session=session, **config)
            else:
                async with async_session() as session:
                    async with session.begin():
                        for config in MockConfigModel.get_default_configs():
                            exists = await session.scalar(
                                select(MockConfigModel).where(
                                    MockConfigModel.name == config["name"]
                                )
                            )
                            if not exists:
                                await cls.save(session=session, **config)
        except Exception as e:
            log.exception(f"初始化mock配置失败: {e}")
            raise

    @classmethod
    async def update_global_status(cls, enabled: bool, creatorUser: User, user_id: int, session: AsyncSession = None):
        """更新全局mock状态"""
        try:
            # return await cls.set_config(
            #     session=session,
            #     name="mock_enabled",
            #     user_id=user_id,
            #     value=str(enabled).lower(),
            #     creatorUser=creatorUser
            # )
            # 详细日志记录输入参数
            log.debug(f"更新用户{user_id}的Mock状态为{enabled}")

            # 查询现有配置
            query = select(MockConfigModel).where(
                MockConfigModel.name == "mock_enabled",
                MockConfigModel.user_id == user_id
            )
            result = await session.execute(query)
            config = result.scalars().first()

            # 存在则更新，不存在则创建
            if config:
                log.info(f"找到现有配置: ID={config.id}")
                config.value = str(enabled).lower()
                log.info(f"更新配置值: {config.value}")
            else:
                log.warning(f"用户{user_id}无配置记录，创建新配置")
                config = MockConfigModel(
                    user_id=user_id,
                    name="mock_enabled",
                    value=str(enabled).lower(),
                    description="用户Mock配置",
                    creator=creatorUser.id,
                    creatorName=creatorUser.username
                )
                session.add(config)
                log.info(f"已创建新配置: {config}")

            # 显式刷新以捕获任何错误
            await session.flush()

            # 验证更新后的值
            await session.refresh(config)
            log.info(f"更新后配置值: {config.value}")

            return True
        except Exception as e:
            # log.exception(f"更新全局mock状态失败: enabled={enabled}, user_id={user_id}, error={str(e)}")
            # raise HTTPException(
            #     status_code=500,
            #     detail=f"更新全局mock状态失败: {str(e)}"
            # )
            log.exception(f"更新全局mock状态失败: {str(e)}")
            # 添加详细错误处理
            if "unique constraint" in str(e).lower():
                raise HTTPException(
                    status_code=409,
                    detail="配置项冲突"
                )
            elif "integrity" in str(e).lower():
                raise HTTPException(
                    status_code=400,
                    detail="数据完整性错误"
                )
            raise HTTPException(
                status_code=500,
                detail=f"更新状态失败: {str(e)}"
            )