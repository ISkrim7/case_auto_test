#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2024/11/20
# @Author : Zulu
# @File : mockModel
# @Software: PyCharm
# @Desc: Mock功能数据模型

from datetime import datetime
from sqlalchemy import Column, String, INTEGER, JSON, BOOLEAN, ForeignKey, DateTime, Text, UniqueConstraint
from app.model.basic import BaseModel

class MockRuleModel(BaseModel):
    """Mock规则表"""
    __tablename__ = 'mock_rule'
    __table_args__ = {
        'sqlite_autoincrement': True,
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'comment': 'Mock规则表'
    }
    user_id = Column(INTEGER, nullable=False, comment="所属用户ID", index=True)  # 新增用户ID字段
    interface_id = Column(INTEGER, ForeignKey("interface.id", ondelete="CASCADE"), comment="关联接口ID")
    path = Column(String(500), nullable=False, comment="接口路径")
    mockname = Column(String(100), nullable=True, comment="Mock接口名称")
    method = Column(String(10), nullable=False, comment="请求方法")
    status_code = Column(INTEGER, nullable=False, default=200, comment="响应状态码")
    response = Column(JSON, nullable=True, comment="响应内容")
    delay = Column(INTEGER, nullable=True, comment="延迟响应(毫秒)")
    enable = Column(BOOLEAN, default=False, comment="是否启用")
    description = Column(String(200), nullable=True, comment="规则描述")
    creator = Column(INTEGER, comment="创建人ID")
    creatorName = Column(String(50), comment="创建人姓名")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    headers = Column(JSON, nullable=True, comment="响应头")
    cookies = Column(JSON, nullable=True, comment="Cookies")
    content_type = Column(String(100), nullable=True, comment="响应内容类型")
    script = Column(Text, nullable=True, comment="前置/后置脚本")
    params = Column(JSON, nullable=True, comment="请求参数")
    request_headers = Column(JSON, nullable=True, comment="请求头")
    body_type = Column(INTEGER, nullable=False, comment="0无 1raw 2data 3..")
    raw_type = Column(String(50), nullable=True, comment="raw 类型 json text")
    body = Column(JSON, nullable=True, comment="请求体")
    data = Column(JSON, nullable=True, comment="表单")

    @property
    def key(self):
        """生成mock规则唯一键"""
        return f"{self.method}:{self.path}"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,  # 新增用户ID输出
            "interface_id": self.interface_id,
            "path": self.path,
            "mockname": self.mockname,
            "method": self.method,
            "status_code": self.status_code,
            "response": self.response,
            "delay": self.delay,
            "enable": self.enable,
            "description": self.description,
            "creator": self.creator,
            "creatorName": self.creatorName,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "headers": self.headers,
            "cookies": self.cookies,
            "content_type": self.content_type,
            "script": self.script,
            "params": self.params,
            "request_headers": self.request_headers,
            "body_type": self.body_type,
            "raw_type": self.raw_type,
            "body": self.body,
            "data": self.data
        }

# class MockConfigModel(BaseModel):
#     """Mock全局配置表"""
#     __tablename__ = 'mock_config'
#
#     name = Column(String(50), unique=True, nullable=False, comment="配置名称")
#     value = Column(String(200), nullable=False, comment="配置值")
#     description = Column(String(200), nullable=True, comment="配置描述")
#
#     @staticmethod
#     def get_default_configs():
#         """获取默认配置"""
#         return [
#             {"name": "mock_enabled", "value": "false", "description": "全局Mock开关"}
#         ]

# 修改MockConfigModel
class MockConfigModel(BaseModel):
    """Mock全局配置表"""
    __tablename__ = 'mock_config'
    user_id = Column(INTEGER, nullable=False, comment="所属用户ID", index=True)  # 新增用户ID字段
    name = Column(String(50), nullable=False, comment="配置名称")
    value = Column(String(200), nullable=False, comment="配置值")
    description = Column(String(200), nullable=True, comment="配置描述")
    creator = Column(INTEGER, comment="创建人ID")          # 必需字段
    creatorName = Column(String(50), comment="创建人姓名")  # 必需字段
    __table_args__ = (
        # 修正为复合唯一约束
        UniqueConstraint('user_id', 'name', name='uq_user_name'),
    )
    @staticmethod
    def get_default_configs():
        """获取默认配置"""
        return [
            {"name": "mock_enabled", "value": "false", "description": "全局Mock开关"}
        ]
