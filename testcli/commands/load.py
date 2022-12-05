# -*- coding: utf-8 -*-
import importlib.util
import os
import re
import sys
from testcli.testcliexception import TestCliException
from testcli.commands.embeddScript import localEmbeddScriptScope

pluginModule = {}
pluginFunction = {}


def loadPlugin(cls, pluginFile: str):
    global pluginFunction
    global pluginModule

    # 首先在当前目录下查找
    # 如果找不到，则去程序所在的目录下去寻找
    if not os.path.exists(pluginFile):
        if not os.path.exists(os.path.join(os.path.abspath(__file__), pluginFile)):
            yield {
                "type": "error",
                "message": "plugin file [" + os.path.abspath(pluginFile) + "] does not exist!",
            }
            return
    pluginFileHandler = open(file=pluginFile, mode="r", encoding=cls.testOptions.get("SCRIPT_ENCODING"))
    pluginContents = pluginFileHandler.readlines()

    # 导入plugin的外部模块
    for pluginContent in pluginContents:
        matchObj = re.match(r"^class(\s+)(.*?)(\s+)?[(|:]", pluginContent)
        if matchObj:
            className = str(matchObj.group(2)).strip()
            # 动态导入class
            spec_class = importlib.util.spec_from_file_location(
                name=className,
                location=os.path.abspath(pluginFile)
            )
            module_class = importlib.util.module_from_spec(spec_class)
            spec_class.loader.exec_module(module_class)
            pluginClass = getattr(module_class, className)
            pluginModule[className] = pluginClass
            localEmbeddScriptScope[className] = pluginModule[className]
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": 'Plugin module [' + str(className) + '] loaded successful.'
            }

    # 导入plugin的函数
    for pluginContent in pluginContents:
        matchObj = re.match(r"^def(\s+)(.*?)(\s+)?[(|:]", pluginContent)
        if matchObj:
            funcName = str(matchObj.group(2)).strip()
            # 动态导入Function
            spec_function = importlib.util.spec_from_file_location(
                name=funcName,
                location=os.path.abspath(pluginFile)
            )
            module_function = importlib.util.module_from_spec(spec_function)
            spec_function.loader.exec_module(module_function)
            pluginFunc = getattr(module_function, funcName)
            pluginFunction[funcName] = pluginFunc
            localEmbeddScriptScope[funcName] = pluginFunction[funcName]
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": 'Plugin function [' + str(funcName) + '] loaded successful.'
            }
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": 'Plugin file loaded successful.'
    }


# 加载数据库驱动
# 标准的默认驱动程序并不需要使用这个函数，这个函数是用来覆盖标准默认驱动程序的加载信息
def loadDriver(cls, driverName: str, driverFile: str):
    if driverName is None:  # 显示当前的Driver配置
        m_Result = []
        for row in cls.db_connectionConf:
            m_Result.append([row["Database"], row["ClassName"], row["FullName"],
                             row["JDBCURL"], row["ODBCURL"], row["JDBCProp"]])
        yield {
            "type": "result",
            "title": "Current Drivers: ",
            "rows": m_Result,
            "headers": ["Database", "ClassName", "FileName", "JDBCURL", "ODBCURL", "JDBCProp"],
            "columnTypes": None,
            "status": "Driver loaded."
        }
        return

    # 只有一个参数，打印当前Database的Driver情况
    if driverFile is None:
        m_Result = []
        for row in cls.db_connectionConf:
            if row["Database"] == driverName:
                m_Result.append([row["Database"], row["ClassName"], row["FullName"],
                                 row["JDBCURL"], row["ODBCURL"], row["JDBCProp"]])
                break
        yield {
            "type": "result",
            "title": "Current Drivers: ",
            "rows": m_Result,
            "headers": ["Database", "ClassName", "FileName", "JDBCURL", "ODBCURL", "JDBCProp"],
            "columnTypes": None,
            "status": "Driver loaded."
        }
        return
    else:
        if cls.script is None:
            driverFile = os.path.join(sys.path[0], driverFile)
        else:
            driverFile = os.path.abspath(os.path.join(os.path.dirname(cls.script), driverFile))
        if not os.path.isfile(driverFile):
            raise TestCliException("Driver not loaded. file [" + driverFile + "] does not exist!")
        found = False
        for nPos in range(0, len(cls.db_connectionConf)):
            if cls.db_connectionConf[nPos]["Database"].upper() == driverName.strip().upper():
                m_Config = cls.db_connectionConf[nPos]
                m_Config["FullName"] = [driverFile, ]
                found = True
                cls.db_connectionConf[nPos] = m_Config
        if not found:
            raise TestCliException("Driver not loaded. Please config it in configfile first.")
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Driver [" + driverName + "] loaded."
        }
        return


# 加载数命令行映射
def loadMap(cls, mapFile: str):
    cls.testOptions.set("TESTREWRITE", "ON")
    cls.cmdMappingHandler.loadCommandMappings(
        commandScriptFileName=cls.script,
        commandMappings=mapFile
    )
    cls.commandMap = mapFile
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": 'Mapping file loaded.'
    }
