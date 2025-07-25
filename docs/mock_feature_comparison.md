# Mock功能对照文档

## 功能对照表

| 功能                | 本系统 | Mock.js | EasyMock | YApi | 备注 |
|---------------------|--------|---------|----------|------|------|
| **HTTP方法支持**     | ✅      | ✅       | ✅        | ✅    |      |
| **自定义状态码**     | ✅      | ✅       | ✅        | ✅    |      |
| **JSON响应**         | ✅      | ✅       | ✅        | ✅    |      |
| **文本响应**         | ✅      | ✅       | ✅        | ✅    |      |
| **延迟响应**         | ✅      | ✅       | ✅        | ❌    |      |
| **全局开关**         | ✅      | ❌       | ✅        | ❌    |      |
| **响应头设置**       | ✅      | ❌       | ✅        | ✅    |      |
| **Cookies设置**      | ✅      | ❌       | ❌        | ❌    | 本系统特有 |
| **内容类型设置**     | ✅      | ✅       | ✅        | ✅    |      |
| **脚本支持**         | ✅      | ✅       | ✅        | ✅    |      |
| **分页查询**         | ✅      | ❌       | ✅        | ✅    |      |
| **批量导入导出**     | ✅      | ❌       | ✅        | ✅    |      |
| **接口关联**         | ✅      | ❌       | ❌        | ✅    |      |
| **操作审计**         | ✅      | ❌       | ❌        | ✅    |      |
| **数据库持久化**     | ✅      | ❌       | ✅        | ✅    |      |

## 使用示例

### 1. 创建Mock规则
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/api/user",
  "method": "GET",
  "statusCode": 200,
  "response": {
    "id": 1,
    "name": "测试用户"
  },
  "delay": 500,
  "headers": {
    "X-Custom-Header": "value"
  }
}
```

### 2. 调用Mock接口
```http
GET /mock/api/user
```

### 3. 响应示例
```json
{
  "id": 1,
  "name": "测试用户"
}
```

## 使用场景示例

### 1. 测试异常场景
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/api/payment",
  "method": "POST",
  "statusCode": 400,
  "response": {
    "error": "余额不足",
    "code": "INSUFFICIENT_BALANCE"
  }
}
```

### 2. 测试分页数据
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/api/users",
  "method": "GET",
  "response": {
    "total": 100,
    "items": [
      {"id": 1, "name": "用户1"},
      {"id": 2, "name": "用户2"}
    ]
  }
}
```

### 3. 测试文件下载
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/api/export",
  "method": "GET",
  "content_type": "application/octet-stream",
  "headers": {
    "Content-Disposition": "attachment; filename=report.xlsx"
  }
}
```

## 脚本功能详解

脚本支持允许在请求前后执行自定义逻辑：

1. **前置脚本(beforeRequest)**
- 执行时机：收到请求后，返回mock响应前
- 典型用途：
  - 修改请求参数
  - 根据参数动态生成响应
  - 记录请求日志

2. **后置脚本(afterResponse)** 
- 执行时机：生成mock响应后，返回给客户端前
- 典型用途：
  - 修改响应数据
  - 添加额外字段
  - 数据格式转换

```javascript
// 动态响应示例
function beforeRequest(params) {
  return {
    statusCode: 200,
    response: {
      requestId: Date.now(),
      query: params
    }
  };
}

// 数据加工示例
function afterResponse(response) {
  if (response.data.items) {
    response.data.count = response.data.items.length;
  }
  return response;
}
```

## 前端开发指引

1. **环境配置**
   - 开发环境默认启用mock
   - 生产环境自动禁用

2. **调试建议**
   - 使用`/mock/status`接口检查mock状态
   - 通过延迟响应测试加载状态
   - 利用headers设置测试特殊场景

3. **错误处理**
   - 404: Mock规则不存在
   - 500: Mock服务内部错误
   - 403: Mock功能已禁用

## 高级测试场景

### 1. 性能测试模拟
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/api/performance",
  "method": "GET",
  "delay": 3000,
  "response": {
    "message": "高延迟响应",
    "metrics": {
      "load": 0.8,
      "responseTime": 3000
    }
  }
}
```

### 2. 安全性测试
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/api/auth",
  "method": "POST",
  "statusCode": 401,
  "headers": {
    "WWW-Authenticate": "Bearer error=\"invalid_token\""
  },
  "response": {
    "error": "无效令牌",
    "code": "AUTH_401"
  }
}
```

### 3. 系统集成模拟
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/external/payment",
  "method": "POST",
  "statusCode": 202,
  "response": {
    "transactionId": "ext_123456",
    "status": "processing"
  },
  "headers": {
    "X-External-System": "PaymentGateway/1.0"
  }
}
```

## 高级脚本案例

### 1. 条件响应
```javascript
function beforeRequest(params) {
  if (params.role === 'admin') {
    return {
      statusCode: 200,
      response: {
        data: '管理员数据',
        permissions: ['read', 'write', 'delete']
      }
    };
  } else {
    return {
      statusCode: 403,
      response: {
        error: '权限不足'
      }
    };
  }
}
```

### 2. 数据聚合处理
```javascript
function afterResponse(response) {
  if (Array.isArray(response.data)) {
    response.data.forEach(item => {
      item.fullName = `${item.firstName} ${item.lastName}`;
      item.timestamp = new Date().toISOString();
    });
    response.metadata = {
      count: response.data.length,
      generatedAt: Date.now()
    };
  }
  return response;
}
```

## 企业级应用指南

### 1. 压力测试配置
```http
POST /mock/create
Content-Type: application/json

{
  "path": "/api/stress",
  "method": "GET",
  "delay": 100,
  "response": {
    "requestCount": "${incrementCounter}",
    "timestamp": "${now}",
    "metrics": {
      "cpu": "${random(50,90)}%",
      "memory": "${random(1,8)}GB"
    }
  },
  "script": "function beforeRequest() { return { dynamicValues: true }; }"
}
```

### 2. 微服务策略
```http
POST /mock/create
Content-Type: application/json
{
  "path": "/service/user/v1/profile",
  "method": "GET",
  "headers": {
    "X-Service-Version": "1.0",
    "X-Service-Name": "user-service"
  },
  "response": {
    "service": "user",
    "version": "1.0",
    "data": {
      "userId": "${uuid}",
      "status": "active"
    }
  }
}
```

### 3. 自动化测试集成
```javascript
// Jest测试示例
test('should return 429 when rate limit exceeded', async () => {
  await mockApi.createRule({
    path: '/api/rate-limit',
    method: 'GET',
    statusCode: 429,
    response: { error: "Too Many Requests" }
  });

  const response = await request(app)
    .get('/api/rate-limit')
    .expect(429);

  expect(response.body.error).toBe("Too Many Requests");
});
```

### 4. 监控告警模拟
```http
POST /mock/create
Content-Type: application/json
{
  "path": "/monitor/alerts",
  "method": "POST",
  "statusCode": 201,
  "response": {
    "alertId": "alert_${timestamp}",
    "status": "firing",
    "severity": "critical",
    "annotations": {
      "summary": "High error rate detected",
      "description": "Error rate is ${random(5,20)}%"
    }
  }
}
```

## 高级功能说明
```javascript
// 前置脚本示例
function beforeRequest(params) {
  // 修改请求参数
  params.userId = 1000; 
  return params;
}

// 后置脚本示例
function afterResponse(response) {
  // 修改响应数据
  response.data.time = new Date();
  return response;
}
```

2. **接口关联**
- 通过`interface_id`关联实际接口
- 自动同步接口路径和方法