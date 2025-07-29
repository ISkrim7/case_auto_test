from typing import List, Sequence

from sqlalchemy import select, and_, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper import Mapper
from app.model import async_session
from app.model.base import User
from app.model.interface import InterfaceGroupModel, InterfaceModel
from app.model.interface.association import GroupApiAssociation
from utils import log


async def get_last_index(session: AsyncSession, groupId: int) -> int:
    try:
        result = await session.execute((
            select(GroupApiAssociation.step_order).where(
                GroupApiAssociation.api_group_id == groupId
            ).order_by(GroupApiAssociation.step_order.desc()).limit(1)
        ))
        last_step_order = result.scalar()  # Fetch the first (and only) result
        return last_step_order or 0
    except Exception as e:
        raise e


async def insert_group_api(session: AsyncSession, groupId: int, apiId: int, step_order: int):
    """
    插入关联 group step

    """
    try:
        # 检查是否存在相同的 case_id 和 step_id
        result = await session.execute(
            select(GroupApiAssociation).where(
                and_(
                    GroupApiAssociation.api_group_id == groupId,
                    GroupApiAssociation.api_id == apiId
                )
            )
        )
        if result.scalar() is not None:
            return False
        await session.execute(
            insert(GroupApiAssociation).values(
                api_group_id=groupId,
                api_id=apiId,
                step_order=step_order
            )
        )
        return True
    except Exception as e:
        raise e


class InterfaceGroupMapper(Mapper):
    __model__ = InterfaceGroupModel

    @classmethod
    async def association_api(cls, groupId: int, apiId: int):
        """
        组提关联素有用例
        :param groupId:
        :param apiId:
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    group: InterfaceGroupModel = await cls.get_by_id(ident=groupId, session=session)
                    group.api_num += 1
                    last_index = await get_last_index(session=session, groupId=groupId)
                    await insert_group_api(session=session, groupId=groupId, apiId=apiId, step_order=last_index + 1)

        except Exception as e:
            raise e

    @classmethod
    async def copy_group(cls, groupId: int, creator: User):
        async with async_session() as session:
            async with session.begin():
                # 1. 获取原组信息
                original_group: InterfaceGroupModel = await cls.get_by_id(groupId, session)

                # 2. 创建新组（自动生成名称，如 "原组名_副本"）
                new_group = InterfaceGroupModel(
                    name=f"{original_group.name}_副本",
                    description=original_group.description,
                    project_id=original_group.project_id,
                    module_id=original_group.module_id,
                    creator=creator.id,
                    creatorName=creator.username
                )
                session.add(new_group)
                await session.flush()  # 确保生成new_group.id

                # 3. 复制关联的API（示例逻辑）
                original_apis = await session.execute(
                    select(GroupApiAssociation)
                    .where(GroupApiAssociation.api_group_id == groupId)
                    .order_by(GroupApiAssociation.step_order)
                )
                original_apis = original_apis.scalars().all()

                # 将原组的API关联到新组，保持顺序
                for index, assoc in enumerate(original_apis, start=1):
                    await session.execute(
                        insert(GroupApiAssociation).values(
                            api_group_id=new_group.id,
                            api_id=assoc.api_id,
                            step_order=index
                        )
                    )

                # 4. 更新新组的api_num
                new_group.api_num = len(original_apis)

    @classmethod
    async def copy_association_api(cls, groupId: int, apiId: int, cr: User):
        """
        复制api
        :param groupId:
        :param apiId:
        :param cr:
        :return
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    # 添加组对象获取
                    group: InterfaceGroupModel = await cls.get_by_id(ident=groupId, session=session)
                    from app.mapper.interface import InterfaceMapper
                    # 复制api 转为私有
                    api = await InterfaceMapper.copy_api(apiId=apiId, creator=cr, is_copy_name=True,
                                                         is_common=False,
                                                         session=session)
                    last_index = await get_last_index(session=session, groupId=groupId)
                    #await insert_group_api(session=session, groupId=groupId, apiId=api.id, step_order=last_index + 1)
                    # 获取插入结果
                    is_success = await insert_group_api(
                        session=session,
                        groupId=groupId,
                        apiId=api.id,
                        step_order=last_index + 1
                    )
                    # 如果插入成功则自增计数
                    if is_success:
                        group.api_num += 1
        except Exception as e:
            raise e

    @classmethod
    async def association_common_apis(cls, groupId: int, apiIds: List[int]):
        """
        关联 common api
        :param groupId:
        :param apiIds:
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    group: InterfaceGroupModel = await cls.get_by_id(ident=groupId, session=session)
                    last_index = await get_last_index(session=session, groupId=groupId)
                    for index, apiId in enumerate(apiIds, start=last_index + 1):
                        flag = await insert_group_api(session=session, groupId=groupId, apiId=apiId, step_order=index)
                        if flag:
                            group.api_num += 1



        except Exception as e:
            raise e

    @classmethod
    async def query_apis(cls, groupId: int) -> List[InterfaceModel]:
        """
        查询关联api
        :param groupId:
        :return:
        """
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(InterfaceModel).join(
                        GroupApiAssociation,
                        GroupApiAssociation.api_id == InterfaceModel.id
                    ).where(
                        GroupApiAssociation.api_group_id == groupId
                    ).order_by(GroupApiAssociation.step_order)
                )
                apis = result.scalars().all()
                return apis
        except Exception as e:
            raise e

    @classmethod
    async def remove_api(cls, groupId: int, apiId: int) -> tuple[bool, str]:
        """
        移除组内API关联关系(不删除API实体)
        :param groupId: 当前组ID
        :param apiId: 要移除的API ID
        :return: (是否成功, 提示信息)
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    group: InterfaceGroupModel = await cls.get_by_id(ident=groupId, session=session)
                    log.info(f"开始删除组 {groupId} 中的API {apiId}关联")

                    # 检查该API是否被其他组使用
                    stmt = select(GroupApiAssociation).where(
                        GroupApiAssociation.api_id == apiId
                    )
                    result = await session.execute(stmt)
                    associations = result.scalars().all()

                    # 收集其他组的关联信息(仅用于日志)
                    other_groups = []
                    for assoc in associations:
                        if assoc.api_group_id != groupId:
                            other_group = await cls.get_by_id(assoc.api_group_id, session)
                            other_groups.append(f"组ID: {other_group.id}, 组名: {other_group.name}")

                    if other_groups:
                        log.warning(f"API {apiId}还被以下组使用:\n" + "\n".join(other_groups))

                    # 删除当前组的关联记录
                    delete_count = await session.execute(
                        delete(GroupApiAssociation).where(
                            and_(
                                GroupApiAssociation.api_group_id == groupId,
                                GroupApiAssociation.api_id == apiId
                            )
                        )
                    )

                    if delete_count.rowcount == 0:
                        return False, "指定关联不存在"

                    group.api_num -= 1
                    log.info(f"已删除组 {groupId} 中的API {apiId}关联，影响记录数: {delete_count.rowcount}")

                    await session.flush()
                    return True, f"成功从组 {groupId} 中移除API {apiId}关联"

        except Exception as e:
            error_msg = f"删除组 {groupId} 中的API {apiId}关联失败: {str(e)}"
            log.error(error_msg)
            return False, error_msg

    @classmethod
    async def reorder_apis(cls, groupId: int, apiIds: List[int]):
        """
        重新排序
        :param groupId:
        :param apiIds:
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    for index, apiId in enumerate(apiIds, start=1):
                        await session.execute(
                            update(GroupApiAssociation).where(
                                and_(
                                    GroupApiAssociation.api_group_id == groupId,
                                    GroupApiAssociation.api_id == apiId
                                )
                            ).values(
                                step_order=index
                            )
                        )
        except Exception as e:
            raise e

    @staticmethod
    async def set_group_when_api_remove(session: AsyncSession, apiId: int):
        """
        当 api删除
        计算数量
        :param session:
        :param apiId:
        :return:
        """
        try:

            query = await session.scalars(select(InterfaceGroupModel.id).join(
                GroupApiAssociation,
                #GroupApiAssociation.api_id == InterfaceGroupModel.id
                GroupApiAssociation.api_group_id == InterfaceGroupModel.id  # 正确定义外键关系
            ).where(
                GroupApiAssociation.api_id == apiId
            ))
            groups: Sequence[InterfaceGroupModel.id] = query.all()
            log.debug(groups)
            await session.execute(
                update(InterfaceGroupModel).where(
                    InterfaceGroupModel.id.in_(groups)
                ).values(
                    api_num=InterfaceGroupModel.api_num - 1
                )
            )
            await session.execute(
                delete(GroupApiAssociation).where(
                    GroupApiAssociation.api_id == apiId
                )
            )
        except Exception as e:
            log.error(f"更新组引用计数失败: {str(e)}")
            raise e

    @classmethod
    async def remove_group(cls, groupId: int):
        """
        删除逻辑
        公共用例解除关联
        私有api 删除
        :param groupId:
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    group = await cls.get_by_id(groupId, session)
                    # 查询api
                    query = await session.execute(
                        select(InterfaceModel).join(
                            GroupApiAssociation,
                            GroupApiAssociation.api_id == InterfaceModel.id
                        ).where(
                            GroupApiAssociation.api_group_id == groupId
                        )
                    )
                    apis = query.scalars().all()
                    # 删除所有关联
                    await session.execute(
                        delete(GroupApiAssociation).where(
                            GroupApiAssociation.api_group_id == groupId
                        )
                    )
                    # 删除所有非公共API
                    private_apis = [api for api in apis if not api.is_common]
                    for api in private_apis:
                        #await session.delete(api)
                        # 检查该API是否被其他组使用
                        stmt = select(GroupApiAssociation).where(
                            GroupApiAssociation.api_id == api.id
                        )
                        result = await session.execute(stmt)
                        associations = result.scalars().all()
                        if not associations:  # 无其他引用才删除
                            await session.delete(api)
                    await session.delete(group)
        except Exception as e:
            raise e


__all__ = ['InterfaceGroupMapper']