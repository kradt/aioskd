# aioskd - Asynchronous Background Task Scheduler
[![PyPI version](https://img.shields.io/pypi/v/aioskd.svg)](https://pypi.org/project/aioskd/)
![License](https://img.shields.io/github/license/kradt/aioskd)
[![codecov](https://codecov.io/gh/kradt/aioskd/branch/main/graph/badge.svg?token=P0YWHFXKQP)](https://codecov.io/gh/kradt/aioskd)
[![tests](https://github.com/kradt/aioskd/actions/workflows/ci_tests.yml/badge.svg)](https://github.com/kradt/aioskd/actions/workflows/ci_tests.yml)


aioskd is a powerful tool for executing background tasks asynchronously at scheduled intervals. It features a flexible scheduler that can be easily adapted to suit the user's specific needs.

## Features

- Asynchronous execution of background tasks
- Customizable scheduling of tasks at specified intervals
- Easy-to-use API for integrating with your Python projects
- Lightweight and efficient

## Installation

You can install `aioskd` using pip:

```bash
pip install aioskd
```

## Usage

### Creating the Scheduler

To get started, import the necessary modules and create an instance of the `Scheduler` class:

```python
from aioskd import Scheduler


skd = Scheduler()
```

### Scheduling Tasks

You can now schedule tasks using the `schedule` decorator. 

```python
import datetime
import asyncio  


@skd.schedule(interval=datetime.timedelta(seconds=1))
async def task_one():
    print("Task One - Hello world!")     
    await asyncio.sleep(2)  
    # Simulate some async work taking 2 seconds  
	

@skd.schedule(interval=datetime.timedelta(seconds=5))
async def task_two():
    print("Task Two - I'm running every 5 seconds!")
    await asyncio.sleep(1) 
    # Simulate some async work taking 1 second
```


In this example, `task_one` will be executed every 1 second, and `task_two` will be executed every 5 seconds.

### Running the Scheduler

To start the scheduler and run the scheduled tasks, you can use the `run()` method:

```python
skd.run()
```

### Command Line Usage

If you want to run the scheduled tasks from the command line, you can use the following command:

```bash
skd path/to/file/with/tasks:obj_of_skd
```

## Examples

### Example 1: Scheduling a Task to Fetch Data

```python
import datetime
import asyncio
import aiohttp
from aioskd import Scheduler


skd = Scheduler()

@skd.schedule(interval=datetime.timedelta(minutes=30))
async def fetch_data():
    url = "https://api.example.com/data"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json() 
		# Process and store the data as needed 
		print("Data fetched successfully!") 
            else:
		print("Failed to fetch data. Status code:", response.status)


if __name__ == "__main__":
    skd.run()
```
	
In this example, the `fetch_data` task is scheduled to run every 30 minutes. It sends a request to an API to fetch data and then processes the response accordingly.

### Example 2: Sending Scheduled Reminder Emails

```python
import datetime
import asyncio
import aiosmtplib
from email.message import EmailMessage
from aioskd import Scheduler


skd = Scheduler() 

@skd.schedule(interval=datetime.timedelta(hours=24))
async def send_reminder_email():
    email_content = "Hello! Just a friendly reminder that your appointment is tomorrow."
    msg = EmailMessage()
    msg.set_content(email_content)
    msg["Subject"] = "Appointment Reminder"
    msg["From"] = "your_email@example.com"
    msg["To"] = "recipient@example.com" 
    async with aiosmtplib.SMTP("smtp.example.com", 587) as server:
	await server.starttls()
	await server.login("your_email@example.com", "your_email_password")
	await server.send_message(msg)

if __name__ == "__main__":
    skd.run()
```

This example schedules the `send_reminder_email` task to run once every 24 hours, sending a reminder email to a specified recipient about an upcoming appointment.

### `schedule` Decorator

- **interval**: `datetime.timedelta` 
	- The interval between which the asynchronous function should be executed. 
- **repeat**: `bool` 
	- A flag that indicates whether the asynchronous function should be repeated or executed only once. - If set to `True`, the function will be scheduled to run repeatedly at the specified interval. - If set to `False`, the function will be executed only once. 
- **immediate**: `bool` 
	- A flag that controls the first execution of the scheduled function. - If set to `True`, the scheduler will execute the function immediately when starting the task for the FIRST TIME, and subsequent executions will be based on the interval. - If set to `False`, the first execution will wait for the interval before running. 
- **iter_count** (optional): `int` 
	- The necessary number of repeats. This parameter is applicable only when `repeat` is `True`. - It specifies the maximum number of times the function should be repeated. - If not provided, the function will continue to be repeated indefinitely until the scheduler is stopped or the coroutine is cancelled.

## Contributing

If you'd like to contribute to this project, follow these steps:

1. Fork the repository and create a new branch.
2. Make your changes and test them thoroughly.
3. Submit a pull request, explaining the changes you've made.
