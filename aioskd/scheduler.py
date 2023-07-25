import asyncio
import datetime
from typing import Callable
from inspect import iscoroutinefunction


class SchedulerTask:
    """
        A class that displays the task of the scheduler
        :param task: Asynchronous function to be executed
        :param interval: The interval between which the asynchronous function should be executed
        :param repeat: Indicates whether the asynchronous function should be repeated or executed once
        :param immediate: If yes, the scheduler will not wait for the interval when starting the task for the FIRST TIME
    """
    def __init__(self, task: Callable, interval: datetime.timedelta, repeat: bool = True, immediate: bool = False) -> None:
        self.task = task
        self.interval = interval
        self.repeat = repeat
        self.immediate = immediate

        if self.immediate:
            self.time_to = datetime.datetime.now()
        else:
            self.time_to = None

    def set_time(self) -> None:
        """
            Sets the time at which the self.task should be executed
        """
        self.time_to = datetime.datetime.now() + self.interval

    async def wait_for_interval(self) -> None:
        amount_of_time = self.time_to - datetime.datetime.now()

        await asyncio.sleep(amount_of_time.total_seconds())

    def time_to_do(self) -> bool:
        """
            Returns True if it is time to execute self.task
        """
        if self.time_to and datetime.datetime.now() >= self.time_to:
            return True
        return False

    def __repr__(self):
        return f"<SchedulerTask task={self.task}"


class Scheduler:
    """
        A scheduler class that is used to perform background tasks in another process.
        
        Problem: 
            I had an asynchronous parsing system that I was thinking of using with celery beat, but celery doesn't work with asyncio yet.
            Unfortunately, I did not find a ready-made solution that would suit me on the Internet, so I decided to implement a scheduler for my own requirements
        
        Solution:
            Create a tool that allows you to run background tasks
            Requirements:
                Support for asyncio 
                Support for concurrent
                Independence from external libraries
                Convenient interaction interface with decorators
    """
    def __init__(self):
        self.tasks = []

    async def _execute_task(self, task: SchedulerTask) -> None:
        """
            A coroutine that checks if it is time to execute the task, if so, executes it, if the task needs to be executed once (repeat), interrupts it, if not, sets a new time
            :param task: The task to be executed
        """
        while True:
            if task.time_to_do():
                await task.task()
                if not task.repeat:
                    break
                task.set_time()

            await task.wait_for_interval()

    def _init_tasks(self) -> None:
        """
           A method that sets the execution time for all tasks that require it
        """
        [task.set_time() for task in self.tasks if not task.time_to]

    async def _run_with_interval(self) -> None:
        """
            Coroutine that creates tasks in which the scheduler tasks will be performed
        """
        self._init_tasks()
        tasks = [asyncio.create_task(self._execute_task(task)) for task in self.tasks]
        await asyncio.gather(*tasks)

    def schedule(self, interval: datetime.timedelta, repeat: bool = True, immediate: bool = False) -> Callable:
        """
            Decorator that collects all the coroutines that need to be executed with time scheduling
            :param interval: The interval between which the asynchronous function should be executed
            :param repeat: Indicates whether the asynchronous function should be repeated or executed once
            :param immediate: If yes, the scheduler will not wait for the interval when starting the task for the FIRST TIME
        """
        def wrapper(func) -> None:
            """
                :param func: Asynchronous function to be performed
            """
            if not iscoroutinefunction(func):
                raise ValueError("Function under decorator must be await. Use 'async def' syntax")
            task = SchedulerTask(task=func, interval=interval, repeat=repeat, immediate=immediate)
            self.tasks.append(task)

        return wrapper

    def run(self) -> None:
        asyncio.run(self._run_with_interval())
