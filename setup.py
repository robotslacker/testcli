# -*- coding: utf-8 -*-
import ast
import re
from io import open
from time import strftime, localtime
from setuptools import setup

'''
How to build and upload this package to PyPi
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
    version = version + "." + strftime("%Y%m%d%H%M%S", localtime())


def open_file(filename):
    """Open and read the file *filename*."""
    with open(filename, 'r+', encoding='utf-8') as rf:
        return rf.read()


readme = open_file("testcli/docs/UserGuide.md")

install_requires = ['JPype1', 'setproctitle', 'urllib3',
                    'click', 'prompt_toolkit', 'paramiko', 'antlr4-python3-runtime==4.11.1',
                    'fs', "psutil", "glom", "hdfs",
                    "python-multipart", "pytest-xdist", "pytest", 'fastapi', 'uvicorn',
                    "coloredlogs", "robotframework", "beautifulsoup4", "lxml",
                    ]

setup(
    name='robotslacker-testcli',
    version=version,
    description='Test Command tool',
    long_description=readme,
    keywords='test command sql api',
    long_description_content_type='text/markdown',
    platforms='any',
    install_requires=install_requires,
    author='RobotSlacker',
    author_email='184902652@qq.com',
    url='https://github.com/robotslacker/testcli.git',

    zip_safe=False,
    packages=['testcli'],
    package_data={'testcli': [
        'jlib/*',
        'conf/*',
        'profile/*',
        'antlr/*.g4',
        'antlrgen/*',
        'commands/*',
        'plugin/*',
        'test/*',
        'docs/*',
        'htmldiff/*', 'htmldiff/*/*',
        "robot/*", "robot/*/*", "robot/*/*", "robot/*/*/*", "robot/*/*/*/*",
    ]},
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "testcli = testcli.cliconsole:cli",
            "testclicomp = testcli.clicomp:cli",
            "testclirobot = testcli.clirobot:cli",
        ],
        "distutils.commands": ["lint = tasks:lint", "test = tasks:test"],
    },
)
