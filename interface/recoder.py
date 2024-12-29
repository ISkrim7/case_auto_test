import json
import mimetypes
from typing import List, Mapping, Dict, Any
from mitmproxy import http
from enums import InterfaceRequestTBodyTypeEnum
from utils import log

Headers = List[Dict[str, Any]] | None
Params = List[Dict[str, Any]] | None
Data = List[Dict[str, Any]] | None


class InterfaceRecoder:

    async def response(self, flow: http.HTTPFlow) -> None:
        """response 响应回调"""
        ir = InterfaceRequest(flow)
        log.error(ir.map)


class InterfaceRequest:
    url: str | None = None
    method: str | None = None
    headers: Headers = None
    params: Params = None
    body: dict | None = None
    data: Data = None
    bodyType: int | None = None

    def __init__(self, flow: http.HTTPFlow) -> None:
        self.flow = flow
        self.url = flow.request.url
        self.method = flow.request.method

        self.set_Headers()
        self.set_Body()

    def set_Headers(self):
        if self.flow.request.headers:
            _headers = dict(self.flow.request.headers)
            self.headers = [dict(key=k, value=v) for k, v in _headers.items()]

    def set_Body(self):
        """
        暂支持
        无body
        json body
        data body
        :return:
        """
        mime_type, _ = mimetypes.guess_type(self.url)  # 结合URL等更多信息辅助判断
        if mime_type == 'application/json':
            return self._is_json()
        elif mime_type == 'application/x-www-form-urlencoded':
            return self._is_data()
        else:
            return self._is_params()

    def _is_json(self):
        try:
            self.bodyType = InterfaceRequestTBodyTypeEnum.Json
            self.body = json.loads(self.flow.request.text)
        except json.decoder.JSONDecodeError as e:
            log.error(e)

    def _is_data(self):
        self.bodyType = InterfaceRequestTBodyTypeEnum.Data
        self.data = self.__parse_kv_text(self.flow.request.text)

    def _is_params(self):
        self.bodyType = InterfaceRequestTBodyTypeEnum.Null
        try:
            query = self.flow.request.query
            self.params = [{"key": k, "value": v} for k, v in dict(query).items()]
        except Exception as e:
            log.error(e)

    @staticmethod
    def __parse_kv_text(text: str):
        """
        将给定的类似 `key=value` 格式用 `&` 连接的文本解析为字典列表，
        每个字典包含 'key' 和 'value' 表示解析后的键值对，并且对键值进行 `unquote` 解引用处理。

        :param text: 待解析的文本，格式如 `key1=value1&key2=value2` 等。
        :return: 解析后的字典列表。
        """
        from urllib.parse import unquote
        pairs = text.split('&')
        result = []
        for pair in pairs:
            key_value = pair.split('=')
            if len(key_value) == 2:
                key = unquote(key_value[0])
                value = unquote(key_value[1])
                result.append({'key': key, 'value': value})
        return result

    @property
    def map(self):
        m = dict(url=self.url,
                 method=self.method,
                 headers=self.headers,
                 params=self.params,
                 data=self.data,
                 body=self.body,
                 bodyType=self.bodyType)
        return m
