from typing import TypeVar

from setuptools.command.alias import alias
from sqlalchemy import select, and_, case
from sqlalchemy.sql.functions import count, func

from app.mapper import Mapper
from app.mapper.interface import InterfaceCaseMapper
from app.mapper.ui.uiCaseMapper import UICaseMapper
from app.model import async_session, BaseModel
from app.model.interface import InterFaceCaseModel, InterfaceTask, InterfaceTaskResultModel
from app.model.ui import UICaseModel, UITaskModel, UICaseTaskResultBaseModel
from utils import log, GenerateTools

T = TypeVar('T', bound=BaseModel)


class StatisticsMapper:

    @staticmethod
    async def all_statistics():
        statistics = {"apis": 0, "uis": 0}
        try:
            apis = await InterfaceCaseMapper.count_()
            uis = await UICaseMapper.count_()
            statistics['apis'] = apis
            statistics['uis'] = uis
            return statistics
        except Exception as e:
            log.error(e)
            return statistics

    @staticmethod
    async def task_data(n=7):
        """
        查询本周运行情况

        :param n: 查询天数
        """
        result = {
            "api_tasks": [],
            "ui_tasks": []
        }
        try:
            async with async_session() as session:
                async with session.begin():
                    api_task = await session.execute(
                        select(
                            InterfaceTaskResultModel.runDay.label("date"),
                            func.count().label("total_num"),  # 总数量
                            func.sum(case((InterfaceTaskResultModel.status == "SUCCESS", 1), else_=0)).label(
                                "success_num"),  # 成功数量
                            func.sum(case((InterfaceTaskResultModel.status == "FAIL", 1), else_=0)).label("fail_num")
                            # 失败数量
                        ).where(
                            InterfaceTaskResultModel.runDay >= GenerateTools.get_date_days_ago(n)
                        ).order_by(
                            InterfaceTaskResultModel.runDay.asc()
                        )
                        .group_by(
                            InterfaceTaskResultModel.runDay
                        )
                    )
                    ui_task = await session.execute(
                        select(
                            UICaseTaskResultBaseModel.run_day.label("date"),
                            func.count().label("total_num"),  # 总数量
                            func.sum(case((UICaseTaskResultBaseModel.status == "SUCCESS", 1), else_=0)).label(
                                "success_num"),  # 成功数量
                            func.sum(case((UICaseTaskResultBaseModel.status == "FAIL", 1), else_=0)).label("fail_num")
                            # 失败数量
                        ).where(
                            UICaseTaskResultBaseModel.run_day >= GenerateTools.get_date_days_ago(n)
                        ).order_by(
                            UICaseTaskResultBaseModel.run_day.asc()
                        )
                        .group_by(
                            UICaseTaskResultBaseModel.run_day
                        )

                    )
                    result['api_tasks'] = _format_task_data(api_task.all(), "API")
                    result['ui_tasks'] = _format_task_data(ui_task.all(), "UI")
                    return result

        except Exception as e:
            log.error(e)
            return result

    @staticmethod
    async def task_today_data():

        try:
            result = {}
            date = GenerateTools.getTime(5)
            async with async_session() as session:
                async with session.begin():
                    api_task = await session.execute(
                        select(
                            InterfaceTaskResultModel.runDay.label("date"),
                            func.count().label("total_num"),  # 总数量
                            func.sum(case((InterfaceTaskResultModel.status == "SUCCESS", 1), else_=0)).label(
                                "success_num"),  # 成功数量
                            func.sum(case((InterfaceTaskResultModel.status == "FAIL", 1), else_=0)).label("fail_num")
                        ).where(
                            InterfaceTaskResultModel.runDay == date
                        )
                    )
                    ui_task = await session.execute(
                        select(
                            UICaseTaskResultBaseModel.run_day.label("date"),
                            func.count().label("total_num"),  # 总数量
                            func.sum(case((UICaseTaskResultBaseModel.status == "SUCCESS", 1), else_=0)).label(
                                "success_num"),  # 成功数量
                            func.sum(case((UICaseTaskResultBaseModel.status == "FAIL", 1), else_=0)).label("fail_num")
                        ).where(
                            UICaseTaskResultBaseModel.run_day == date
                        )
                    )
                    apis = api_task.fetchone()
                    uis = ui_task.fetchone()

                    result['api_task'] = {
                        "date": apis.date if apis.date else date,
                        "total_num": apis.total_num if apis.total_num else 0,
                        "success_num": apis.success_num if apis.success_num else 0,
                        "fail_num": apis.fail_num if apis.fail_num else 0
                    }
                    result['ui_task'] = {
                        "date": uis.date if uis.date else date,
                        "total_num": uis.total_num if uis.total_num else 0,
                        "success_num": uis.success_num if uis.success_num else 0,
                        "fail_num": uis.fail_num if uis.fail_num else 0
                    }
                    return result
        except Exception as e:
            raise e

    @staticmethod
    async def week_data(n=7):
        try:
            statistics = {
                "apis": 0,
                "api_task": 0,
                "uis": 0,
                "apis_growth": 0,
                "api_task_growth": 0,
                "uis_growth": 0,
                "ui_task_growth": 0
            }
            date = GenerateTools.get_date_days_ago(n)
            two_weeks_ago_date = GenerateTools.get_date_days_ago(n + 14)

            async with async_session() as session:
                async with session.begin():
                    # Helper function to perform count queries
                    async def get_count(model, start_date, end_date=None):
                        query = select(func.count()).select_from(model).filter(
                            model.create_time >= start_date,
                            model.create_time < end_date if end_date else True
                        )
                        result = await session.execute(query)
                        return result.scalar()

                    # Query for the current week data
                    api_data_current = await get_count(InterFaceCaseModel, date)
                    api_task_current = await get_count(InterfaceTask, date)
                    ui_data_current = await get_count(UICaseModel, date)
                    ui_task_current = await get_count(UITaskModel, date)

                    # Query for the previous week data
                    api_data_previous = await get_count(InterFaceCaseModel, two_weeks_ago_date, date)
                    api_task_previous = await get_count(InterfaceTask, two_weeks_ago_date, date)
                    ui_data_previous = await get_count(UICaseModel, two_weeks_ago_date, date)
                    ui_task_previous = await get_count(UITaskModel, two_weeks_ago_date, date)

                    # Calculate growth percentage
                    statistics["apis"] = api_data_current
                    statistics["api_task"] = api_task_current
                    statistics["uis"] = ui_data_current
                    statistics["ui_task"] = ui_task_current

                    statistics["apis_growth"] = calculate_growth(api_data_current, api_data_previous)
                    statistics["api_task_growth"] = calculate_growth(api_task_current, api_task_previous)
                    statistics["uis_growth"] = calculate_growth(ui_data_current, ui_data_previous)
                    statistics["ui_task_growth"] = calculate_growth(ui_task_current, ui_task_previous)
            log.debug(statistics)
            return statistics

        except Exception as e:
            log.error(f"An unexpected error occurred in week_data: {e}", exc_info=True)
            raise


def calculate_growth(current, previous):
    if current == 0 and previous == 0:
        return 0

    if previous > 0:
        return round(((current - previous) / previous), 2) * 100

    return 0


def _format_task_data(task_datas, task_type):
    TASK_TYPES = {
        "API": {
            "total_name": "总构建数量",
            "success_name": "成功数量",
            "fail_name": "失败数量"
        },
        "UI": {
            "total_name": "总构建数量",
            "success_name": "成功数量",
            "fail_name": "失败数量"
        }
    }

    formatted_data = []
    for row in task_datas:
        date_str = row.date.strftime("%Y-%m-%d")
        formatted_data.append(
            {"date": date_str, "name": TASK_TYPES[task_type]["total_name"], "num": int(row.total_num)})
        formatted_data.append(
            {"date": date_str, "name": TASK_TYPES[task_type]["success_name"], "num": int(row.success_num)})
        formatted_data.append({"date": date_str, "name": TASK_TYPES[task_type]["fail_name"], "num": int(row.fail_num)})
    return formatted_data


