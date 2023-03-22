# -*- coding: utf-8 -*-

import ast
import re
from io import open
from setuptools import setup

'''
How to build and upload this package to PyPi
    python setup.py sdist
    python setup.py bdist_wheel --universal
    twine upload dist/*

How to build and upload this package to Local site:
    python setup.py install
'''


_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("testcli/__init__.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )


def open_file(filename):
    """Open and read the file *filename*."""
    with open(filename, 'r+', encoding='utf-8') as rf:
        return rf.read()


readme = open_file("testcli/docs/UserGuide.md")

setup(
    name='robotslacker-testcli',
    version=version,
    description='Test Command tool',
    long_description=readme,
    keywords='test command sql api',
    long_description_content_type='text/markdown',
    platforms='any',
    install_requires=['JPype1', 'setproctitle', 'urllib3<1.27',
                      'click', 'prompt_toolkit',  'paramiko', 'antlr4-python3-runtime==4.11.1',
                      'hdfs', 'fs', "psutil",
                      "python-multipart",
                      "pytest", 'fastapi', 'uvicorn', "pytest-xdist",
                      "coloredlogs", "robotframework", "beautifulsoup4", "lxml"
                      ],

    author='RobotSlacker',
    author_email='184902652@qq.com',
    url='https://github.com/robotslacker/testcli.git',

    zip_safe=False,
    packages=['testcli'],
    package_data={'testcli': [
        'jlib/*',
        'conf/*', 'profile/*',
        'antlrgen/*', 'commands/*',
        'test/*',
        'docs/UserGuide.md',
        'docs/robotslacker.jpg',
    ]},
    python_requires='>=3.6',
    entry_points={
        "console_scripts": ["testcli = testcli.main:cli"],
        "distutils.commands": ["lint = tasks:lint", "test = tasks:test"],
    },
)
