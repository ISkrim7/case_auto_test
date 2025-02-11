from typing import Type, TypeVar

from sqlalchemy import and_, select

from app.exception import NotFind
from app.mapper import Mapper
from app.model import BaseModel, async_session
from app.model.base import User
from app.model.interface import InterfaceVariables
T = TypeVar('T', bound=BaseModel)


class InterfaceVarsMapper(Mapper):
    __model__ = InterfaceVariables

    @classmethod
    async def insert(cls: Type[T], user: User, **kwargs) -> T:
        """
        插入数据
        同一个case 校验 key 唯一
        :param user
        :param case_id
        :param kwargs:
        :return:
        """
        caseId = kwargs.get("case_id")
        try:
            async with async_session() as session:
                async with session.begin():
                    from app.mapper.ui.uiCaseMapper import UICaseMapper
                    await UICaseMapper.get_by_id(ident=caseId, session=session)

                    key_exists = await session.execute(
                        select(InterfaceVariables).where(and_(
                            InterfaceVariables.key == kwargs.get("key"),
                            InterfaceVariables.case_id == caseId
                        ))
                    )
                    if key_exists.scalar():
                        raise NotFind("key 已存在")
                    return await cls.save_no_session(session=session, **kwargs)
        except Exception as e:
            raise e