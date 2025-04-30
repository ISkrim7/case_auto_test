import json
import os
from typing import AnyStr, NoReturn
from fastapi import UploadFile

from app.mapper.file import FileMapper
from app.model.base import User
from config import Config
from utils import GenerateTools, log
import magic
file_path = os.path.dirname(os.path.abspath(__file__))

AVATAR = os.path.join(file_path, "avatar")
API_DATA = os.path.join(file_path, "api_data")
def verify_dir(_path: str):
    if not os.path.exists(_path):
        os.makedirs(_path)


class FileManager:
    # 头像


    @staticmethod
    async def save_data_file(file: UploadFile, interfaceId: str):
        """
        接口请求form 附件保存
        """
        verify_dir(API_DATA)
        fileName = f"{interfaceId}_{file.filename}"
        filePath = os.path.join(API_DATA, fileName)
        with open(filePath, "wb") as buffer:
            buffer.write(await file.read())

        return fileName


    @staticmethod
    async def save_avatar(file: UploadFile, user: User):
        """
        头像存本地
        路径存file table
        url 存user
        更新
        删除本地原来
        删除file table
        重新存
        """
        verify_dir(AVATAR)
        if user.avatar:
            log.debug(user.avatar)
            await FileMapper.remove_file(user.avatar.split("uid=")[-1])

        fileName = GenerateTools.uid()
        fileType = file.content_type
        filePath = os.path.join(AVATAR, fileName)
        with open(filePath, "wb") as buffer:
            buffer.write(await file.read())

        file_model = await FileMapper.insert(**dict(
            fileType=fileType,
            filePath=filePath,
            fileName=fileName
        ))
        avatar_PATH = Config.FILE_AVATAR_PATH + file_model.uid
        from app.mapper.user import UserMapper
        await UserMapper.set_avatar(avatar_PATH, user)

    @staticmethod
    def delFile(path: AnyStr):
        """
        delAvatar
        :param path: 绝对路径
        :return:
        """
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def reader(path: str):
        with open(path, "rb") as f:
            return f.read()
