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

1. 克隆项目：

    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```
2. 编写config：

    - 配置自己的数据库等相关内容

3. 安装所需依赖：

    ```bash
    pip install -r requirements.txt
    ```

4. 执行run.py

## 💡 贡献

欢迎提交 Issues 或 Pull Requests，若有任何问题或建议，随时与我联系。

---
> 联系我
>
![](resource/wx.png)

> 一起推动接口自动化测试工具的成长与发展！
