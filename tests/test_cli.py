from aioskd.cli import skd


def test_incorect_type_of_path_skd(click_CLI):
    result = click_CLI.invoke(skd, ["some.path.to.obj"])
    assert isinstance(result.exception, ValueError)
    assert "Incorrect Type of path to object" in str(result.exception)
    result = click_CLI.invoke(skd, ["some/path/to/obj"])
    assert isinstance(result.exception, ValueError)
    assert "Incorrect Type of path to object" in str(result.exception)


def test_not_exist_path(click_CLI):
    result = click_CLI.invoke(skd, ["some/path/to/obj:test"])

    assert isinstance(result.exception, SystemExit)
    assert "Error: Invalid value for 'APP': Path 'some/path/to/obj.py' does not exist." in str(result.output)


def test_exsist_path_but_incorent_path_to_obj(click_CLI, tmp_path):
    path = tmp_path / "test.py"
    path = f"{str(path).replace('.py', '')}"
    result = click_CLI.invoke(skd, [path])

    assert isinstance(result.exception, ValueError)
    assert "Incorrect Type of path to object" in str(result.exception)


def test_exsist_path(click_CLI, tmp_path):
    path = tmp_path / "test.py"
    path.write_text("""from aioskd.scheduler import Scheduler\nskd = Scheduler()""")

    path = f"{str(path).replace('.py', '')}"
    result = click_CLI.invoke(skd, [ f"{path}:skd" ])
    assert "Tasks completed successfully" in str(result.output)


def test_file_with_task(click_CLI, tmp_path):
    path = tmp_path / "test.py"
    path.write_text("""import datetime\nfrom aioskd.scheduler import Scheduler\nskd = Scheduler()\n@skd.schedule(interval=datetime.timedelta(seconds=1), repeat=False)\nasync def test_func():\n\tprint("hello world")""")
    path = f"{str(path).replace('.py', '')}"
    result = click_CLI.invoke(skd, [ f"{path}:skd" ])
    output = str(result.output)
    assert "Tasks completed successfully" in str(output)
    assert "hello world" in str(output)
