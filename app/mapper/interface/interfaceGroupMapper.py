from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper import Mapper
from app.model import async_session
from app.model.base import User
from app.model.interface import InterfaceGroupModel, group_api_association, InterfaceModel


async def get_last_index(session: AsyncSession, groupId: int) -> int:
    try:
        sql = (
            select(group_api_association.c.step_order).where(
                group_api_association.c.api_group_id == groupId
            ).order_by(group_api_association.c.step_order.desc()).limit(1)
        )
        result = await session.execute(sql)
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
            select(group_api_association).where(
                and_(
                    group_api_association.c.api_group_id == groupId,
                    group_api_association.c.api_id == apiId
                )
            )
        )
        if result.scalar() is not None:
            return
        await session.execute(
            group_api_association.insert().values(
                api_group_id=groupId,
                api_id=apiId,
                step_order=step_order
            )
        )
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
                    from app.mapper.interface import InterfaceMapper
                    # 复制api 转为私有
                    api = await InterfaceMapper.copy_api(apiId=apiId, creator=cr, is_copy_name=True,
                                                         is_common=False,
                                                         session=session)
                    last_index = await get_last_index(session=session, groupId=groupId)
                    await insert_group_api(session=session, groupId=groupId, apiId=api.id, step_order=last_index + 1)

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
                    group.api_num = len(apiIds)
                    last_index = await get_last_index(session=session, groupId=groupId)
                    for index, apiId in enumerate(apiIds, start=last_index + 1):
                        await insert_group_api(session=session, groupId=groupId, apiId=apiId, step_order=index)

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
                        group_api_association,
                        group_api_association.c.api_id == InterfaceModel.id
                    ).where(
                        group_api_association.c.api_group_id == groupId
                    ).order_by(group_api_association.c.step_order)
                )
                apis = result.scalars().all()
                return apis
        except Exception as e:
            raise e

    @classmethod
    async def remove_api(cls, groupId: int, apiId: int):
        """
        移除关联api
        :param groupId:
        :param apiId:
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    from app.mapper.interface import InterfaceMapper

                    group: InterfaceGroupModel = await cls.get_by_id(ident=groupId, session=session)
                    group.api_num -= 1
                    api: InterfaceModel = await InterfaceMapper.get_by_id(ident=apiId, session=session)
                    await session.execute(
                        group_api_association.delete().where(
                            and_(
                                group_api_association.c.api_group_id == groupId,
                                group_api_association.c.api_id == apiId
                            )
                        )
                    )
                    if not api.is_common:
                        await session.delete(api)
                        await session.flush()

        except Exception as e:
            raise e

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
                            group_api_association.update().where(
                                and_(
                                    group_api_association.c.api_group_id == groupId,
                                    group_api_association.c.api_id == apiId
                                )
                            ).values(
                                step_order=index
                            )
                        )
        except Exception as e:
            raise e
