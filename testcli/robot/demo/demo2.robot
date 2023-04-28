*** Settings ***
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
Test Setup       TestCli Test Setup
Test Teardown    TestCli Test Clnup

*** Test Cases ***
Demo1
    [Documentation]            TestCli基于Robot测试样例
    Execute TestCli Script     demo2.sql    demo2.log
    Compare Files              demo2.log    demo2.ref
