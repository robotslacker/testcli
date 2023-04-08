# -*- coding: utf-8 -*-
import importlib.util
import os
import re
from ..testcliexception import TestCliException
from ..commands.embeddScript import globalEmbeddScriptScope

# 包含在脚本中的模块列表
# { modeleName: modulePtr }
scriptModule = {}

# 包含在脚本中的功能函数列表
# { functionName: functionPtr }
scriptFunction = {}

# 插件列表
"""
    {
        "NAME": <pluginName>, 
        "NAMESPACE": <nameSpace>:list, 
        "CMDENTRY": ptr<functionPrt>, 
        "SETUP": ptr<functionPrt>,
        "TEARDOWN": ptr<functionPrt>,
    }
"""
plugins = {}


# 加载额外的Python脚本
# 用来扩展当前的内嵌语法
def loadScript(cls, scriptFile: str):
    global scriptFunction
    global scriptModule

    # 首先在当前目录下查找
    # 如果找不到，则去程序所在的目录下去寻找
    if not os.path.exists(scriptFile):
        if not os.path.exists(os.path.join(os.path.abspath(__file__), scriptFile)):
            yield {
                "type": "error",
                "message": "Script file [" + os.path.abspath(scriptFile) + "] does not exist!",
            }
            return
    scriptFileHandler = open(file=scriptFile, mode="r", encoding=cls.testOptions.get("SCRIPT_ENCODING"))
    scriptContents = scriptFileHandler.readlines()

    # 导入script的外部模块
    for scriptContext in scriptContents:
        matchObj = re.match(r"^class(\s+)(.*?)(\s+)?[(|:]", scriptContext)
        if matchObj:
            className = str(matchObj.group(2)).strip()
            # 动态导入class
            spec_class = importlib.util.spec_from_file_location(
                name=className,
                location=os.path.abspath(scriptFile)
            )
            module_class = importlib.util.module_from_spec(spec_class)
            spec_class.loader.exec_module(module_class)
            scriptClass = getattr(module_class, className)
            scriptModule[className] = scriptClass
            globalEmbeddScriptScope[className] = scriptModule[className]
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": 'Module [' + str(className) + '] loaded successful.'
            }

    # 导入script的函数
    for scriptContext in scriptContents:
        matchObj = re.match(r"^def(\s+)(.*?)(\s+)?[(|:]", scriptContext)
        if matchObj:
            funcName = str(matchObj.group(2)).strip()
            # 动态导入Function
            spec_function = importlib.util.spec_from_file_location(
                name=funcName,
                location=os.path.abspath(scriptFile)
            )
            module_function = importlib.util.module_from_spec(spec_function)
            spec_function.loader.exec_module(module_function)
            scriptFunc = getattr(module_function, funcName)
            scriptFunction[funcName] = scriptFunc
            globalEmbeddScriptScope[funcName] = scriptFunction[funcName]
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": 'Function [' + str(funcName) + '] loaded successful.'
            }
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": 'Script file loaded successful.'
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


# 加载额外的插件，用于扩展新的命令
def loadPlugin(cls, pluginFile: str):
    # 首先在当前目录下查找
    # 如果找不到，则去程序所在的目录下去寻找
    bFoundPluginFile = False
    if os.path.exists(pluginFile):
        # 首先假定是绝对文件名
        bFoundPluginFile = True
        pluginFile = os.path.abspath(pluginFile)
    if not bFoundPluginFile:
        # 其次去程序文件所在的目录去相对查找
        if os.path.exists(os.path.join(os.path.abspath(__file__), pluginFile)):
            bFoundPluginFile = True
            pluginFile = os.path.abspath(os.path.join(os.path.abspath(__file__), pluginFile))
    if not bFoundPluginFile:
        # 还是没有找到，就去plugin目录下相对查找
        if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "plugin", pluginFile)):
            bFoundPluginFile = True
            pluginFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugin", pluginFile))

    if not bFoundPluginFile:
        # 最后还是找不到
        yield {
            "type": "error",
            "message": "Plugin file [" + os.path.abspath(pluginFile) + "] does not exist!",
        }
        return
    pluginFileHandler = open(file=pluginFile, mode="r", encoding=cls.testOptions.get("SCRIPT_ENCODING"))
    pluginContents = pluginFileHandler.readlines()

    # 首先找到插件的名称，这是必须定义的内容，即变量COMMAND代表的东西
    # pluginName在存放的时候将会被大写
    pluginName = None
    for pluginContext in pluginContents:
        matchObj = re.match(r"^COMMAND(\s+)?=(.*)", pluginContext)
        if matchObj:
            commandName = str(matchObj.group(2)).strip()
            pluginName = str(eval(commandName))
            break
    if pluginName is None:
        yield {
            "type": "error",
            "message": "Load plugin file [" + os.path.abspath(pluginFile) + "] error! Variable \"COMMAND\" missed.",
        }
        return
    # 不能和已有的其他命令重合
    if pluginName.upper() in ['EXIT', 'QUIT', 'SLEEP', 'USE', 'ECHO', 'ASSERT', 'START', 'LOAD', 'HOST',
                              'HELP', 'IF', 'ENDIF', 'SET', 'SPOOL', 'LOOP', 'WHENEVER', 'SSH', 'JOB',
                              'COMPARE', 'DATA', 'MONITOR']:
        yield {
            "type": "error",
            "message": "Load plugin file [" + os.path.abspath(pluginFile) + "] error! Conflicting with keywords!",
        }
        return

    # 加载外挂文件中的函数, cmdEntry作为函数的入口
    plugin = {}
    for funcName in ["cmdEntry"]:
        spec_function = importlib.util.spec_from_file_location(name=funcName, location=os.path.abspath(pluginFile))
        module_function = importlib.util.module_from_spec(spec_function)
        try:
            spec_function.loader.exec_module(module_function)
            funcEntry = getattr(module_function, funcName)
            plugin.update({funcName: funcEntry})
        except AttributeError:
            yield {
                "type": "error",
                "message": "Load plugin file [" + os.path.abspath(
                    pluginFile) + "] error! Please define \"cmdEntry\" in plugin file.",
            }
            return
        except SyntaxError as se:
            yield {
                "type": "error",
                "message": "Load plugin file [" + os.path.abspath(
                    pluginFile) + "] error! " + repr(se),
            }
            return
    cls.plugin[pluginName.upper()] = plugin

    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": 'Plugin [' + pluginName + '] loaded successful.'
    }


def executeLoadRequest(cls, requestObject):
    if requestObject["option"] == "SCRIPT":
        for commandResult in loadScript(
                cls=cls,
                scriptFile=requestObject["scriptFile"]
        ):
            yield commandResult
    elif requestObject["option"] == "PLUGIN":
        for commandResult in loadPlugin(
                cls=cls,
                pluginFile=requestObject["pluginFile"]
        ):
            yield commandResult
    elif requestObject["option"] == "JDBCDRIVER":
        driverName = None
        driverClass = None
        driverFile = None
        driverURL = None
        driverProps = None
        if "driverName" in requestObject:
            driverName = requestObject["driverName"]
        if "driverClass" in requestObject:
            driverClass = requestObject["driverClass"]
        if "driverFile" in requestObject:
            driverFile = requestObject["driverFile"]
        if "driverURL" in requestObject:
            driverURL = requestObject["driverURL"]
        if "driverProps" in requestObject:
            driverProps = requestObject["driverProps"]
        for commandResult in loadJDBCDriver(
                cls=cls,
                driverName=driverName,
                driverClass=driverClass,
                driverFile=driverFile,
                driverURL=driverURL,
                driverProps=driverProps
        ):
            yield commandResult
    elif requestObject["option"] == "MAP":
        for commandResult in loadMap(
                cls=cls,
                mapFile=requestObject["mapFile"]
        ):
            yield commandResult
