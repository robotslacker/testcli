# -*- coding: utf-8 -*-
import time
import os
import traceback
import jpype
from ..sqlclijdbc import connect as jdbcconnect
from ..sqlclijdbc import SQLCliJDBCTimeOutException
from ..sqlclijdbc import SQLCliJDBCException
from ..testcliexception import TestCliException


# 连接数据库
def connectDb(cls, connectProperties, timeout: int = -1):
    # 如果当前的连接存在，且当前连接没有被保存，则断开当前的连接
    # 如果当前连接已经被保存，这里不做任何操作
    if cls.db_conn is not None:
        if cls.db_sessionName is None:
            # 如果之前数据库连接没有被保存，则强制断开连接
            cls.db_conn.close()
            cls.db_conn = None
            cls.cmdExecuteHandler.sqlConn = None
        else:
            if cls.db_saved_conn[cls.db_sessionName][0] is None:
                # 之前并没有保留数据库连接
                cls.db_conn.close()
                cls.db_conn = None
                cls.cmdExecuteHandler.sqlConn = None

    # 一旦开始数据库连接，则当前连接会被置空，以保证连接错误的影响能够对后续的语句产生作用
    cls.db_conn = None
    cls.cmdExecuteHandler.sqlConn = None

    if cls.db_connectionConf is None:
        yield {
            "type": "error",
            "message": "Please load driver first."
        }
        return

    # 如果连接内容仅仅就一个mem，则连接到memory db上
    if "localService" in connectProperties:
        if str(connectProperties["localService"]).upper() == "MEM":
            # 内置一个mem，用户调试需要
            connectProperties["service"] = "X"
            connectProperties["username"] = "sa"
            connectProperties["password"] = "sa"
            connectProperties["driver"] = "jdbc"
            connectProperties["driverSchema"] = "h2mem"
            connectProperties["driverType"] = "mem"
            connectProperties["host"] = "0.0.0.0"
            connectProperties["port"] = 0
            connectProperties["parameters"] = {}
        elif str(connectProperties["localService"]).upper() == "META":
            jobManagerURL = str(cls.testOptions.get("JOBMANAGER_METAURL")).strip()
            if len(jobManagerURL) == 0:
                raise TestCliException("TestCli-0000:  Meta is used for jobmanager, but you have not enable it.")
            hostAndport = str(jobManagerURL).replace("tcp://", "").split(':')
            host = hostAndport[0]
            port = hostAndport[1]
            # 如果连接内容仅仅就一个META，则连接到内置的jobmanager db
            connectProperties["service"] = "mem:testclimeta"
            connectProperties["username"] = "sa"
            connectProperties["password"] = "sa"
            connectProperties["driver"] = "jdbc"
            connectProperties["driverSchema"] = "h2tcp"
            connectProperties["driverType"] = "tcp"
            connectProperties["host"] = host
            connectProperties["port"] = port
            connectProperties["parameters"] = {}
        else:
            yield {
                "type": "error",
                "message": "Invalid localservice. MEM|META only."
            }
            return

    # 连接数据库
    try:
        # 如果当前未指定参数，缺省为上一次连接的参数
        if "driverSchema" not in connectProperties:
            connectProperties["driverSchema"] = cls.db_driverSchema
        if "username" not in connectProperties:
            connectProperties["username"] = cls.db_username
        if "password" not in connectProperties:
            connectProperties["password"] = cls.db_password
        if "driver" not in connectProperties:
            connectProperties["driver"] = cls.db_driver
        if "driverSchema" not in connectProperties:
            connectProperties["driverSchema"] = cls.db_driverSchema
        if "driverType" not in connectProperties:
            connectProperties["driverType"] = cls.db_driverType
        if "host" not in connectProperties:
            connectProperties["host"] = cls.db_host
        if "port" not in connectProperties:
            if cls.db_port is not None:
                connectProperties["port"] = int(cls.db_port)
            else:
                connectProperties["port"] = None
        if "service" not in connectProperties:
            connectProperties["service"] = cls.db_service
        if "parameters" not in connectProperties:
            connectProperties["parameters"] = cls.db_parameters

        if connectProperties["driver"] == 'jdbc':  # JDBC 连接数据库
            if connectProperties["driverSchema"] is None:
                # 必须指定数据库驱动类型
                yield {
                    "type": "error",
                    "message": "Unknown database [" + str(connectProperties["driverSchema"]) + "]. " +
                               "Connect Failed. Missed jdbc configuration in conf/testcli.ini."
                }
                return
            # 读取配置文件，判断随后JPype连接的时候使用具体哪一个Jar包
            jarList = []
            driverClass = ""
            jdbcURL = None
            jdbcProp = ""
            for jarConfig in cls.db_connectionConf:
                jarList.extend(jarConfig["FullName"])
            jarList = list(set(jarList))
            for jarConfig in cls.db_connectionConf:
                if jarConfig["Database"].upper() == str(connectProperties["driverSchema"]).upper():
                    driverClass = jarConfig["ClassName"]
                    jdbcURL = jarConfig["JDBCURL"]
                    jdbcProp = jarConfig["JDBCProp"]
                    break
            if jdbcURL is None:
                # 没有找到Jar包
                yield {
                    "type": "error",
                    "message": "Unknown database [" + str(connectProperties["driverSchema"]) + "]. " +
                               "Connect Failed. Missed jdbcurl configuration in conf/testcli.ini."
                }
                return

            # 如果没有指定数据库类型，则无法进行数据库连接
            if driverClass is None:
                yield {
                    "type": "error",
                    "message": "Missed driver config [" + connectProperties["driverSchema"] +
                               "]. Database Connect Failed. "
                }
                return

            # 替换连接字符串中的变量信息
            # 连接字符串中可以出现的变量有：  ${host} ${port} ${service} ${driverType}
            if connectProperties["host"] is not None:
                jdbcURL = jdbcURL.replace("${host}", connectProperties["host"])
            if connectProperties["port"] is not None:
                jdbcURL = jdbcURL.replace("${port}", str(connectProperties["port"]))
            if cls.db_port is None:
                jdbcURL = jdbcURL.replace(":${port}", "")
            else:
                jdbcURL = jdbcURL.replace("${port}", str(cls.db_port))
            if connectProperties["service"] is not None:
                jdbcURL = jdbcURL.replace("${service}", connectProperties["service"])
            else:
                jdbcURL = jdbcURL.replace("${service}", "")
            if connectProperties["driverType"] is not None:
                jdbcURL = jdbcURL.replace("${driverType}", connectProperties["driverType"])

            # 构造连接参数
            jdbcConnProp = {}
            if "username" in connectProperties:
                jdbcConnProp['user'] = connectProperties["username"]
            if "password" in connectProperties:
                jdbcConnProp['password'] = connectProperties["password"]
            # 处理连接参数中的属性信息，既包括配置文件中提供的参数，也包括连接命令行中输入的
            if jdbcProp is not None:
                for row in jdbcProp.strip().split(','):
                    props = row.split(':')
                    if len(props) == 2:
                        propName = str(props[0]).strip()
                        propValue = str(props[1]).strip()
                        jdbcConnProp[propName] = propValue
            if connectProperties["parameters"] is not None:
                for connectParameter in connectProperties["parameters"]:
                    jdbcConnProp[connectParameter["parameterName"]] = connectParameter["parameterValue"]
            # 尝试数据库连接，保持一定的重试次数，一直到连接上
            retryCount = 0
            while True:
                try:
                    cls.db_conn = jdbcconnect(
                        jclassname=driverClass,
                        url=jdbcURL,
                        driverArgs=jdbcConnProp,
                        jars=jarList,
                        timeoutLimit=timeout)
                    break
                except SQLCliJDBCTimeOutException as je:
                    raise je
                except SQLCliJDBCException as je:
                    if "TESTCLI_DEBUG" in os.environ:
                        print('traceback.print_exc():\n%s' % traceback.print_exc())
                        print('traceback.format_exc():\n%s' % traceback.format_exc())
                    retryCount = retryCount + 1
                    if retryCount >= int(cls.testOptions.get("SQLCONN_RETRYTIMES")):
                        raise je
                    else:
                        time.sleep(2)
                        continue

            # 将当前DB的连接字符串备份到变量中， 便于SET命令展示
            cls.testOptions.set("CONNURL", str(jdbcURL))
            cls.testOptions.set("CONNSCHEMA", str(connectProperties["username"]))

            # 成功连接后，保留当前连接的所有信息，以便下一次连接
            cls.db_url = jdbcURL
            cls.db_username = connectProperties["username"]
            cls.db_password = connectProperties["password"]
            cls.db_driver = connectProperties["driver"]
            cls.db_driverSchema = connectProperties["driverSchema"]
            cls.db_driverType = connectProperties["driverType"]
            cls.db_host = connectProperties["host"]
            cls.db_port = connectProperties["port"]
            cls.db_service = connectProperties["service"]
            cls.db_parameters = connectProperties["parameters"]

            # 保存连接句柄
            cls.cmdExecuteHandler.sqlConn = cls.db_conn
        else:
            yield {
                "type": "error",
                "message": "Invalid protocol [" + str(connectProperties["driver"]) +
                           "]. Currently, JDBC is the only supported option."
            }
            return
    except TestCliException as se:  # Connecting to a database fail.
        raise se
    except Exception as e:  # Connecting to a database fail.
        if "TESTCLI_DEBUG" in os.environ:
            print('traceback.print_exc():\n%s' % traceback.print_exc())
            print('traceback.format_exc():\n%s' % traceback.format_exc())
            print("[DEBUG] db_sessionName = [" + str(cls.db_sessionName) + "]")
            for jarfile in cls.db_connectionConf:
                print("[DEBUG] jar_file = " + str(jarfile) + "]")
        if str(e).find("SQLInvalidAuthorizationSpecException") != -1:
            yield {
                "type": "error",
                "message": str(jpype.java.sql.SQLInvalidAuthorizationSpecException(e).getCause())
            }
            return
        else:
            yield {
                "type": "error",
                "message": str(e)
            }
            return
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": 'Database connected.'
    }


# 断开数据库连接
def disconnectDb(cls):
    if cls.db_conn:
        cls.db_conn.close()
    cls.db_conn = None
    cls.cmdExecuteHandler.sqlConn = None
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": 'Database disconnected.'
    }
