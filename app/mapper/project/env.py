from typing import List
from sqlalchemy import select, and_
from app.mapper import Mapper
from app.model import async_session
from app.model.base import EnvModel


class EnvMapper(Mapper):
    __model__ = EnvModel