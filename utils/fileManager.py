import os
from typing import AnyStr, NoReturn
from fastapi import UploadFile
from app.model.base import FileModel
from enums import FileEnum
from utils import GenerateTools
from file import current_dir as file_path
import shutil




def verify_dir(_path: str):
    if not os.path.exists(_path):
        os.makedirs(_path)




class FileManager:
    AVATAR = os.path.join(file_path, "Avatar")

    @staticmethod
    def writer(file: UploadFile, T: FileEnum, pid: str = None):
        """
        写入文件
        :param file: UploadFile
        :param T: 类型
        :param pid: 项目id
        :return:
        """
        fileName = GenerateTools.uid()
        opt = {
            FileEnum.AVATAR: FileManager._save_avatar,
            # FileEnum.BUG: FileManager._save_bug,
        }
        # if pid:
        #     return FileManager._save_excel(file, fileName, pid)
        return opt[T](file, fileName)

    @staticmethod
    def _save_avatar(file: UploadFile, fileName: str) -> str:
        verify_dir(FileManager.AVATAR)
        _path = os.path.join(FileManager.AVATAR, fileName)
        with open(_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return _path

    @staticmethod
    def delAvatar(avatarPath: AnyStr) -> NoReturn:
        """
        delAvatar
        :param avatarPath: 绝对路径
        :return:
        """
        if os.path.exists(avatarPath):
            os.remove(avatarPath)

    @staticmethod
    def reader(path:str):
        with open(path, "rb") as f:
            return f.read()
