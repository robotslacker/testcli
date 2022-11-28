del /s/q dist\*
del /s/q build\*
python setup.py sdist
python setup.py bdist_wheel --universal
pip uninstall --yes robotslacker_testcli
python setup.py install
REM twine upload dist/*
