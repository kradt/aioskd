from setuptools import setup, find_packages


def get_readme():
    with open("README.md", "r") as file:
        return file.read()


setup(
  name='aioskd',
  version='0.0.4',
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
        schedule=scheduler.cli:schedule
  ''',
  keywords='background tasks asyncio async',
  python_requires='>=3.11'
)