import sys
import click
from importlib.machinery import SourceFileLoader


sys.path.append(".")

class CustomPath(click.Path):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convert(self, value, param, ctx) -> tuple:
        """
            Validate and check if path exist
        """
        splited_path = value.split(":")
        path, obj = splited_path if len(splited_path) == 2 else [None, None]
        if not path or not obj:
            raise ValueError("Incorrect Type of path to object")
        filename = path.split("/")[-1]
        converted_path = super().convert(path + ".py", param, ctx)
        
        return converted_path, filename, obj


@click.command()
@click.option("--app", "-A", help="path to file with tasks in simple format", type=CustomPath(exists=True))
def schedule(app):
 
    """Start work task's scheduler

        \b
        Example:
            my_project/src/run:app
        \b
        Where:
            my_project/src - path to module,
            run.py - your module,
            app - object of Scheduler class"
            
    """
    path, name, obj = app
    
    # Find import and execute module with tasks
    module = SourceFileLoader(name, path).load_module()

    # Start Scheduler
    scheduler = getattr(module, obj)
    scheduler.run()

if __name__ == "__main__":
    schedule()