rd /s/q build
rd /s/q dist
python setup.py sdist
python setup.py bdist_wheel --universal
pip uninstall --yes robotslacker_testcli
pip install dist/robotslacker_testcli-0.0.27-py2.py3-none-any.whl
rd /s/q build
REM twine upload dist/*
