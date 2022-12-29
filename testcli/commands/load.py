# -*- coding: utf-8 -*-
import importlib.util
import os
import re
from ..testcliexception import TestCliException
from ..commands.embeddScript import localEmbeddScriptScope

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
def loadJDBCDriver(cls,
                   driverName: str, driverClass: str,
                   driverFile: str, driverURL: str,
                   driverProps: str):
    if driverName is None:  # 显示当前的Driver配置
        m_Result = []
        for row in cls.db_connectionConf:
            m_Result.append([row["Database"], row["ClassName"], row["FullName"],
                             row["JDBCURL"], row["JDBCProp"]])
        yield {
            "type": "result",
            "title": "Current Drivers: ",
            "rows": m_Result,
            "headers": ["Database", "ClassName", "FileName", "JDBCURL", "JDBCProp"],
            "columnTypes": None,
            "status": "Driver loaded."
        }
        return

    # 如果给定的一个全路径，则使用全路径文件, 否则按照相对路径查找
    driverFileFullPathList = []
    if driverFile is not None:
        driverFileList = driverFile.split(',')
        for driverFile in driverFileList:
            driverFile = driverFile.strip().strip('"').strip("'")
            if not os.path.exists(driverFile):
                raise TestCliException("Driver not loaded. "
                                       "file [" + str(os.path.abspath(driverFile)) + "] does not exist!")
            else:
                driverFileFullPathList.append(os.path.abspath(driverFile))

    # 查看指定的驱动是否存在，如果存在，则替换，不存在，则新增
    found = False
    for nPos in range(0, len(cls.db_connectionConf)):
        if cls.db_connectionConf[nPos]["Database"].upper() == driverName.strip().upper():
            m_Config = cls.db_connectionConf[nPos]
            if len(driverFileFullPathList) != 0:
                m_Config["FullName"] = driverFileFullPathList
            if driverClass is not None:
                m_Config["ClassName"] = driverClass
            if driverURL is not None:
                m_Config["JDBCURL"] = driverURL
            if driverProps is not None:
                m_Config["JDBCProp"] = driverProps
            found = True
            cls.db_connectionConf[nPos] = m_Config
    if not found:
        cls.db_connectionConf.append(
            {
                "ClassName": driverClass,
                "FullName": driverFileFullPathList,
                "JDBCURL": driverURL,
                "JDBCProp": driverProps,
                "Database": driverName
            }
        )
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": "Driver [" + driverName + "] loaded."
    }


# 加载命令行映射信息
def loadMap(cls, mapFile: str):
    try:
        cls.cmdMappingHandler.loadCommandMappings(
            commandScriptFileName=cls.executeScript,
            commandMappings=mapFile
        )
        cls.testOptions.set("TESTREWRITE", "ON")
        cls.commandMap = mapFile
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": 'Mapping file loaded.'
        }
    except TestCliException as te:
        yield {
            "type": "error",
            "message": te.message
        }
