from app.mapper import Mapper
from app.model.interface.interfaceGlobal import InterfaceGlobalVariable, InterfaceGlobalHeader, InterfaceGlobalFunc


class InterfaceGlobalVariableMapper(Mapper):
    __model__ = InterfaceGlobalVariable


class InterfaceGlobalHeaderMapper(Mapper):
    __model__ = InterfaceGlobalHeader


class InterfaceGlobalFuncMapper(Mapper):
    __model__ = InterfaceGlobalFunc


__all__ = [
    "InterfaceGlobalVariableMapper",
    "InterfaceGlobalHeaderMapper",
    "InterfaceGlobalFuncMapper"
]