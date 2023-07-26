from setuptools import setup, find_packages


def get_readme():
    with open("README.md", "r") as file:
        return file.read()


setup(
  name='aioskd',
  version='0.0.6',
  author='Artem Sydorenko',
  author_email='kradworkmail@gmail.com',
  description='Tool for execute async background tasks',
  long_description=get_readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=['click==8.1.3'],
  classifiers=[
    'Programming Language :: Python :: 3.11'
  ],
  entry_points='''
        [console_scripts]
        skd=aioskd.cli:skd
  ''',
  keywords='async, scheduling, background-tasks, asynchronous-programming, scheduler-library, python, task-scheduler, background-processing, concurrency, asyncio, timed-tasks, library, python3, interval-tasks, task-scheduling, asynchronous-background-tasks, background-scheduler, background-jobs, background-execution, task-execution, scheduling-tasks, async-jobs, async-tasks, job-scheduler, task-runner, task-manager',
  python_requires='>=3.11'
)