import datetime
import asyncio
import pytest


def test_schedule_of_scheduler_method(scheduler, async_function):
    # Decorator
    task = scheduler.schedule(interval=datetime.timedelta(minutes=5))(async_function)

    assert task in scheduler.tasks
    assert task.task == async_function
    assert task.interval == datetime.timedelta(minutes=5)


def test_exception_in_schedule_method(scheduler):

    def test_function():
        print("hello world")

    with pytest.raises(ValueError) as err:
        # Decorator over the isn't couroutine function
        task = scheduler.schedule(interval=datetime.timedelta(minutes=5))(test_function)
    assert "Function under decorator must be await. Use 'async def' syntax" in str(err.value)


def test_run_in_scheduler(scheduler):
    # run without tasks
    assert scheduler.run() == None

def test_run_without_repeat(scheduler, scheduled_task):
    scheduled_task.repeat = False
    assert scheduler.run() == None


def test_repr_in_task(scheduled_task, async_function):
    assert repr(scheduled_task) in f"<SchedulerTask task={async_function.__name__} every {scheduled_task.interval}"


def test_immediate_attr_in_task(scheduler, async_function):
    task = scheduler.schedule(interval=datetime.timedelta(minutes=5), immediate=True)(async_function)
    # Test that if arg immediate True task have to start immediatly
    difference_of_time = (task.time_to - datetime.datetime.now()).total_seconds()
    assert int(difference_of_time) == 0


def test_time_to_is_time_now_plus_interval_in_task(scheduled_task):
    time_start = datetime.datetime.now()
    setted_time = scheduled_task.set_time()
    difference_of_time = (setted_time-time_start).total_seconds()
    # Test that set_time method set time to like datetime.datetime.now() + interval
    assert int(difference_of_time) == int(scheduled_task.interval.total_seconds())
    assert scheduled_task.time_to == setted_time


@pytest.mark.asyncio
async def test_time_to_do_in_task(scheduled_task):
    scheduled_task.interval = datetime.timedelta(seconds=1)
    scheduled_task.set_time()
    # test that time_to_do return right bool answers
    assert not scheduled_task.time_to_do()
    await asyncio.sleep(1)
    assert scheduled_task.time_to_do()


@pytest.mark.asyncio
async def test_wait_for_interval_method_in_task(scheduled_task):
    scheduled_task.interval = datetime.timedelta(seconds=1)
    # Test that wait_fo_interval raise error
    with pytest.raises(RuntimeError) as err:
        await scheduled_task.wait_for_interval()
    assert "set_time() must be called" in str(err.value)

    time_start = datetime.datetime.now()
    scheduled_task.set_time()
    # Test that wait_fo_interval wait correctly
    await scheduled_task.wait_for_interval()
    difference_of_time = (datetime.datetime.now()-time_start).total_seconds()
    assert int(difference_of_time) == int(scheduled_task.interval.total_seconds())


@pytest.mark.asyncio
async def test_iter_count_without_repeat(scheduler, async_function):
    with pytest.raises(ValueError) as err:
        scheduler.schedule(interval=datetime.timedelta(seconds=1), repeat=False, iter_count=5)(async_function)

    assert "If you want to repeat set arg repeat=True" in str(err.value)
    task = scheduler.schedule(interval=datetime.timedelta(seconds=1), iter_count=5)(async_function)
    assert task.repeat == True
    assert task.iter_count == 5


def test_next_iter(scheduled_task):
    task_counts = scheduled_task.count
    scheduled_task.next_iter()
    assert scheduled_task.count == task_counts + 1


def test_simple_task_with_iter_count(scheduler, async_function, capsys):

    task = scheduler.schedule(interval=datetime.timedelta(seconds=1), iter_count=2)(async_function)

    assert scheduler.run() == None
    assert "Hello world" in capsys.readouterr().out.strip()


def test_create_task_witout_decorator(scheduler, async_function, capsys):
    task = scheduler.register_task(async_function)
    with pytest.raises(ValueError) as err:
        scheduler.run()

    assert "Task must be scheduled before running. Use task.schedule(interval: datetime.timedelta)" in str(err.value)

    task.schedule(interval=datetime.timedelta(seconds=5), repeat=False)
    assert scheduler.run() == None
    assert "Hello world" in capsys.readouterr().out.strip()

def test_create_task_with_args_without_decorator(scheduler, capsys):

    async def test_args(a: int, *args, b: str = "some", **kwargs):
        print("a")
        print(args)
        for i in args:
            print(f"arg in args: {i}")
        print(b)
        print(kwargs)
        for i in kwargs:
            print(f"{i} = {kwargs[i]}")

    task = scheduler.register_task(test_args, 5, 3, 4, 23, 3, b="yes", name="Robert", age=25)

    with pytest.raises(ValueError) as err:
        scheduler.run()

    assert "Task must be scheduled before running. Use task.schedule(interval: datetime.timedelta)" in str(err.value)
    task.schedule(interval=datetime.timedelta(seconds=5), repeat=False)
    assert scheduler.run() == None
    out = capsys.readouterr().out.strip()
    assert "age = 25" in out
    assert "name = Robert" in out
    assert "5" in out
    assert "arg in args: 23" in out
    assert "yes" in out
