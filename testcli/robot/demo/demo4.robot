*** Settings ***
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
Test Setup       TestCli Test Setup
Test Teardown    TestCli Test Clnup

*** Test Cases ***
Demo1
    [Documentation]                          TestCli基于Robot测试样例
    Execute TestCli Script With Reference    demo4.sql    demo4.log   demo4.ref

