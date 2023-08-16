import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Callable, List, Optional

import pytz

from custom_exceptions import TimerValueException, TimerStarted, TimerNotStarted


def timer_init(data, callback, *args, **kwargs):
    start_time = end_time = end_date = days_of_week = None
    if data.get('start') and data.get('end'):
        start_time = datetime.strptime(data.get('start'), '%H:%M:%S').time()
        end_time = datetime.strptime(data.get('end'), '%H:%M:%S').time()
    else:
        raise TimerValueException('Нету времени начала или окончания')
    if data.get('end_date_notify'):
        end_date = datetime.strptime(data.get('end_date_notify'), '%Y-%m-%d').date()
    if data.get('day_of_week'):
        days_of_week = data.get('day_of_week')

    return RepeatTimer(interval=data['interval'],
                       callback=callback,
                       tz=data['time_zone'],
                       start_time=start_time,
                       end_time=end_time,
                       end_date=end_date,
                       days_of_week=days_of_week,
                       *args,
                       **kwargs)


class RepeatTimer:
    def __init__(self,
                 interval: int,
                 callback: Callable,
                 tz: str,
                 start_time: Optional[datetime.time] = None,
                 end_time: Optional[datetime.time] = None,
                 days_of_week: Optional[List[int]] = None,
                 end_date: Optional[datetime.date] = None,
                 *args,
                 **kwargs):
        self.interval = interval
        self.callback = callback
        self.tz = tz
        self.start_time = start_time
        self.end_time = end_time
        self.days_of_week = days_of_week
        self.end_date = end_date
        self.args = args
        self.kwargs = kwargs
        self._task = None
        self.logger = logging

    async def start(self) -> None:
        if self._task is not None:
            raise TimerStarted('Timer already running')

        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            raise TimerNotStarted('Timer not running')

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def _run(self) -> None:
        while True:
            now = datetime.now() + pytz.timezone(self.tz).utcoffset(datetime.now())
            if self.end_date and now.date() > self.end_date:
                break

            if self.days_of_week and now.weekday() not in self.days_of_week:
                time_of_day = now - datetime.strptime(str(now.date()), "%Y-%m-%d")
                await asyncio.sleep((timedelta(hours=24) - time_of_day).seconds)
                continue

            current_time = now.time()
            if self.start_time and current_time < self.start_time:
                await asyncio.sleep(self._get_sleep_time(current_time))
                continue

            if self.end_time and current_time > self.end_time:
                await asyncio.sleep(self._get_sleep_time(current_time))
                continue

            try:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(*self.args, **self.kwargs)
                else:
                    self.callback(*self.args, **self.kwargs)
            except Exception as e:
                self.logger.exception(f'Callback error {e}')
            await asyncio.sleep(self.interval)

    async def run_once(self, delay) -> None:
        await asyncio.sleep(delay)
        if asyncio.iscoroutinefunction(self.callback):
            await self.callback(*self.args, **self.kwargs)
        else:
            self.callback(*self.args, **self.kwargs)

    def _get_sleep_time(self, current_time: time) -> int:
        return (datetime.strptime(str(self.start_time), "%H:%M:%S") -
                datetime.strptime(str(current_time), "%H:%M:%S.%f")).seconds + 1
