import requests


def send():
    url = 'http://127.0.0.1:6006/mini/formDataReq'
    data = requests.post(url=url,
                         data={"username": "admin", "password": "admin"})
    print(data.request.headers)
    print(data.text)


def get_send():
    url = 'http://127.0.0.1:6006/mini/queryUser'
    headers = {"token": "im dsadkjhaskjdhaskjhd"}
    data = requests.get(url=url, params={"username": "admin", "password": "admin"},
                        headers=headers
                        )
    print(data.request.headers)
    print(data.text)


def parse_urlencoded_data(data):
    from urllib.parse import unquote
    result = {}
    pairs = data.split('&')
    for pair in pairs:
        key_value = pair.split('=')
        if len(key_value) == 2:
            key = unquote(key_value[0])
            value = unquote(key_value[1])
            result[key] = value
    print(result)


a = {'url': 'https://sso.bacic5i5j.com/login?service=https://beijing.cbs.bacic5i5j.com/base/cas',
     'method': 'POST',
     'headers': [{'key': 'content-length', 'value': '129'}, {'key': 'cache-control', 'value': 'max-age=0'},
                 {'key': 'sec-ch-ua', 'value': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"'},
                 {'key': 'sec-ch-ua-mobile', 'value': '?0'}, {'key': 'sec-ch-ua-platform', 'value': '"Windows"'},
                 {'key': 'origin', 'value': 'https://sso.bacic5i5j.com'},
                 {'key': 'content-type', 'value': 'application/x-www-form-urlencoded'},
                 {'key': 'upgrade-insecure-requests', 'value': '1'}, {'key': 'user-agent',
                                                                      'value': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'},
                 {'key': 'accept',
                  'value': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'},
                 {'key': 'sec-fetch-site', 'value': 'same-origin'}, {'key': 'sec-fetch-mode', 'value': 'navigate'},
                 {'key': 'sec-fetch-user', 'value': '?1'}, {'key': 'sec-fetch-dest', 'value': 'document'},
                 {'key': 'referer',
                  'value': 'https://sso.bacic5i5j.com/login?service=https://beijing.cbs.bacic5i5j.com/base/cas'},
                 {'key': 'accept-encoding', 'value': 'gzip, deflate, br, zstd'},
                 {'key': 'accept-language', 'value': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6'},
                 {'key': 'cookie',
                  'value': 'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%228386269%22%2C%22first_id%22%3A%22193f94c62a7605-049963a93117cf-26011851-3686400-193f94c62a818c3%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkzZjk0YzYyYTc2MDUtMDQ5OTYzYTkzMTE3Y2YtMjYwMTE4NTEtMzY4NjQwMC0xOTNmOTRjNjJhODE4YzMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI4Mzg2MjY5In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%228386269%22%7D%2C%22%24device_id%22%3A%22193f94c62a7605-049963a93117cf-26011851-3686400-193f94c62a818c3%22%7D, yd_srvbl=e344699bceda9e80b45559d5eeaded26, waf_srvbl=85b4c6b75636ad90e15f6d01b2f5e706, JSESSIONID=602B59926748743E5CFBBAF3AD5620DF'},
                 {'key': 'priority', 'value': 'u=0, i'}],
     'params': None,
     'data': [{'key': 'username', 'value': '123'}, {'key': 'password', 'value': '8660efd908b94c69'},
              {'key': 'encrypted', 'value': 'true'},
              {'key': 'lt', 'value': 'LT-1638152-sgfq5ojjuhUQR0II7bp13NAX2QYf6c'},
              {'key': 'execution', 'value': 'e1s1'}, {'key': '_eventId', 'value': 'submit'}],
     'body': None,
     'bodyType': 2}
b = {'url': 'https://miao.baidu.com/abdr?_o=https%3A%2F%2Ffanyi.baidu.com', 'method': 'POST',
     'headers': [{'key': 'Host', 'value': 'miao.baidu.com'}, {'key': 'Connection', 'value': 'keep-alive'},
                 {'key': 'Content-Length', 'value': '2311'}, {'key': 'sec-ch-ua-platform', 'value': '"Windows"'},
                 {'key': 'User-Agent',
                  'value': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'},
                 {'key': 'sec-ch-ua', 'value': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"'},
                 {'key': 'Content-Type', 'value': 'text/plain;charset=UTF-8'},
                 {'key': 'sec-ch-ua-mobile', 'value': '?0'}, {'key': 'Accept', 'value': '*/*'},
                 {'key': 'Origin', 'value': 'https://fanyi.baidu.com'}, {'key': 'Sec-Fetch-Site', 'value': 'same-site'},
                 {'key': 'Sec-Fetch-Mode', 'value': 'cors'}, {'key': 'Sec-Fetch-Dest', 'value': 'empty'},
                 {'key': 'Referer', 'value': 'https://fanyi.baidu.com/'},
                 {'key': 'Accept-Encoding', 'value': 'gzip, deflate, br, zstd'},
                 {'key': 'Accept-Language', 'value': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6'},
                 {'key': 'Cookie',
                  'value': 'BIDUPSID=83FD2B8893D28ED9A3F2936A2D06BA68; PSTM=1708229511; BAIDUID=83FD2B8893D28ED9E279CCA797B14669:FG=1; ab_jid=a242eabfcfcfeaa8352664c0a62e1f0d4d1e; ab_jid_BFESS=a242eabfcfcfeaa8352664c0a62e1f0d4d1e; MCITY=-131%3A; BDUSS=ZzMlRVUjNhZUVwN1RxU0JRVEhVY2U3VWdCbzNKakxXeU9HUElkSzcwUzFWTnhtRVFBQUFBJCQAAAAAAAAAAAEAAADZXUnZzfW087~JdXUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALXHtGa1x7Rmdk; BDUSS_BFESS=ZzMlRVUjNhZUVwN1RxU0JRVEhVY2U3VWdCbzNKakxXeU9HUElkSzcwUzFWTnhtRVFBQUFBJCQAAAAAAAAAAAEAAADZXUnZzfW087~JdXUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALXHtGa1x7Rmdk; ab_bid=1ea69785c59738d981566666813ecbbcfb57; BAIDUID_BFESS=83FD2B8893D28ED9E279CCA797B14669:FG=1; ZFY=tA2:AqWe8kGSivWKGjzBOcKP0rr3CnEIMcRPmk:A22EiM:C; H_WISE_SIDS=60277_61027_61217_61245_61246_60853_61367_61391_61392_61389_61434_61430_61493_61519_61529_61360; BA_HECTOR=2ga4a4a50kah01248k848k8l917bel1jms3851u; H_PS_PSSID=60277_61027_61217_60853_61391_61430_61519_61529_61360; delPer=0; PSINO=2; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_WISE_SIDS_BFESS=60277_61027_61217_61245_61246_60853_61367_61391_61392_61389_61434_61430_61493_61519_61529_61360; RT="z=1&dm=baidu.com&si=26938f42-37c8-428a-a0d4-a0510dba43e9&ss=m56ip5lt&sl=0&tt=0&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"'}],
     'params': [{'key': '_o', 'value': 'https://fanyi.baidu.com'}], 'data': None, 'body': None, 'bodyType': 0}

if __name__ == '__main__':
    get_send()
