# 接口&UI自动化平台

[![FastAPI](https://img.shields.io/badge/FastAPI-blue)](https://www.python.org/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![Httpx](https://img.shields.io/badge/Httpx-blue)](https://www.python-httpx.org/)
[![PlayWright](https://img.shields.io/badge/PlayWright-blue)](https://playwright.dev/python/docs/api/class-playwright)
[![Mysql](https://img.shields.io/badge/Mysql-blue)]()
[![Redis](https://img.shields.io/badge/Redis-blue)]()


---

## 🚀 功能特点

### 接口自动化能力

✨ **核心功能**：

- **基础 HTTP 请求**：支持多种 HTTP 请求类型（GET、POST、PUT、DELETE 等）。
- **变量提取与写入**：可从响应中提取变量，支持在后续请求中使用。
- **断言功能**：提供响应状态码、内容等多种断言验证。
- **前后置脚本**：在用例执行前后执行自定义 Python 脚本。
- **调试模式**：逐步执行测试用例，便于精准排查问题。
- **用例执行**：支持单个或批量用例的执行。
- **定时任务**：定时执行接口测试任务，适用于定期测试。
- **报告展示**：自动生成并展示 HTML 格式的测试报告，明确显示成功与失败的详细信息。
- **实时日志可视化**：在测试执行过程中实时展示日志，便于进度监控。
- **接口录制（未完善）**：录制接口请求并快速生成对应的测试用例。（计划在未来版本中实现）

### UI 自动化功能

✨ **Playwright 集成**：

- **UI 自动化支持**：集成了 Playwright，能够执行浏览器自动化测试，模拟用户操作界面。
- **步骤录入**：支持在 UI 测试中录入测试步骤，便于快速创建测试用例。
- **前后置接口请求**：每个步骤可与前后置接口请求结合，动态调整测试流程。
- **全局变量**：支持全局变量的管理，步骤和请求中的变量可以全局共享，方便管理和使用。
- **公共步骤编辑**：支持创建和管理公共步骤，可以重复使用，减少冗余，提升效率。
- **任务管理**：与接口测试类似，UI 测试任务支持定时执行与结果推送，支持企业微信等推送方式。
- **SQL 支持（未完成）**：计划在未来版本中支持 SQL 操作，增强数据处理能力。
- **IF 条件判断执行**：支持根据条件判断执行特定步骤，灵活控制测试流程。

---

## 🖥️ UI 展示

#### [前端项目地址](https://github.com/Caoyongqi912/caseHubWeb)

### 📊 首页数据展示

![index](resource/index.png)

### 📊 **API 列表**

展示所有接口的概览：

![API列表](resource/api.png)

---

### 🔍 **API 详情**

***查看单个接口的详细信息***

![API详情](resource/detail.png)

---

***前置操作***

![前置](resource/before1.png)

![前置](resource/before2.png)

![前置](resource/before3.png)

---

***响应提取***

![extract](resource/extract.png)

***断言***

![assert](resource/assert.png)

**请求变量写入**

![assert](resource/var1.png)
![assert](resource/var0.png)
支持

- url
- header
- query
- body
- exec sql

### 🖱️ **APITry**

支持在 UI 中直接执行接口请求，快速验证 API 可用性：

![APITry](resource/try.gif)

---

### ➕ **Case 添加 API**

支持：

- 添加公共 API
- 手动录入 API
- 添加API GROUP
- API 执行拖拽排序
- 支持基本的 CRUD 操作

![Case添加API](resource/caseAdd.gif)

---

### ⚡ **RunCase 执行用例**

- **同步执行**：实时展示测试日志，确保每个步骤都可监控。
  ![RunCase](resource/runBySync.gif)

- **后台执行 & 轮询结果**：适用于长期任务或需要在后台执行的测试。
  ![RunCase](resource/runByAsync.gif)

---

### 📅 **Task 接口任务**

任务可关联多个 API 用例，支持：

- 定时任务执行
- 执行结果推送（目前支持企业微信）

![Task接口任务](resource/task_detail.png)

---

### 📈 **Task 任务报告**

生成并展示任务执行后的详细报告，帮助团队了解测试状态。

![Report](resource/report.png)

## UI自动化

- 支持配置方法、环境、公共步骤、操作任务的调度
- UI执行步骤前后置接口请求、SQL(未完成) IF 条件判断执行
- 步骤拖拽排序、

![ui](resource/ui_detail.gif)


---

## 🛠️ 安装与使用

### 安装依赖

1. 克隆项目

2. 编写config

    - 配置自己的数据库等相关内容
        - config.py
        - 主要是下面 按照本地情况自定义

```python
class LocalConfig(BaseConfig):
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 5050
    DOMAIN = f"http://{SERVER_HOST}:{SERVER_PORT}"
    UI_Headless = True
    UI_Timeout = 5000
    UI_SLOW = 500
    UI_ERROR_PATH = DOMAIN + "/file/ui_case/uid="
    FILE_AVATAR_PATH = DOMAIN + "/file/avatar/uid="
    APS = False
    Record_Proxy = False
    MYSQL_SERVER = "127.0.0.1"
    MYSQL_PASSWORD = "your password"
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(
        'root', MYSQL_PASSWORD, MYSQL_SERVER, BaseConfig.MYSQL_PORT, BaseConfig.MYSQL_DATABASE)

    ASYNC_SQLALCHEMY_URI = f'mysql+aiomysql://root:{MYSQL_PASSWORD}'
    f'@{MYSQL_SERVER}:{BaseConfig.MYSQL_PORT}/{BaseConfig.MYSQL_DATABASE}'


# UI_TASK_URL = f"{DOMAIN}:{BaseConfig.STRUCTURE_WEB_SERVER_PORT}/ui/task/detail/taskId="
# UI_REPORT_URL = f"{DOMAIN}:{BaseConfig.STRUCTURE_WEB_SERVER_PORT}/report/history/uiTask/detail/uid="

REDIS_DB = 0
REDIS_SERVER = "127.0.0.1"
REDIS_URL: str = f"redis://{REDIS_SERVER}:{BaseConfig.REDIS_PORT}/{REDIS_DB}"

# 定时任务Stores
APSJobStores = {
    'default': RedisJobStore(
        db=2,  # Redis 数据库编号
        jobs_key='apscheduler.jobs',  # 存储任务的键
        run_times_key='apscheduler.run_times',  # 存储任务运行时间的键
        host=REDIS_SERVER,  # Redis 服务器地址
        port=BaseConfig.REDIS_PORT,  # Redis 服务器端口
        password=None  # Redis 密码（如果没有密码，设置为 None）
    ),

}
# oracle client 
CX_Oracle_Client_Dir = "/your/instantclient_23_3"

```

3. 安装所需依赖：

    ```bash
    pip install -r requirements.txt
    ```

4、安装mysql 、 redis

5、运行

- 查看main.py
    - `init_aps` 定时任务开启
    - `init_db` 创建表
    - `init_proxy` 开启代理 （暂时不用开，配置关闭就好）
    - `init_redis` 配合 proxy 使用 也可不用开
- 执行 run.py
- 添加admin用户 见这个接口
```python
@router.post(path="/registerAdmin", description="添加管理")
async def register_admin(user: RegisterAdmin) -> Response:
    await UserMapper.register_admin(**user.dict())
    return Response.success()
```

6、前端部署见 [前端项目](https://github.com/Caoyongqi912/caseHubWeb)


> 存在疑问？联系我
>
![](resource/wx.png)


