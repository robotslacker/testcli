*** Settings ***
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
Test Setup       TestCli Test Setup
Test Teardown    TestCli Test Clnup

*** Test Cases ***
Demo1
    [Documentation]            TestCli基于Robot测试样例
    Execute TestCli Script     demo3.sql    demo3.log
    Compare Files              demo3.log    demo3.ref
