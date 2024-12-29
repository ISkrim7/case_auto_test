import json
import os
from typing import AnyStr, NoReturn
from fastapi import UploadFile

from app.mapper.file import FileMapper
from app.model.base import User
from config import Config
from utils import GenerateTools, log
from file import current_dir as file_path


def verify_dir(_path: str):
    if not os.path.exists(_path):
        os.makedirs(_path)


class FileManager:
    # 头像
    AVATAR = os.path.join(file_path, "avatar")

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
        verify_dir(FileManager.AVATAR)
        if user.avatar:
            log.debug(user.avatar)
            await FileMapper.remove_file(user.avatar.split("uid=")[-1])

        fileName = GenerateTools.uid()
        fileType = file.content_type
        filePath = os.path.join(FileManager.AVATAR, fileName)
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

    @staticmethod
    def json_file_reader(path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(data)

if __name__ == '__main__':
    FileManager.json_file_reader("../cyq的项目.json")