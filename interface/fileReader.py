import asyncio
import json
from json import JSONDecodeError
from typing import List, Dict, Any

from fastapi import UploadFile
from enums import InterfaceUploadEnum
from utils import MyLoguru

log = MyLoguru().get_logger()


class FileReader:

    @staticmethod
    def readFile(file_path: str):
        with open(f'{file_path}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        apis = data.get("apis")
        for i in apis:
            name = i.get("name")
            desc = i.get("description")
            method = i.get("method")
            url = i.get("url")
            print(name, desc, method, url)
            request_body = i.get("request")
            print(request_body)

            headers_parameter = request_body.get("headers", {"parameter": None}).get("parameter")
            # print(headers_parameter)
            if headers_parameter:
                headers = [dict(key=i.get("key") if i.get("key") else None,
                                value=i.get("value") if i.get("value") else None,
                                desc=i.get("description", None)) for i in headers_parameter]
                print(headers)

    @staticmethod
    async def readUploadFile(v: str, file: UploadFile):

        match v:
            case InterfaceUploadEnum.YApi:
                return await FileReader._yapi(file)
            case InterfaceUploadEnum.PostMan:
                pass
            case InterfaceUploadEnum.Swagger:
                pass
            case InterfaceUploadEnum.ApiPost:
                pass

    @staticmethod
    async def _yapi(file: UploadFile) -> List[Dict[str, Any]]:
        """
        解析 YAPI 导出的文件数据，并转换为结构化数据。

        :param file: 上传的文件对象
        :return: 解析后的 YAPI 数据列表
        """
        data = json.loads(await file.read())
        yapi_data = []

        for item in data:
            part_data = {
                'part': item.get("name"),
                'data': []
            }

            item_list = item.get('list', [])
            if item_list:
                # 并发处理每个接口的数据
                part_data['data'] = await asyncio.gather(
                    *(FileReader._get_yapi_data(api_data) for api_data in item_list)
                )

            yapi_data.append(part_data)

        return yapi_data

    @staticmethod
    async def _get_yapi_data(api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单个 API 数据，提取请求信息。

        :param api_data: 单个 API 的原始数据
        :return: 解析后的请求信息
        """
        request_info = {
            'name': api_data.get("title"),
            'method': api_data.get("method"),
            'url': api_data.get("path"),
            'params': api_data.get("req_params", []),
            'headers': api_data.get("req_headers", []),
            'description': api_data.get("desc", ""),
        }

        # 处理请求头
        if api_data.get('req_headers'):
            request_info['headers'] = [
                {
                    'id': header.get('_id'),
                    'key': header.get('name'),
                    'value': header.get('value'),
                    'desc': header.get('desc'),
                }
                for header in api_data.get("req_headers")
            ]

        # 处理查询参数
        if api_data.get('req_query'):
            request_info['params'] = [
                {
                    'id': query.get('_id'),
                    'key': query.get('name'),
                    'value': query.get('value'),
                    'desc': query.get('desc'),
                }
                for query in api_data.get("req_query")
            ]

        # 处理请求体
        req_body_type = api_data.get('req_body_type')
        if req_body_type == "json":
            request_info['body_type'] = 1
            try:
                request_info['body'] = json.loads(api_data.get('res_body', '{}'))
            except JSONDecodeError:
                request_info['body'] = api_data.get('res_body')
        elif req_body_type == "form":
            request_info['body_type'] = 2
            request_info['data'] = api_data.get('req_body_form')
        else:
            request_info['body_type'] = 0

        return request_info