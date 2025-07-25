#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2024/11/20
# @Author : Zulu
# @File : __init__
# @Software: PyCharm
# @Desc: Mock模块初始化文件

from fastapi import APIRouter

router = APIRouter(prefix="/mock", tags=['Mock接口'])