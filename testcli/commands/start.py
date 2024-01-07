# -*- coding: utf-8 -*-
import os
import re
import codecs
import time
import traceback
from ..globalvar import globalEmbeddScriptScope


# 从文件中执行SQL
def executeFile(cls, scriptFile, argv):
    # 将scriptFile根据平台进行转义
    try:
        if str(scriptFile).startswith("'"):
            scriptFile = scriptFile[1:]
        if str(scriptFile).endswith("'"):
            scriptFile = scriptFile[:-1]
        with open(
                file=os.path.expanduser(scriptFile),
                mode="r",
                encoding=cls.testOptions.get("SCRIPT_ENCODING")) as f:
            query = f.read()

        # 空文件直接返回
        if len(query) == 0:
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return

        # 将程序的参数记录到环境信息中
        localargv = [scriptFile]
        localargv.extend(argv)
        globalEmbeddScriptScope["argv"] = localargv

        # 处理脚本文件头数据, 文件开头的0xFEFF,codecs.BOM_UTF8忽略不看
        if ord(query[0]) == 0xFEFF:
            # 去掉脚本文件可能包含的UTF-BOM
            query = query[1:]
        if query[:3] == codecs.BOM_UTF8:
            # 去掉脚本文件可能包含的UTF-BOM
            query = query[3:]

        # Scenario, Transaction等Hint信息不会带入到下一个脚本文件中
        cls.cmdExecuteHandler.scenario = ''
        cls.cmdExecuteHandler.transaction = ''
        cls.cmdExecuteHandler.setStartTime(time.time())

        # 这里需要把command按照namespace分离，即不同的namespace分开执行
        # 避免切换namespace后，解析导致的问题
        # 其中：
        #   __use__ namespace 为一段
        #   两个 __use__ namespace之间为一段
        commandList = []
        lastCommand = None
        lastNameSpace = cls.nameSpace
        for commandLine in query.split("\n"):
            match_obj = re.match(r"(\s+)?__USE__(\s+)NAMESPACE(\s+)(.*)$",
                                 commandLine, re.IGNORECASE | re.DOTALL)
            if match_obj:
                newNameSpace = match_obj.group(4).strip().upper()
                if lastCommand is not None:
                    commandList.append({"nameSpace": lastNameSpace, "script": lastCommand})
                    lastCommand = None
                commandList.append({"nameSpace": "GENERAL", "script": commandLine})
                lastNameSpace = newNameSpace
                lastNameSpace = lastNameSpace.strip().upper().strip(';')
                continue
            else:
                if lastCommand is None:
                    lastCommand = commandLine
                else:
                    lastCommand = lastCommand + "\n" + commandLine
        if lastCommand is not None:
            commandList.append({"nameSpace": lastNameSpace, "script": lastCommand})

        # 分段执行执行的语句
        for command in commandList:
            for executeResult in \
                    cls.cmdExecuteHandler.runStatement(
                        statement=command["script"],
                        commandScriptFile=os.path.expanduser(scriptFile),
                        nameSpace=command["nameSpace"]
                    ):
                yield executeResult
    except IOError as e:
        if "TESTCLI_DEBUG" in os.environ:
            print('traceback.print_exc():\n%s' % traceback.print_exc())
            print('traceback.format_exc():\n%s' % traceback.format_exc())
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Execute script [" + str(os.path.abspath(scriptFile)) + "] failed. " + repr(e)
        }
