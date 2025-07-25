
from app.mapper import Mapper
from app.model.interface.interfaceGlobal import  InterfaceGlobalHeader, InterfaceGlobalFunc




class InterfaceGlobalHeaderMapper(Mapper):
    __model__ = InterfaceGlobalHeader


class InterfaceGlobalFuncMapper(Mapper):
    __model__ = InterfaceGlobalFunc


__all__ = [
    "InterfaceGlobalHeaderMapper",
    "InterfaceGlobalFuncMapper"
]
