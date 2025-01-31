from sqlalchemy import select

from app.mapper import Mapper
from app.model import async_session
from app.model.ui.uiConfig import UIConfig


class UIConfigMapper(Mapper):
    __model__ = UIConfig

    @classmethod
    async def config(cls) -> UIConfig:
        try:
            async with async_session() as session:
                exe = await session.execute(
                    select(UIConfig).limit(1)
                )
                return exe.scalar()
        except Exception as e:
            raise e
