import asyncio
import datetime
from typing import Callable
import functools
from inspect import iscoroutinefunction


class SchedulerTask:
    """
        A class that displays the task of the scheduler
        :param task: Asynchronous function to be executed
        :param interval: The interval between which the asynchronous function should be executed
        :param repeat: Indicates whether the asynchronous function should be repeated or executed once
        :param immediate: If yes, the scheduler will not wait for the interval when starting the task for the FIRST TIME
        :param iter_count: necessary number of repeats

    """
    def __init__(
            self,
            task: Callable,
            interval: datetime.timedelta | None = None,
            immediate: bool = False,
            repeat: bool = True,
            iter_count: int | None = None) -> None:
        
        self.task = task
        self.interval = interval
        self.count = 0
        self.repeat = repeat
        self.iter_count = iter_count
        if self.iter_count and not self.repeat:
            raise ValueError("If you want to repeat set arg repeat=True")

        self.immediate = immediate
        if self.immediate:
            self.time_to = datetime.datetime.now()
        else:
            self.time_to = None

    def schedule(
            self,
            interval: datetime.timedelta,
            immediate: bool = False,
            repeat: bool = True,
            iter_count: int | None = None) -> None:
        
        self.__init__(task=self.task, interval=interval, immediate=immediate, repeat=repeat, iter_count=iter_count)

    def next_iter(self):
        self.count += 1
        self.set_time()

    def set_time(self) -> datetime.datetime:
        """
            Sets the time at which the self.task should be executed
        """
        if not self.interval:
            raise ValueError("Task must be scheduled before running. Use task.schedule(interval: datetime.timedelta)")

        self.time_to = datetime.datetime.now() + self.interval
        return self.time_to

    async def wait_for_interval(self) -> None:
        if not self.time_to:
            raise RuntimeError("set_time() must be called")
        
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
        return f"<SchedulerTask task={self.task.__name__} every {self.interval}"


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
                if not task.repeat or task.count == task.iter_count:
                    break
                task.next_iter()

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

    def schedule(
            self,
            interval: datetime.timedelta,
            immediate: bool = False,
            repeat: bool = True, iter_count: int | None = None) -> Callable:
        """
            Decorator that collects all the coroutines that need to be executed with time scheduling

            :param interval: The interval between which the asynchronous function should be executed
            :param repeat: Indicates whether the asynchronous function should be repeated or executed once
            :param immediate: If yes, the scheduler will not wait for the interval when starting the task for the FIRST TIME
            :param iter_count: necessary number of repeats
        """
        def wrapper(func) -> None:
            """
                :param func: Asynchronous function to be performed
            """
            if not iscoroutinefunction(func):
                raise ValueError("Function under decorator must be await. Use 'async def' syntax")
            task = SchedulerTask(task=func, interval=interval, repeat=repeat, immediate=immediate, iter_count=iter_count)
            self.tasks.append(task)
            return task

        return wrapper
    
    def register_task(self, task: Callable, *args, **kwargs) -> SchedulerTask:
        """
            Register a new task without scheduling it.

            This method allows you to manually create a task without using the 'schedule' decorator.
            The task can later be scheduled

            :param task: The asynchronous function to be performed as the task.
            :param *args: Positional arguments to be passed to the task function when it is executed.
            :param **kwargs: Keyword arguments to be passed to the task function when it is executed.
            :return: A SchedulerTask object representing the registered task.
            :rtype: SchedulerTask
        """
        partial_task = functools.partial(task, *args, **kwargs)
        functools.update_wrapper(partial_task, task)
        
        new_task = SchedulerTask(task=partial_task)
        self.tasks.append(new_task)
        return new_task

    def run(self) -> None:
        asyncio.run(self._run_with_interval())
