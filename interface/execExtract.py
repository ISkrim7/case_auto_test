from typing import List, Mapping, Any, Dict
from enums import InterfaceExtractTargetVariablesEnum
from httpx import Response

from utils import MyJsonPath


class ExecResponseExtract:

    def __init__(self, response: Response = None):
        self.response = response
        self.variables = {}

    async def __call__(self, extracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        :param extracts:
        :return:
        """
        for extract in extracts:
            match int(extract[InterfaceExtractTargetVariablesEnum.Target]):
                case InterfaceExtractTargetVariablesEnum.ResponseJsonExtract:
                    jp = MyJsonPath(jsonBody=self.response.json(),
                                    expr=extract['value'])
                    value = await jp.value()
                    extract['value'] = value
                case InterfaceExtractTargetVariablesEnum.ResponseHeaderExtract:
                    jp = MyJsonPath(jsonBody=dict(self.response.headers),
                                    expr=extract['value'])
                    value = await jp.value()
                    extract['value'] = value
                case _:
                    continue
        return extracts
