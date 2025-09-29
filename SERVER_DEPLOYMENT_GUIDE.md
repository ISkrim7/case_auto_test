# 服务器Docker部署手册

## 环境要求

- Linux服务器
- Docker 20.10+
- Docker Compose 1.29+
- 至少2GB可用内存

## 部署步骤

### 1. 安装Docker环境

```bash
# Ubuntu示例
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl enable --now docker
```

### 2. 准备项目文件

```bash
git clone [项目仓库地址]
cd case_auto_test
```

### 3. 构建Docker镜像

```bash
docker build -t auto-test-hub:2.2 .
```

### 4. 使用Docker Compose启动

```bash
docker-compose up -d
```

### 5. 验证服务

```bash
curl http://localhost:5050
```

## 配置说明

### 环境变量

可在docker-compose.yml中修改：

- `TZ`: 时区设置
- `MYSQL_*`: MySQL数据库配置
- `REDIS_*`: Redis配置

### 资源限制

- 最大使用2个CPU核心和512MB内存
- 保证至少0.5个CPU核心和256MB内存

## 镜像迁移部署

### 1. 导出镜像

```bash
# 保存镜像为tar文件
docker save -o auto-test-hub-2.0.tar auto-test-hub:2.0

# 压缩镜像文件(可选)
gzip auto-test-hub-2.0.tar
```

### 2. 传输镜像到目标服务器

```bash
scp auto-test-hub-2.0.tar* user@target-server:/path/to/directory
```

### 3. 在目标服务器导入镜像

```bash
# 如果是压缩过的镜像
gunzip auto-test-hub-2.0.tar.gz

# 导入镜像
docker load -i auto-test-hub-2.0.tar
```

### 4. 部署运行

#### 镜像与配置同步方案

1. **统一打包**：将镜像和对应的docker-compose文件一起打包

```bash
tar czvf auto-test-hub-bundle.tar.gz auto-test-hub-2.0.tar docker-compose.yml
```

2. **目录管理**：为每个项目创建独立目录

```bash
# 目标服务器操作
mkdir -p /opt/auto-test-hub
mv auto-test-hub-2.0.tar docker-compose.yml /opt/auto-test-hub
cd /opt/auto-test-hub
```

3. **版本验证**：确保镜像与配置版本匹配

```bash
# 查看镜像版本
docker images | grep auto-test-hub

# 验证docker-compose中的镜像版本
grep "image:" docker-compose.yml
```

4. **启动服务**：

```bash
docker load -i auto-test-hub-2.0.tar
docker-compose -f ./docker-compose.yml up -d
```

#### 多项目管理

```bash
# 项目A
/projects/project_a/
|- docker-compose.yml (引用image:project_a:1.0)
|- project_a-1.0.tar

# 项目B
/projects/project_b/
|- docker-compose.yml (引用image:project_b:2.0)
|- project_b-2.0.tar
```

## 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 更新服务
docker-compose pull && docker-compose up -d
```

## 多项目管理指南

### 1. 使用不同docker-compose文件

```bash
# 使用主配置(单服务模式)
docker-compose -f docker-compose.yml up -d

# 使用备份配置(包含数据库服务)
docker-compose -f docker-compose.bak up -d
```

### 2. 项目隔离方案

```bash
# 为不同项目创建独立网络
docker network create project1_network
docker-compose -f docker-compose.yml --project-name project1 --network project1_network up -d
```

### 3. 环境变量管理

建议使用.env文件管理不同环境的配置：

```bash
# .env文件示例
COMPOSE_PROJECT_NAME=my_project
TZ=Asia/Shanghai
MYSQL_SERVER=192.168.1.100
```

## 常见问题

1. 端口冲突：修改docker-compose.yml中的端口映射
2. 构建失败：检查网络连接和依赖安装
3. 内存不足：增加服务器内存或调整资源限制
4. 服务冲突：确保使用不同的项目名称(--project-name)
