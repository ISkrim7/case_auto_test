from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper import Mapper
from app.model import async_session
from app.model.interface import InterfaceGroupModel, group_api_association, InterfaceModel
from utils import log


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
                    group: InterfaceGroupModel = cls.get_by_id(ident=groupId, session=session)
                    group.api_num += 1
                    last_index = await get_last_index(session=session, groupId=groupId)
                    await session.execute(
                        group_api_association.insert().values(
                            api_group_id=groupId,
                            api_id=apiId,
                            step_order=last_index + 1
                        )
                    )
        except Exception as e:
            raise e

    @classmethod
    async def association_common_apis(cls, groupId: int, apis: List[int]):
        """
        关联 common api
        :param groupId:
        :param apis:
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    group: InterfaceGroupModel = cls.get_by_id(ident=groupId, session=session)
                    group.api_num = len(apis)
                    last_index = await get_last_index(session=session, groupId=groupId)
                    for index, apiId in enumerate(apis, start=last_index + 1):
                        await session.execute(
                            group_api_association.insert().values(
                                api_group_id=groupId,
                                api_id=apiId,
                                step_order=index
                            )
                        )

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
                async with session.begin():
                    result = await session.execute(
                        select(InterfaceModel).join(
                            group_api_association,
                            group_api_association.c.api_id == InterfaceModel.id
                        ).where(
                            group_api_association.c.api_group_id == groupId
                        ).order_by(group_api_association.c.step_order)
                    )
                    apis = result.all()
                    return apis
        except Exception as e:
            raise e
