import sys
import click
from importlib.util import spec_from_file_location, module_from_spec


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
@click.argument("app", type=CustomPath(exists=True))
def skd(app):
 
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
    

    # Create a spec for the module from the given file path
    spec = spec_from_file_location(name, path)
    # Create the module from the spec
    module = module_from_spec(spec)
    # Load and execute the module
    spec.loader.exec_module(module)

    # Start Scheduler
    scheduler = getattr(module, obj)
    scheduler.run()
    click.echo("Tasks completed successfully")

if __name__ == "__main__": # pragma: no cover
    skd()