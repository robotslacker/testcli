# -*- coding: utf-8 -*-
import sys
import subprocess
from testcli.testcliexception import TestCliException


# 执行主机的操作命令
def executeLocalCommand(cls, command: str):
    if 'win32' in str(sys.platform).lower():
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        print("Will execute [" + str(command) + "]")
        p = subprocess.Popen(command,
                             shell=True,
                             startupinfo=startupinfo,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    else:
        p = subprocess.Popen(command,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    try:
        (stdoutdata, stderrdata) = p.communicate()
        summaryStatus = str(stdoutdata.decode(encoding=cls.testOptions.get("RESULT_ENCODING")))
        if len(str(stderrdata.decode(encoding=cls.testOptions.get("RESULT_ENCODING")))) != 0:
            summaryStatus = summaryStatus + "\n" + \
                            str(stderrdata.decode(encoding=cls.testOptions.get("RESULT_ENCODING")))
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": summaryStatus
        }
    except UnicodeDecodeError:
        raise TestCliException("The character set [" + cls.testOptions.get("RESULT_ENCODING") + "]" +
                               " does not match the terminal character set, " +
                               "so the terminal information cannot be output correctly.")
