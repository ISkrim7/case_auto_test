import json


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


if __name__ == '__main__':
    FileReader.readFile('../cyq的项目.json')
