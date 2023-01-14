rd /s/q build
rd /s/q dist
python setup.py sdist
python setup.py bdist_wheel --universal
pip uninstall --yes robotslacker_testcli
python setup.py install
rd /s/q build
REM twine upload dist/*
