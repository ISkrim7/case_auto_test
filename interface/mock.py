#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2024/11/20
# @Author : Zulu
# @File : mock
# @Software: PyCharm
# @Desc: 接口测试Mock功能实现

from typing import Dict, Any, Optional
from fastapi import Request, Response as FastResponse
from httpx import Response
import json
import asyncio
from utils import MyLoguru
from app.mapper.interface.mockMapper import MockRuleMapper, MockConfigMapper
from sqlalchemy.ext.asyncio import AsyncSession
from app.model import async_session
log = MyLoguru().get_logger()
from app.model.interface.mockModel import MockRuleModel

class MockManager:
    """Mock功能管理器"""

    def __init__(self):
        self.mock_rules: Dict[str, Dict] = {}
        # 初始化时不加载数据，由外部调用者通过get_mock_manager()或显式调用_load_from_db()
        # 按用户ID存储规则 {user_id: {rule_key: rule_data}}
        self.user_rules: Dict[int, Dict[str, Dict]] = {}
        # 存储用户全局Mock状态 {user_id: enabled}
        self.user_status: Dict[int, bool] = {}

    async def _load_user_rules(self, user_id: int, session: AsyncSession):
        """加载指定用户的mock规则到内存"""
        if user_id not in self.user_rules:
            rules = await MockRuleMapper.get_active_rules(user_id, session)
            self.user_rules[user_id] = {}
            for rule in rules:
                key = f"{rule.method}:{rule.path}"
                self.user_rules[user_id][key] = rule.to_dict()

    async def _get_user_mock_status(self, user_id: int, session: AsyncSession) -> bool:
        """获取并缓存用户全局Mock状态"""
        if user_id not in self.user_status:
            try:
                self.user_status[user_id] = await MockConfigMapper.is_mock_enabled(user_id, session)
                log.info(f"User {user_id} mock status: {self.user_status[user_id]}")
            except Exception as e:
                log.error(f"Failed to get mock status for user {user_id}: {str(e)}")
                self.user_status[user_id] = False
        return self.user_status[user_id]

    async def _load_from_db(self, user_id: int, session: AsyncSession = None):
        """从数据库加载mock规则"""
        try:

            # 检查Mock状态
            if not await MockConfigMapper.is_mock_enabled(user_id, session):
                log.debug(f"用户{user_id}的Mock功能未启用，跳过规则加载")
                return False

            # 加载规则
            rules = await MockRuleMapper.get_active_rules(user_id, session)
            if not rules:
                log.info(f"用户{user_id}没有启用的Mock规则")
                return True

            # 清空现有规则
            self.mock_rules.clear()

            # 处理规则
            valid_count = 0
            for rule in rules:
                try:
                    # 验证规则类型
                    if not isinstance(rule, MockRuleModel):
                        log.error(f"无效规则类型: {type(rule)}")
                        continue

                    key = f"{rule.method}:{rule.path}"
                    self.mock_rules[key] = {
                        "status_code": rule.status_code,
                        "response": rule.response,
                        "delay": rule.delay / 1000 if rule.delay else None,
                        "interface_id": rule.interface_id,
                        "mockname": rule.mockname,
                        "headers": rule.headers,
                        "cookies": rule.cookies,
                        "content_type": rule.content_type,
                        "script": rule.script
                    }
                    valid_count += 1
                    log.debug(f"加载规则: {key}")

                except AttributeError as ae:
                    log.error(f"规则字段缺失: {str(ae)}")
                except Exception as e:
                    log.error(f"处理规则失败: {str(e)}")

            log.info(f"成功加载{valid_count}/{len(rules)}条规则")
            return True

        except Exception as e:
            log.error(f"Failed to load mock rules from database for user {user_id}: {str(e)}")
            return False

    async def add_mock_rule(self,
                          path: str,
                          method: str = "GET",
                          status_code: int = 200,
                          response: Optional[Dict[str, Any]] = None,
                          delay: Optional[float] = None,
                          interface_id: Optional[int] = None,
                          mockname: Optional[str] = None,
                          description: Optional[str] = None,
                          headers: Optional[Dict[str, Any]] = None,
                          cookies: Optional[Dict[str, Any]] = None,
                          content_type: Optional[str] = None,
                          script: Optional[str] = None) -> bool:
        """添加Mock规则到数据库和内存"""
        key = f"{method.upper()}:{path}"

        # 保存到数据库
        rule = await MockRuleMapper.save(
            interface_id=interface_id,
            path=path,
            mockname=mockname,
            method=method.upper(),
            status_code=status_code,
            response=response or {},
            delay=int(delay * 1000) if delay else None,
            enable=True,
            description=description,
            headers=headers,
            cookies=cookies,
            content_type=content_type,
            script=script
        )

        # 更新内存缓存
        self.mock_rules[key] = {
            "status_code": status_code,
            "response": response or {},
            "delay": delay,
            "interface_id": interface_id,
            "mockname": mockname,
            "headers": headers,
            "cookies": cookies,
            "content_type": content_type,
            "script": script
        }

        log.info(f"Added mock rule: {key} for interface {interface_id}")
        return True

    async def update_mock_rule_by_id(self,
                                   rule_id: int,
                                   path: Optional[str] = None,
                                   method: Optional[str] = None,
                                   status_code: Optional[int] = None,
                                   response: Optional[Dict[str, Any]] = None,
                                   delay: Optional[float] = None,
                                   interface_id: Optional[int] = None,
                                   mockname: Optional[str] = None,
                                   description: Optional[str] = None,
                                   headers: Optional[Dict[str, Any]] = None,
                                   cookies: Optional[Dict[str, Any]] = None,
                                   content_type: Optional[str] = None,
                                   script: Optional[str] = None) -> bool:
        """根据ID更新Mock规则"""
        # 构建更新数据
        update_data = {}
        if path is not None:
            update_data["path"] = path
        if method is not None:
            update_data["method"] = method.upper()
        if status_code is not None:
            update_data["status_code"] = status_code
        if response is not None:
            update_data["response"] = response
        if delay is not None:
            update_data["delay"] = int(delay * 1000)
        if interface_id is not None:
            update_data["interface_id"] = interface_id
        if mockname is not None:
            update_data["mockname"] = mockname
        if description is not None:
            update_data["description"] = description
        if headers is not None:
            update_data["headers"] = headers
        if cookies is not None:
            update_data["cookies"] = cookies
        if content_type is not None:
            update_data["content_type"] = content_type
        if script is not None:
            update_data["script"] = script

        # 更新数据库
        await MockRuleMapper.update_by_id(rule_id, update_data)

        # 获取更新后的规则
        updated_rule = await MockRuleMapper.get_by_id(rule_id)
        if not updated_rule:
            log.error(f"Failed to get updated mock rule with id: {rule_id}")
            return False

        # 更新内存缓存
        key = f"{updated_rule.method}:{updated_rule.path}"
        self.mock_rules[key] = {
            "status_code": updated_rule.status_code,
            "response": updated_rule.response,
            "delay": updated_rule.delay / 1000 if updated_rule.delay else None,
            "interface_id": updated_rule.interface_id,
            "mockname": updated_rule.mockname,
            "headers": updated_rule.headers,
            "cookies": updated_rule.cookies,
            "content_type": updated_rule.content_type,
            "script": updated_rule.script
        }

        log.info(f"Updated mock rule by id: {rule_id}")
        return True

    async def remove_mock_rule(self, path: str, method: str = "GET") -> bool:
        """从数据库和内存中删除Mock规则"""
        key = f"{method.upper()}:{path}"
        if key in self.mock_rules:
            # 从数据库删除
            await MockRuleMapper.delete_by(path=path, method=method.upper())
            # 从内存删除
            del self.mock_rules[key]
            log.info(f"Removed mock rule: {key}")
            return True
        return False

    async def clear_mock_rules(self):
        """清空所有Mock规则"""
        # 从数据库删除所有规则
        await MockRuleMapper.delete_all()
        # 清空内存缓存
        self.mock_rules.clear()
        log.info("Cleared all mock rules from database and memory")


    async def mock_response(self, path: str, method: str, user_id: int, session: AsyncSession) -> Optional[FastResponse]:

        """增强匹配日志的Mock响应处理"""
        try:
            log.info(f"====== 开始处理Mock请求: {method} {path} ======")

            # 1. 检查全局Mock状态
            user_enabled = await MockConfigMapper.is_mock_enabled(user_id, session)
            log.debug(f"用户 {user_id} 全局Mock状态: {user_enabled}")

            if not user_enabled:
                log.info(f"用户 {user_id} 的Mock功能未启用")
                return None

            # 2. 加载用户规则
            log.debug("加载用户规则...")
            await self._load_user_rules(user_id, session)
            user_rules = self.user_rules.get(user_id, {})

            # 记录所有规则
            log.debug(f"用户 {user_id} 的所有规则: {list(user_rules.keys())}")
            log.info(f"内存中加载的规则数量: {len(user_rules)}")

            # 3. 标准化请求路径
            clean_path = path.split('?')[0]  # 移除查询参数
            # 确保路径以斜杠开头
            standardized_path = clean_path if clean_path.startswith('/') else f'/{clean_path}'
            standardized_path = standardized_path.rstrip('/')  # 移除结尾斜杠
            log.debug(f"标准化路径: '{standardized_path}' (原始: '{clean_path}')")

            # 4. 尝试匹配规则
            matching_key = None
            matched_rule = None

            # 精确匹配
            exact_key = f"{method.upper()}:{standardized_path}"
            log.debug(f"尝试精确匹配: {exact_key}")
            if exact_key in user_rules:
                matching_key = exact_key
                matched_rule = user_rules[exact_key]
                log.info(f"精确匹配成功: {exact_key}")

            # 前缀匹配
            if not matched_rule:
                log.debug("精确匹配失败，尝试前缀匹配...")
                for rule_key in user_rules:
                    rule_method, rule_path = rule_key.split(":", 1)
                    rule_path = rule_path.rstrip('/')

                    # 确保规则路径以斜杠开头
                    if not rule_path.startswith('/'):
                        rule_path = f'/{rule_path}'

                    # 比较标准化后的路径
                    if method.upper() == rule_method and standardized_path == rule_path:
                        matching_key = rule_key
                        matched_rule = user_rules[rule_key]
                        log.info(f"前缀匹配成功: {rule_key}")
                        break

            # 后缀匹配
            if not matched_rule:
                log.debug("前缀匹配失败，尝试后缀匹配...")
                for rule_key in user_rules:
                    rule_method, rule_path = rule_key.split(":", 1)
                    rule_path = rule_path.rstrip('/')

                    if method.upper() == rule_method and standardized_path.endswith(rule_path):
                        matching_key = rule_key
                        matched_rule = user_rules[rule_key]
                        log.info(f"后缀匹配成功: {rule_key}")
                        break

            # 通配符匹配
            if not matched_rule:
                log.debug("后缀匹配失败，尝试通配符匹配...")
                for rule_key in user_rules:
                    rule_method, rule_path = rule_key.split(":", 1)
                    rule_path = rule_path.rstrip('/')

                    # 处理通配符
                    if '*' in rule_path:
                        pattern = rule_path.replace('*', '.*')
                        import re
                        if re.match(pattern, standardized_path) and method.upper() == rule_method:
                            matching_key = rule_key
                            matched_rule = user_rules[rule_key]
                            log.info(f"通配符匹配成功: {rule_key} -> {standardized_path}")
                            break

            # 5. 构建响应
            if matched_rule:
                log.info(f"找到匹配规则: {matching_key}")
                return await self._build_response(matched_rule)

            log.warning(f"未找到匹配规则: 方法={method} 路径={standardized_path}")
            log.debug(f"所有尝试的规则: {list(user_rules.keys())}")
            return None

        except Exception as e:
            log.exception(f"Mock响应处理失败: {str(e)}")
            return None

    async def _build_response(self, rule: dict) -> FastResponse:
        """根据规则构建响应"""
        """根据规则构建响应"""
        # 处理延迟响应
        if rule.get("delay"):
            # 数据库存储的是毫秒，转换为秒
            await asyncio.sleep(rule["delay"] / 1000)

        # 构建响应
        response_data = rule.get("response") or {}
        if isinstance(response_data, str):
            try:
                response_data = json.loads(response_data)
            except json.JSONDecodeError:
                response_data = {"raw": response_data}

        response = FastResponse(
            status_code=rule.get("status_code", 200),
            content=json.dumps(response_data) if isinstance(response_data, dict) else response_data,
            media_type=rule.get("content_type", "application/json")
        )

        # 添加自定义headers
        if headers := rule.get("headers"):
            for key, value in headers.items():
                response.headers[key] = str(value)

        # 添加cookies
        if cookies := rule.get("cookies"):
            for key, value in cookies.items():
                response.set_cookie(key=key, value=str(value))

        return response


async def enable(self, user_id: int, session: AsyncSession):
    """启用用户Mock功能并同步到数据库"""
    try:
        # 确保session处于活动状态
        if not session.in_transaction():
            async with session.begin():
                return await self._do_enable(user_id, session)
        else:
            return await self._do_enable(user_id, session)
    except Exception as e:
        log.error(f"Failed to enable mock for user {user_id}: {str(e)}")
        raise

async def _do_enable(self, user_id: int, session: AsyncSession):
    """实际执行启用操作"""
    # 先检查当前状态
    current_status = await MockConfigMapper.is_mock_enabled(user_id, session)
    if current_status:
        log.info(f"用户 {user_id} 的Mock功能已处于启用状态")
        return

    # 更新状态
    await MockConfigMapper.update_global_status(True, user_id, session)
    self.user_status[user_id] = True
    log.info(f"Mock enabled for user {user_id}")

async def disable(self, user_id: int):
    """禁用用户Mock功能并同步到数据库"""
    try:
        await MockConfigMapper.update_global_status(False, user_id)
        self.user_status[user_id] = False
        self.user_rules.pop(user_id, None)  # 清除用户规则缓存
        log.info(f"Mock disabled for user {user_id}")
    except Exception as e:
        log.error(f"Failed to disable mock for user {user_id}: {str(e)}")
        raise

# 全局Mock管理器实例
mock_manager = MockManager()

async def get_mock_manager(user_id: int, session: AsyncSession = None) -> MockManager:

    """获取Mock管理器实例（支持传入会话）"""
    # 确保管理器初始化
    if not hasattr(mock_manager, 'user_rules'):
        mock_manager.user_rules = {}

    if not hasattr(mock_manager, 'user_status'):
        mock_manager.user_status = {}

    # 使用传入会话或创建新会话
    if session:
        # 使用传入会话加载规则
        await mock_manager._load_from_db(user_id, session)
    else:
        # 创建新会话
        async with async_session() as new_session:
            await mock_manager._load_from_db(user_id, new_session)

    # 确保状态一致
    mock_manager.user_status[user_id] = await MockConfigMapper.is_mock_enabled(user_id, session)
    return mock_manager

async def mock_request_checker(request: Request, call_next):
    """检查请求头中是否有mock标志"""
    if request.headers.get("X-Mock-Request", "").lower() != "true":
        return FastResponse(
            status_code=404,
            content=json.dumps({
                "code": 404,
                "message": "非Mock请求",
                "suggestion": "如需Mock请求，请添加X-Mock-Request: true请求头"
            }),
            media_type="application/json"
        )
    return await call_next(request)

async def init_mock_config():
    """初始化mock配置"""
    try:
        # 强制初始化mock配置，确保至少有一条记录
        result = await MockConfigMapper.init_default_configs(force=True)
        if result:
            log.info("Mock config initialized successfully")
        else:
            log.warning("Mock config already exists, enabling mock by default")
            await MockConfigMapper.update_global_status(True)
        return True
    except Exception as e:
        log.error(f"Failed to initialize mock config: {str(e)}")
        return False