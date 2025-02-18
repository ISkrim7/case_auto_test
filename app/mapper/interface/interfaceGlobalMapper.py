from app.mapper import Mapper
from app.model.interface.interfaceGlobal import InterfaceGlobalVariable, InterfaceGlobalHeader


class InterfaceGlobalVariableMapper(Mapper):
    __model__ = InterfaceGlobalVariable


class InterfaceGlobalHeaderMapper(Mapper):
    __model__ = InterfaceGlobalHeader