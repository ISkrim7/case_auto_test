from typing import List, Mapping, Any, Dict, Callable
import re,json

from jsonpath import jsonpath

from enums import InterfaceExtractTargetVariablesEnum
from httpx import Response

from enums.CaseEnum import ExtraEnum
from utils import JsonExtract, log


class ExecResponseExtract:
    """
    接口 响应提取
    """

    def __init__(self, response: Response = None):
        self.response = response
        self.variables = {}

    async def __call__(self, extracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        :param extracts:
        :return: 处理后的extracts列表，可能包含多个值
        """
        log.debug(f"原始提取参数:{extracts}")
        handlers = {
            InterfaceExtractTargetVariablesEnum.ResponseJsonExtract: self._handle_response_json_extract,
            InterfaceExtractTargetVariablesEnum.ResponseHeaderExtract: self._handle_response_header_extract,
            InterfaceExtractTargetVariablesEnum.RequestCookieExtract: self._handle_request_cookie_extract,
            InterfaceExtractTargetVariablesEnum.ResponseTextExtract: self._handle_response_text_extract,
        }

        processed_extracts = []
        for extract in extracts:
            try:
                target = int(extract.get("target", 0))
                handler: Callable = handlers.get(target)
                if handler:
                    result = await handler(extract)
                    # 处理多值情况
                    if isinstance(result, list):
                        log.info(f"提取到多个值 - key: {extract.get('key')}, 表达式: {extract.get('value')}, 数量: {len(result)}")
                        for idx, value in enumerate(result):
                            new_extract = extract.copy()
                            new_extract['key'] = f"{extract.get('key')}_{idx+1}"
                            new_extract['value'] = value
                            processed_extracts.append(new_extract)
                            log.debug(f"值 #{idx+1}: {value}")
                    else:
                        extract['value'] = result
                        processed_extracts.append(extract)
                        log.info(f"提取到单个值 - key: {extract.get('key')}, 值: {result}")
                else:
                    log.warning(f"不支持的提取目标: {target}")
            except KeyError as e:
                log.error(f"提取参数缺少必要键: {e}")
            except Exception as e:
                log.error(f"提取处理错误: {e}")

        log.info(f"最终提取结果: {processed_extracts}")
        return processed_extracts

    async def _handle_response_json_extract(self, extract: Dict[str, Any]) -> Any:
        """处理 ResponseJsonExtract 类型"""
        opt = extract.get("extraOpt", ExtraEnum.JSONPATH)
        try:
            jp = JsonExtract(jsonBody=self.response, expr=extract['value'])
            match opt:
                case ExtraEnum.JMESPATH:
                    return jp.search()
                case ExtraEnum.JSONPATH:
                    # 检查是否包含索引语法 [数字]
                    index_match = re.search(r'\[(\d+)\]$', extract['value'])
                    if index_match:
                        # 提取指定索引的元素
                        idx = int(index_match.group(1))
                        base_expr = extract['value'][:index_match.start()] + '[*]'
                        result = jsonpath(self.response.json(), base_expr)
                        if result and len(result) > idx:
                            return result[idx]
                        return None
                    else:
                        # 默认提取所有或单个元素
                        result = await jp.value()
                        if isinstance(result, list) and "[*]" in extract['value']:
                            return result
                        return result
        except Exception as e:
            log.error(f"Failed to extract JSON value: {e}")
            return None

    async def _handle_response_header_extract(self, extract: Dict[str, Any]) -> Any:
        """处理 ResponseHeaderExtract 类型"""
        try:
            jp = JsonExtract(jsonBody=dict(self.response.headers), expr=extract['value'])
            return await jp.value()
        except Exception as e:
            log.error(f"Failed to extract header value: {e}")
            return None

    async def _handle_request_cookie_extract(self, extract: Dict[str, Any]) -> Any:
        """处理 RequestCookieExtract 类型 """
        log.info(f"RequestCookieExtract ${self.response.request.headers}")
        log.info(f"RequestCookieExtract ${self.response.cookies}")
        return self.response.request.headers.get("cookie", None)

    async def _handle_response_text_extract(self, extract: Dict[str, Any]) -> Any:
        """处理 ResponseTextExtract 类型，统一使用正则表达式处理所有格式响应"""
        try:
            # 统一将响应内容转为文本处理
            response_text = self.response.text
            
            # 对于JSON响应，保持原始JSON结构但转为字符串处理
            content_type = self.response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                try:
                    # 保持JSON结构但转为字符串，确保正则能匹配
                    response_text = json.dumps(self.response.json())
                except ValueError:
                    pass  # 不是有效JSON，保持原样
                    
            # 统一使用正则表达式提取
            match = re.search(extract['value'], response_text)
            return match.group(1) if match else None
            
        except Exception as e:
            log.error(f"Failed to extract text value: {e}")
            return None
