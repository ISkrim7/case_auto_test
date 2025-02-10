from typing import TypeVar

from sqlalchemy import select, and_
from sqlalchemy.sql.functions import count, func

from app.mapper import Mapper
from app.mapper.interface import InterfaceCaseMapper
from app.mapper.ui.uiCaseMapper import UICaseMapper
from app.model import async_session, BaseModel
from app.model.interface import InterFaceCaseModel, InterfaceTask
from app.model.ui import UICaseModel, UITaskModel
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

                    log.debug(f"Current API data count: {api_data_current}")
                    log.debug(f"Current API task count: {api_task_current}")
                    log.debug(f"Current UI data count: {ui_data_current}")
                    log.debug(f"Current UI task count: {ui_task_current}")

                    # Calculate growth percentage
                    statistics["apis"] = api_data_current
                    statistics["api_task"] = api_task_current
                    statistics["uis"] = ui_data_current
                    statistics["ui_task"] = ui_task_current

                    def calculate_growth(current, previous):
                        log.debug(current)
                        log.debug(previous)
                        if current == 0 and previous == 0:
                            return 0
                        if previous > 0:
                            return ((current - previous) / previous) * 100
                        return 0

                    statistics["apis_growth"] = calculate_growth(api_data_current, api_data_previous)
                    statistics["api_task_growth"] = calculate_growth(api_task_current, api_task_previous)
                    statistics["uis_growth"] = calculate_growth(ui_data_current, ui_data_previous)
                    statistics["ui_task_growth"] = calculate_growth(ui_task_current, ui_task_previous)
            log.debug(statistics)
            return statistics

        except Exception as e:
            log.error(f"An unexpected error occurred in week_data: {e}", exc_info=True)
            raise


