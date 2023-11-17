*** Settings ***
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
Test Setup       TestCli Test Setup
Test Teardown    TestCli Test Clnup

*** Test Cases ***
Demo1
    [Documentation]                          TestCli基于Robot测试样例
    Execute Python Script                    demo5.py
    Execute Pytest Script                    demo6.py



