import asyncio
from typing import TypeVar, List

from app.mapper.interface import InterfaceTaskMapper
from app.model.base import User
from app.model.interface import InterfaceModel, InterFaceCaseModel, InterfaceTask, InterfaceTaskResultModel
from enums import InterfaceAPIResultEnum, StarterEnum
from utils import MyLoguru
from .io_sender import APISocketSender
from .runner import InterFaceRunner
from .starter import Starter
from .writer import InterfaceAPIWriter

log = MyLoguru().get_logger()
Interface = TypeVar('Interface', bound=InterfaceModel)
InterfaceCase = TypeVar('InterfaceCase', bound=InterFaceCaseModel)
Interfaces = List[Interface]
InterfaceCases = List[InterfaceCase]
InterfaceTaskResult = TypeVar('InterfaceTaskResult', bound=InterfaceTaskResultModel)


class TaskRunner:
    task: InterfaceTask
    result: str = InterfaceAPIResultEnum.SUCCESS

    def __init__(self,
                 starter: Starter | None,
                 io: APISocketSender | None):
        self.starter = starter
        self.io = io
        self.progress = 0

    async def runTask(self, taskId: int):
        """
        执行任务
        :param taskId: 任务Id
        :return:
        """
        self.task = await InterfaceTaskMapper.get_by_id(taskId)
        log.debug(f"running task {self.task} start by {self.starter.username}")

        task_result: InterfaceTaskResult = await InterfaceAPIWriter.init_interface_task(self.task,
                                                                                        starter=self.starter)

        try:
            apis: Interfaces = await InterfaceTaskMapper.query_apis(self.task.id)
            cases: InterfaceCases = await InterfaceTaskMapper.query_case(self.task.id)
            task_result.totalNumber = len(apis + cases)
            if apis:
                await self.__run_Apis(apis=apis, task_result=task_result)
            if cases:
                await self.__run_Cases(cases=cases, task_result=task_result)
        except Exception as e:
            log.exception(e)
            raise e
        finally:
            task_result.result = self.result
            log.debug(task_result.result)
            await InterfaceAPIWriter.write_interface_task_result(task_result)

    async def __run_Apis(self, apis: Interfaces, task_result: InterfaceTaskResult):
        """执行关联api"""
        parallel = self.task.parallel
        # 顺序执行
        if parallel == 0:
            return await self.__run_api_by_sequential_execution(apis, task_result)

        semaphore = asyncio.Semaphore(parallel)  # 限制并行数量为 parallel
        await self.io.send(f"并行数量 {parallel}")
        lock = asyncio.Lock()  # 保护共享资源
        tasks = []
        for api in apis:
            task = asyncio.create_task(
                self.__run_single_api_with_semaphore_and_lock(api, task_result, semaphore, lock)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def __run_api_by_sequential_execution(self, apis: Interfaces, task_result: InterfaceTaskResult, ):
        """顺序执行"""
        for api in apis:
            flag: bool = await InterFaceRunner(self.starter, self.io).run_interface_by_task(
                interface=api,
                taskResult=task_result
            )
            await self.write_process_result(flag, task_result)
            await self.io.clear_logs()

    async def __run_single_api_with_semaphore_and_lock(self, api: Interface, task_result: InterfaceTaskResult,
                                                       semaphore: asyncio.Semaphore, lock: asyncio.Lock):
        """执行单个 API，限制并行数量，并保护共享资源"""
        log.error(f"====={api}")
        async with semaphore:  # 限制并行数量
            flag: bool = await InterFaceRunner(self.starter, self.io).run_interface_by_task(
                interface=api,
                taskResult=task_result
            )

            # 使用锁保护共享资源的修改
            async with lock:
                await self.write_process_result(flag, task_result)
            await self.io.clear_logs()


    async def write_process_result(self,flag:bool, task_result: InterfaceTaskResult):
        await self.set_process(task_result)
        if flag:
            task_result.successNumber += 1
        else:
            self.result = InterfaceAPIResultEnum.ERROR
            task_result.failNumber += 1

    async def __run_Cases(self, cases: InterfaceCases, task_result: InterfaceTaskResult):
        """执行关联case"""
        for case in cases:
            flag: bool = await InterFaceRunner(self.starter, self.io).run_interfaceCase_by_task(
                interfaceCase=case,
                taskResult=task_result
            )
            await self.set_process(task_result)
            if flag:
                task_result.successNumber += 1
                break
            else:
                task_result.result = InterfaceAPIResultEnum.ERROR
                task_result.failNumber += 1
            await self.io.clear_logs()

    async def set_process(self, task_result: InterfaceTaskResult):
        """写进度"""
        self.progress += 1
        task_result.progress = round(self.progress / task_result.totalNumber, 1) * 100
        return await InterfaceAPIWriter.write_task_process(task_result=task_result)
