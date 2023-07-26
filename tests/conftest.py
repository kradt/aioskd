import pytest
import asyncio
import datetime
from click.testing import CliRunner

from aioskd import Scheduler


@pytest.fixture(scope="function")
def scheduler():
    skd = Scheduler()
    yield skd


@pytest.fixture(scope="function")
def async_function():

    async def func_for_test():
        print("Hello world")
        await asyncio.sleep(1)

    yield func_for_test


@pytest.fixture(scope="function")
def task(scheduler, async_function):
    yield scheduler.schedule(interval=datetime.timedelta(seconds=1))(async_function)
    scheduler.tasks = []
    

@pytest.fixture(scope="function")
def click_CLI():
    yield CliRunner()
