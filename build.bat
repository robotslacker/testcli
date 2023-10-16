rd /s/q build
rd /s/q dist
REM python setup.py sdist
python setup.py bdist_wheel --universal
pip uninstall --yes robotslacker_testcli
for %%f in (dist\robotslacker_testcli*.whl) do (
    pip install %%f
)
rd /s/q build
REM twine upload dist/*
