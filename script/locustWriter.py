import subprocess


def run_locust(test_id: str, url: str, method: str, headers: dict, body: dict, users: int, spawn_rate: int, run_time: str):
    """
    动态生成 Locust 脚本并启动压测
    """
    # 生成 Locust 脚本
    locust_script = f"""
from locust import HttpUser, task, between
import json

class DynamicUser(HttpUser):
    wait_time = constant(3)

    @task
    def test_api(self):
        headers = {headers}
        body = {body}
        method = "{method.lower()}"
        if method == "get":
            self.client.get("{url}", headers=headers)
        elif method == "post":
            self.client.post("{url}", json=body, headers=headers)
        elif method == "put":
            self.client.put("{url}", json=body, headers=headers)
        elif method == "delete":
            self.client.delete("{url}", headers=headers)
"""

    # 将脚本写入文件
    script_path = f"locust_script_{test_id}.py"
    with open(script_path, "w") as f:
        f.write(locust_script)
    # 启动 Locust
    locust_command = [
        "locust",
        "-f", script_path,
        "--host", "",  # 目标 URL 已经在脚本中指定
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--headless",
        "--csv", f"results_{test_id}"  # 将结果保存到 CSV 文件
    ]
    subprocess.run(locust_command)
    # 读取压测结果
    with open(f"results_{test_id}_stats.csv", "r") as f:
        results = f.read()
    load_test_results = {}

    # 存储结果
    load_test_results[test_id] = results
if __name__ == '__main__':
    run_locust(test_id="1", url="", method="get", headers={}, body={}, users=1, spawn_rate=1, run_time="1m")
