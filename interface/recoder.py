import json
import mimetypes
from json import JSONDecodeError
from typing import List, Mapping, Dict, Any
from mitmproxy import http
from enums import InterfaceRequestTBodyTypeEnum
from utils import log, rc
from utils import GenerateTools

Headers = List[Dict[str, Any]] | None
Params = List[Dict[str, Any]] | None
Data = List[Dict[str, Any]] | None
valid_extensions = ("js", "css", "ttf", "jpg", "svg", "gif", "png", 'ts')


class Record:
    """
    开始录制
    redis 存储 record_userId: user record info

    mitmproxy
    """
    prefix = "record_"

    @classmethod
    async def start_record(cls, key_name: str, recordInfo: Dict[str, Any]):
        """
        开始录制
        """
        name = Record.prefix + key_name
        key = await rc.check_key_exist(name)
        if key:
            await rc.remove_key(name)
        log.debug(f"start record {name} {recordInfo}")
        for k, v in recordInfo.items():
            if isinstance(v, list):
                recordInfo[k] = json.dumps(v)
        return await rc.h_set(name=name, value=recordInfo)

    @classmethod
    async def clear_record(cls, ip: str, uid: str):
        """
        停止录制
        """
        IP = cls.prefix + ip
        UID = cls.prefix + uid
        await rc.remove_key(IP)
        await rc.remove_key(UID)
        return

    @classmethod
    async def query_record(cls, name: str):
        """
        查询录制
        """
        name = cls.prefix + name
        data = await rc.l_range(name=name)
        datas = [json.loads(i) for i in data]
        log.info(datas)
        return datas


class InterfaceRecoder:

    async def response(self, flow: http.HTTPFlow) -> None:
        """response 响应回调"""
        if flow.request.method.lower() == "options" or any(ext in flow.request.url for ext in valid_extensions):
            return
        _client = await rc.h_get_all("record_" + flow.client_conn.peername[0])

        methods = json.loads(_client['method'])
        if _client and _client["url"] in flow.request.url \
                and flow.request.method.upper() in methods:
            ir = RecordRequest(flow)
            log.debug(ir.map)
            await rc.l_push("record_" + _client['uid'], ir.map)


class RecordRequest:
    uid: str = None
    url: str | None = None
    method: str | None = None
    headers: Headers = None
    params: Params = None
    body: dict | None = None
    data: Data = None
    bodyType: int | None = None
    response: str | None = None

    def __init__(self, flow: http.HTTPFlow) -> None:
        self.flow = flow
        self.url = flow.request.url
        self.method = flow.request.method
        self.set_Headers()
        self.set_Body()
        self.set_response()

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
        requestType = self.flow.request.headers.get("Content-Type")
        log.warning(f"requestType: {requestType}")

        if "json" in requestType:
            return self._is_json()
        if "form" in requestType:
            return self._is_data()
        else:
            return self._is_params()

    def set_response(self):
        content_type = self.flow.response.headers.get("Content-Type", "")
        text = self.flow.response.text if self.flow.response.text else ""

        # 获取字符编码
        content_encoding = self.flow.response.headers.get("Content-Encoding", "utf-8")

        try:
            if "json" in content_type.lower():
                self.response = json.dumps(json.loads(text), indent=4, ensure_ascii=False)
            elif "text" in content_type.lower() or "xml" in content_type.lower():
                self.response = text
            else:
                self.response = self.flow.response.data.decode(content_encoding)
        except (JSONDecodeError, UnicodeDecodeError) as e:
            # 记录日志或采取其他措施
            log.error(f"Error processing response: {e}")
            self.response = text

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
    def map(self) -> str:
        m = dict(
            response=self.response,
            create_time=GenerateTools.getTime(1),
            uid=GenerateTools.uid(),
            url=self.url,
            method=self.method,
            headers=self.headers,
            params=self.params,
            data=self.data,
            body=self.body,
            bodyType=self.bodyType)
        return json.dumps(m, ensure_ascii=False)
