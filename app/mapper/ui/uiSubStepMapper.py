from typing import List

from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.mapper import Mapper
from app.model import async_session
from app.model.base import User
from app.model.ui import SubStepModel


class SubStepMapper(Mapper):
    __model__ = SubStepModel

    @classmethod
    async def copy_sub(cls, session: AsyncSession, oldStepId: int, newStepId: int, cr: User):
        try:
            exe = await session.execute(
                select(SubStepModel).where(SubStepModel.stepId == oldStepId)
                .order_by(SubStepModel.order.asc())
            )
            oldSubs = exe.scalars().all()
            for index, old_sub in enumerate(oldSubs, start=1):
                new_sub = old_sub.copy_map
                new_sub['creator'] = cr.id
                new_sub['creatorName'] = cr.username
                new_sub['stepId'] = newStepId
                new_sub['order'] = index
                await cls.save_no_session(session, **new_sub)
        except Exception as e:
            raise e

    @classmethod
    async def add_sub(cls, cr: User, stepId: int, **kwargs):
        try:
            async with async_session() as session:
                async with session.begin():
                    order = await get_order(session, stepId)
                    kwargs["order"] = order
                    kwargs["stepId"] = stepId
                    kwargs['creator'] = cr.id
                    kwargs["creatorName"] = cr.username
                    return await cls.save_no_session(session, **kwargs)
        except Exception as e:
            raise e

    @classmethod
    async def query_by_stepId(cls, stepId):
        try:
            async with async_session() as session:
                exe = await session.execute(
                    select(cls.__model__).where(cls.__model__.stepId == stepId)
                    .order_by(cls.__model__.order.asc())
                )
                datas = exe.scalars().all()
                return datas

        except Exception as e:
            raise e

    @classmethod
    async def reorder_sub_step(cls, stepId: int, subIds: List[int]):
        try:
            async with async_session() as session:
                async with session.begin():
                    for subId, index in enumerate(subIds,start=1):
                        await session.execute(
                            update(cls.__model__).where(
                                and_(cls.__model__.stepId == stepId, cls.__model__.id == subId)
                            ).values(
                                order=index,
                            )
                        )
        except Exception as e:
            raise e


async def get_order(session: AsyncSession, stepId) -> int:
    try:
        res = await session.execute(select(func.count())
                                    .where(SubStepModel.stepId == stepId))
        return res.scalar()
    except Exception as e:
        raise e
