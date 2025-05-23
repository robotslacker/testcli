# -*- coding: utf-8 -*-

"""
http://www.python.org/topics/database/DatabaseAPI-2.0.html
"""

import datetime
import glob
import os
import sys
import time
import warnings
import decimal

import jpype


class SQLCliJDBCException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


class SQLCliJDBCTimeOutException(SQLCliJDBCException):
    pass


class SQLCliJDBCLargeObject:
    def __init__(self):
        self._object = None
        self._ObjectLength = 0
        self._ColumnTypeName = None

    def setObject(self, p_Object):
        self._object = p_Object

    def getObjectLength(self):
        return self._ObjectLength

    def setObjectLength(self, p_ObjectLength: int):
        self._ObjectLength = p_ObjectLength

    def getData(self, p_nStartPos: int, p_nLength: int):
        if self._object is None:
            return None
        else:
            m_ObjectType = str(type(self._object))
            if m_ObjectType.upper().find("CLOB") != -1:
                return self._object.getSubString(p_nStartPos, int(p_nLength))
            elif m_ObjectType.upper().find("BLOB") != -1:
                byteResult = self._object.getBytes(p_nStartPos, int(p_nLength))
                if byteResult is not None:
                    return bytearray(self._object.getBytes(p_nStartPos, int(p_nLength)))
                else:
                    return None
            else:
                raise SQLCliJDBCException("SQLCLI-00000: Unknown LargeObjectType [" + m_ObjectType + "]")

    def getColumnTypeName(self):
        return self._ColumnTypeName

    def setColumnTypeName(self, p_ColumnTypeName: str):
        self._ColumnTypeName = p_ColumnTypeName


def reraise(tp, value, tb=None):
    if value is None:
        value = tp()
    else:
        value = tp(value)
    if tb:
        raise value.with_traceback(tb)
    raise value


string_type = str


# Mapping from java.sql.Types attribute name to attribute value
_jdbc_name_to_const = None


# Mapping from java.sql.Types attribute constant value to its attribute name
_jdbc_const_to_name = []


def _handle_sql_exception_jpype():
    import jpype
    SQLException = jpype.java.sql.SQLException
    exc_info = sys.exc_info()
    db_err = isinstance(exc_info[1], SQLException)

    if db_err:
        exc_type = DatabaseError
    else:
        exc_type = InterfaceError

    reraise(exc_type, exc_info[1], exc_info[2])


def limit(method, timeout):
    """ Convert a Java method to asynchronous call with a specified timeout. """
    """ 这里不使用func_timeout， 是因为funct_timeout的函数内部如果启动新的线程，会导致Python进程最后无法退出的问题"""
    def f(*args):
        @jpype.JImplements(jpype.java.util.concurrent.Callable)
        class ClsJLimit:
            @jpype.JOverride
            def call(self):
                return method(*args)
        future = jpype.java.util.concurrent.FutureTask(ClsJLimit())
        jpype.java.lang.Thread(future).start()
        try:
            timeunit = jpype.java.util.concurrent.TimeUnit.SECONDS
            return future.get(int(timeout), timeunit)
        except jpype.java.util.concurrent.TimeoutException:
            future.cancel(True)
            raise SQLCliJDBCTimeOutException("TimeOut")
    return f


def _get_classpath():
    """Extract CLASSPATH from system environment as JPype doesn't seem
    to respect that variable.
    """
    try:
        orig_cp = os.environ['CLASSPATH']
    except KeyError:
        return []
    expanded_cp = []
    for i in orig_cp.split(os.path.pathsep):
        expanded_cp.extend(_jar_glob(i))
    return expanded_cp


def _jar_glob(item):
    if item.endswith('*'):
        return glob.glob('%s.[jJ][aA][rR]' % item)
    else:
        return [item]


#  DB-API 模块所兼容的 DB-API 最高版本号
apilevel = '2.0'

'''
0:不支持线程安全, 多个线程不能共享此模块
1:初级线程安全支持: 线程可以共享模块, 但不能共享连接
2:中级线程安全支持线程可以共享模块和连接, 但不能共享游标
3:完全线程安全支持 线程可以共享模块, 连接及游标
'''
threadsafety = 1

# 该模块支持的 SQL 语句参数风格
paramstyle = 'qmark'


class DBAPITypeObject(object):
    _mappings = {}

    def __init__(self, *values):
        """Construct new DB-API 2.0 type object.
        values: Attribute names of java.sql.Types constants"""
        self.values = values
        for type_name in values:
            if type_name in DBAPITypeObject._mappings:
                raise ValueError("Non unique mapping for type '%s'" % type_name)
            DBAPITypeObject._mappings[type_name] = self

    def __cmp__(self, other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1
        else:
            return -1

    def __repr__(self):
        return 'DBAPITypeObject(%s)' % ", ".join([repr(i) for i in self.values])

    @classmethod
    def _map_jdbc_type_to_dbapi(cls, jdbc_type_const):
        try:
            type_name = _jdbc_const_to_name[jdbc_type_const]
        except KeyError:
            if "TESTCLI_DEBUG" in os.environ:
                warnings.warn("Unknown JDBC type with constant value %d. "
                              "Using None as a default type_code." % jdbc_type_const)
            return None
        try:
            return cls._mappings[type_name]
        except KeyError:
            if "TESTCLI_DEBUG" in os.environ:
                warnings.warn("No type mapping for JDBC type '%s' (constant value %d). "
                              "Using None as a default type_code." % (type_name, jdbc_type_const))
            return None


STRING = DBAPITypeObject('CHAR', 'NCHAR', 'NVARCHAR', 'VARCHAR', 'OTHER')
TEXT = DBAPITypeObject('CLOB', 'LONGVARCHAR', 'LONGNVARCHAR', 'NCLOB', 'SQLXML', 'STRUCT', 'ARRAY')
BINARY = DBAPITypeObject('BINARY', 'BLOB', 'LONGVARBINARY', 'VARBINARY')
NUMBER = DBAPITypeObject('BOOLEAN', 'BIGINT', 'BIT', 'INTEGER', 'SMALLINT', 'TINYINT')
FLOAT = DBAPITypeObject('FLOAT', 'REAL', 'DOUBLE')
DECIMAL = DBAPITypeObject('DECIMAL', 'NUMERIC')
DATE = DBAPITypeObject('DATE')
TIME = DBAPITypeObject('TIME')
DATETIME = DBAPITypeObject('TIMESTAMP', 'TIMESTAMP_WITH_TIMEZONE')
ROWID = DBAPITypeObject('ROWID')


# DB-API 2.0 Module Interface Exceptions
class Error(Exception):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class InternalError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class DataError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass


# DB-API 2.0 Type Objects and Constructors

def _str_func(func):
    def to_str(*parms):
        return str(func(*parms))

    return to_str


Date = _str_func(datetime.date)
Time = _str_func(datetime.time)
Timestamp = _str_func(datetime.datetime)


def AttachJVM(jars=None, libs=None):
    """Open a connection to a database using a JDBC driver and return
    a Connection instance.

    jclassname: Full qualified Java class name of the JDBC driver.
    url: Database url as required by the JDBC driver.
    driver_args: Dictionary or sequence of arguments to be passed to
           the Java DriverManager.getConnection method. Usually
           sequence of username and password for the db. Alternatively
           a dictionary of connection arguments (where `user` and
           `password` would probably be included). See
           http://docs.oracle.com/javase/7/docs/api/java/sql/DriverManager.html
           for more details
    jars: Jar filename or sequence of filenames for the JDBC driver
    libs: Dll/so filenames or sequence of dlls/sos used as shared
          library by the JDBC driver
    """
    if jars:
        if isinstance(jars, string_type):
            jars = [jars]
    else:
        jars = []
    if libs:
        if isinstance(libs, string_type):
            libs = [libs]
    else:
        libs = []

    import jpype
    if not getattr(jpype, "isJVMStarted")():
        args = []
        class_path = []
        if jars:
            class_path.extend(jars)
        class_path.extend(_get_classpath())
        if class_path:
            # class_path 进行去重
            class_path = list(set(class_path))
            class_path = os.path.pathsep.join(class_path)
            args.append('-Djava.class.path=%s' % class_path)
        if libs:
            # path to shared libraries
            libs_path = os.path.pathsep.join(libs)
            args.append('-Djava.library.path=%s' % libs_path)
        jvm_path = getattr(jpype, "getDefaultJVMPath")()
        getattr(jpype, "startJVM")(
            jvm_path,
            *args,
            ignoreUnrecognized=True,
            convertStrings=True
        )
        if "TESTCLI_DEBUG" in os.environ:
            print("JVM started: class.path=[" + jpype.java.lang.System.getProperty('java.class.path') + "]")
            print("JVM Version: [" + ".".join([str(x) for x in getattr(jpype, "getJVMVersion")()]) + "]")

    if jpype.java.lang.Thread.isAttached():
        jpype.java.lang.Thread.currentThread().setContextClassLoader(jpype.java.lang.ClassLoader.getSystemClassLoader())
    if _jdbc_name_to_const is None:
        types = jpype.java.sql.Types
        types_map = {}
        for i in types.class_.getFields():
            if jpype.java.lang.reflect.Modifier.isStatic(i.getModifiers()):
                const = i.get(None)
                types_map[i.getName()] = const
        _init_types(types_map)


def DetachJVM():
    try:
        if getattr(jpype, "isThreadAttachedToJVM")():
            jpype.java.lang.Thread.detach()
    except ImportError:
        # JPype可能已经被卸载，不再重复操作
        pass


# DB-API 2.0 Module Interface connect constructor
def connect(jclassname, url, driverArgs=None, jars=None, libs=None, timeoutLimit=-1):
    """Open a connection to a database using a JDBC driver and return
    a Connection instance.

    jclassname: Full qualified Java class name of the JDBC driver.
    url: Database url as required by the JDBC driver.
    driver_args: Dictionary or sequence of arguments to be passed to
           the Java DriverManager.getConnection method. Usually
           sequence of username and password for the db. Alternatively
           a dictionary of connection arguments (where `user` and
           `password` would probably be included). See
           http://docs.oracle.com/javase/7/docs/api/java/sql/DriverManager.html
           for more details
    jars: Jar filename or sequence of filenames for the JDBC driver
    libs: Dll/so filenames or sequence of dlls/sos used as shared
          library by the JDBC driver
    """
    # 连接到JVM上
    AttachJVM(jars=jars, libs=libs)

    if isinstance(driverArgs, string_type):
        driverArgs = [driverArgs]
    if not driverArgs:
        driverArgs = []

    # register driver for DriverManager
    try:
        jpype.JClass(jclassname)
    except TypeError:
        raise SQLCliJDBCException("SQLCLI-00000: Load java class failed. [" + str(jclassname) + "]")
    if isinstance(driverArgs, dict):
        Properties = jpype.java.util.Properties
        info = Properties()
        for k, v in driverArgs.items():
            if v is not None:
                info.setProperty(k, v)
        dargs = [info]
    else:
        dargs = driverArgs

    try:
        if timeoutLimit != -1:
            connecterJDBC = limit(jpype.java.sql.DriverManager.getConnection, timeoutLimit)
        else:
            connecterJDBC = jpype.java.sql.DriverManager.getConnection
        if "TESTCLI_DEBUG" in os.environ:
            print("[DEBUG] JDBC Connect URL =[" + str(url) + "]. ")
            print("[DEBUG] JDBC Connect Prop=[" + str(driverArgs) + "]. ")
        jconn = connecterJDBC(url, *dargs)
    except SQLCliJDBCTimeOutException:
        raise SQLCliJDBCException("SQLCLI-0000:: Timeout expired. Abort this command.")
    except jpype.java.sql.SQLException as je:
        raise SQLCliJDBCException(je.toString().replace("java.sql.SQLException: ", "").
                                  replace("java.sql.SQLTransientConnectionException: ", "").
                                  replace("java.sql.SQLInvalidAuthorizationSpecException: ", ""))

    return Connection(jconn, _converters)


def DateFromTicks(ticks):
    return Date(time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    return Time(time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(time.localtime(ticks)[:6])


# DB-API 2.0 Connection Object
class Connection(object):
    Error = Error
    Warning = Warning
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    InternalError = InternalError
    OperationalError = OperationalError
    ProgrammingError = ProgrammingError
    IntegrityError = IntegrityError
    DataError = DataError
    NotSupportedError = NotSupportedError

    def __init__(self, jconn, converters):
        self.jconn = jconn
        self._closed = False
        self._converters = converters

    def isClosed(self):
        return self._closed

    def close(self):
        if self.jconn is not None:
            self.jconn.close()
        self._closed = True

    def commit(self):
        try:
            self.jconn.commit()
        except Exception:
            _handle_sql_exception_jpype()

    def rollback(self):
        try:
            self.jconn.rollback()
        except Exception:
            _handle_sql_exception_jpype()

    def cursor(self):
        return Cursor(self, self._converters)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def setAutoCommit(self, p_bAutoCommit):
        self.jconn.setAutoCommit(p_bAutoCommit)


# DB-API 2.0 Cursor Object
class Cursor(object):
    rowcount = -1
    _meta = None
    _prep = None
    _stmt = None
    _rs = None
    _description = None
    warnings = None

    # 默认的fetchmany返回记录数，100
    arraysize = 100

    def __init__(self, connection, converters):
        self._connection = connection
        self._converters = converters

    # 取消当前正在执行的SQL语句
    def cancel(self):
        try:
            if self._prep is not None:
                self._prep.cancel()
            if self._stmt is not None:
                self._stmt.cancel()
        except Exception:
            # 并不处理任何cancel时候发生的错误
            pass

    @property
    def description(self):
        if self._description:
            return self._description
        m = self._meta
        if m:
            count = m.getColumnCount()
            self._description = []
            for col in range(1, count + 1):
                size = m.getColumnDisplaySize(col)
                jdbc_type = m.getColumnType(col)
                if jdbc_type == 0:
                    # PEP-0249: SQL NULL values are represented by the
                    # Python None singleton
                    column_type = None
                else:
                    if jdbc_type not in _jdbc_const_to_name:
                        # 如果列表中没法找到jdbc_type, 则将JDBC_TYPE_NAME直接返回
                        column_type = m.getColumnTypeName(col)
                    else:
                        column_type = str(_jdbc_const_to_name[jdbc_type])
                col_desc = (m.getColumnLabel(col),
                            column_type,
                            size,
                            size,
                            m.getPrecision(col),
                            m.getScale(col),
                            m.isNullable(col),
                            )
                self._description.append(col_desc)
            return self._description

    #   optional callproc(self, procname, *parameters) unsupported
    def close(self):
        self._close_last()
        self._connection = None

    def _close_last(self):
        """Close the resultset and reset collected metadata.
        """
        if self._rs:
            self._rs.close()
        self._rs = None
        if self._prep:
            self._prep.close()
        self._prep = None
        self._meta = None
        self._description = None

    def _set_stmt_parms(self, prep_stmt, parameters):
        if self:
            pass
        for i in range(len(parameters)):
            if type(parameters[i]) == list:
                m_JavaObject = None
                if len(parameters[i]) != 0:
                    m_JavaArray = jpype.JArray(jpype.JObject)
                    m_JavaObject = m_JavaArray(parameters[i])
                prep_stmt.setObject(i + 1, m_JavaObject)
            else:
                prep_stmt.setObject(i + 1, _pyobj_to_javaobj(parameters[i]))

    def execute_direct(self, operation, TimeOutLimit=-1):
        if self._connection.isClosed():
            raise Error()
        self._close_last()
        is_rs = False
        self._stmt = self._connection.jconn.createStatement()
        try:
            if TimeOutLimit != -1:
                execute = limit(self._stmt.execute, TimeOutLimit)
            else:
                execute = self._stmt.execute
            is_rs = execute(operation)
            m_SQLWarnMessage = None
            m_SQLWarnings = self._stmt.getWarnings()
            while m_SQLWarnings is not None:
                if m_SQLWarnMessage is None:
                    m_SQLWarnMessage = m_SQLWarnings.getMessage()
                else:
                    m_SQLWarnMessage = m_SQLWarnMessage + "\n" + m_SQLWarnings.getMessage()
                m_SQLWarnings = m_SQLWarnings.getNextWarning()
            self.warnings = m_SQLWarnMessage
        except SQLCliJDBCTimeOutException:
            raise SQLCliJDBCTimeOutException("SQLCLI-0000:: Timeout expired. Abort this command.")
        except Exception:
            _handle_sql_exception_jpype()
        self._rs = self._stmt.getResultSet()
        if self._rs is not None:
            self._meta = self._rs.getMetaData()
            self.rowcount = self._stmt.getUpdateCount()
        else:
            self._meta = None
            self.rowcount = -1
        if is_rs:
            self.rowcount = -1
        else:
            self.rowcount = self._stmt.getUpdateCount()

    def execute(self, operation, parameters=None, TimeOutLimit=-1):
        if self._connection.isClosed():
            raise Error()
        if not parameters:
            parameters = ()
        self._close_last()
        self._prep = self._connection.jconn.prepareStatement(operation)
        self._set_stmt_parms(self._prep, parameters)
        is_rs = False
        try:
            if TimeOutLimit != -1:
                execute = limit(self._prep.execute, TimeOutLimit)
            else:
                execute = self._prep.execute
            is_rs = execute()
            m_SQLWarnMessage = None
            m_SQLWarnings = self._prep.getWarnings()
            while m_SQLWarnings is not None:
                if m_SQLWarnMessage is None:
                    m_SQLWarnMessage = m_SQLWarnings.getMessage()
                else:
                    m_SQLWarnMessage = m_SQLWarnMessage + "\n" + m_SQLWarnings.getMessage()
                m_SQLWarnings = m_SQLWarnings.getNextWarning()
            self.warnings = m_SQLWarnMessage
        except SQLCliJDBCTimeOutException:
            raise SQLCliJDBCTimeOutException("SQLCLI-0000:: Timeout expired. Abort this command.")
        except Exception:
            _handle_sql_exception_jpype()
        # 忽略对execute的返回判断，总是恒定的去调用getResultSet
        self._rs = self._prep.getResultSet()
        if self._rs is not None:
            self._meta = self._rs.getMetaData()
        else:
            self._meta = None
        if is_rs:
            self.rowcount = -1
        else:
            self.rowcount = self._prep.getUpdateCount()

    def executemany(self, operation, seq_of_parameters):
        self._close_last()
        self._prep = self._connection.jconn.prepareStatement(operation)
        for parameters in seq_of_parameters:
            self._set_stmt_parms(self._prep, parameters)
            self._prep.addBatch()
        update_counts = self._prep.executeBatch()
        m_SQLWarnMessage = None
        m_SQLWarnings = self._prep.getWarnings()
        while m_SQLWarnings is not None:
            if m_SQLWarnMessage is None:
                m_SQLWarnMessage = m_SQLWarnings.getMessage()
            else:
                m_SQLWarnMessage = m_SQLWarnMessage + "\n" + m_SQLWarnings.getMessage()
            m_SQLWarnings = m_SQLWarnings.getNextWarning()
        self.warnings = m_SQLWarnMessage
        self.rowcount = sum(update_counts)
        self._close_last()

    def fetchone(self):
        if not self._rs:
            raise Error()
        if not self._rs.next():
            return None
        row = []
        for col in range(1, self._meta.getColumnCount() + 1):
            sqltype = self._meta.getColumnType(col)
            columnClassName = self._meta.getColumnClassName(col)
            columnTypeName = self._meta.getColumnTypeName(col)
            if columnTypeName != "LONG":
                # Oracle的LONG类型不支持getObject函数
                columnDataType = type(self._rs.getObject(col))
            else:
                columnDataType = str

            if columnClassName is None:
                # NULL值
                converter = _DEFAULT_CONVERTERS["VARCHAR"]
            elif columnClassName in 'org.postgresql.util.PGmoney':
                converter = _DEFAULT_CONVERTERS["VARCHAR"]
            elif columnClassName in ['oracle.sql.TIMESTAMPTZ']:
                converter = _DEFAULT_CONVERTERS["TIMESTAMP_WITH_TIMEZONE"]
            elif columnClassName in ['dm.jdbc.driver.DmdbTimestamp']:
                converter = _DEFAULT_CONVERTERS["TIMESTAMP_WITH_TIMEZONE"]
            elif columnClassName in ['oracle.sql.TIMESTAMPLTZ']:
                converter = _DEFAULT_CONVERTERS["TIMESTAMP_WITH_LOCAL_TIME_ZONE"]
            elif columnClassName.upper().find("BFILE") != -1:
                converter = _DEFAULT_CONVERTERS["BFILE"]
            elif columnTypeName in ['YEAR']:              # mysql数据类型
                converter = _DEFAULT_CONVERTERS["YEAR"]
            elif columnTypeName in ['timestamptz']:       # PG数据类型
                converter = _DEFAULT_CONVERTERS["TIMESTAMP_WITH_TIMEZONE"]
            elif columnClassName in ['java.sql.SQLXML']:       # SQLXML
                converter = _DEFAULT_CONVERTERS["VARCHAR"]
            elif str(columnDataType).find("'byte[]'") != -1 and \
                    columnTypeName.upper() in ['GEOMETRY', 'GEOGRAPHY']:
                converter = _DEFAULT_CONVERTERS["BINARY"]
            else:
                if sqltype in self._converters.keys():
                    converter = self._converters.get(sqltype)
                else:
                    converter = _unknownSqlTypeConverter
                    if "TESTCLI_DEBUG" in os.environ:
                        warnings.warn("Unknown JDBC convert with constant value " + str(sqltype) +
                                      ":" + self._meta.getColumnClassName(col))
            if "TESTCLI_DEBUG" in os.environ:
                print("[DEBUG] JDBC SQLType=[" + str(converter.__name__) + "] for col [" + str(col) + "]. " +
                      "sqltype=[" + str(sqltype) + ":" + str(columnClassName) + ":" + columnTypeName + "]")
            v = converter(self._connection.jconn, self._rs, col, columnClassName)
            row.append(v)
        return tuple(row)

    def fetchmany(self, size=None):
        if not self._rs:
            raise Error()
        if size is None:
            size = self.arraysize
        self._rs.setFetchSize(size)
        rows = []
        row = None
        for i in range(size):
            row = self.fetchone()
            if row is None:
                break
            else:
                rows.append(row)
        # reset fetch size
        if row:
            self._rs.setFetchSize(0)
        return rows

    def fetchall(self):
        rows = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            else:
                rows.append(row)
        return rows

    def setinputsizes(self, sizes):
        pass

    def setoutputsize(self, size, column=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _unknownSqlTypeConverter(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    return str(java_val)


def _to_time(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    try:
        java_val = rs.getTime(col)
        if not java_val:
            return
        lt = java_val.toLocalTime()
        t = datetime.time().replace(
            hour=lt.getHour(), minute=lt.getMinute(), second=lt.getSecond(), microsecond=lt.getNano())
        return t
    except Exception:
        # 处理一些超过Python数据类型限制的时间类型
        return rs.getString(col)


def _to_year(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    try:
        java_val = rs.getDate(col)
    except Exception:
        # 处理一些超过Python数据类型限制的时间类型
        return rs.getString(col)
    if not java_val:
        return
    java_cal = jpype.JClass("java.util.Calendar").getInstance()
    java_cal.setTime(java_val)
    return int(java_cal.get(1))


def _to_bit(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    try:
        java_val = rs.getObject(col)
    except Exception:
        # 不支持getObject操作, 直接返回字符类型
        str_val = rs.getString(col)
        if str_val is None:
            return
        else:
            return "0b" + rs.getString(col)
    if java_val is None:
        return
    typeName = str(java_val.getClass().getTypeName())
    if typeName == "byte[]":
        m_BitAsciiStr = "0b" + str(bin(int.from_bytes(java_val, sys.byteorder))).lstrip("0b").zfill(len(java_val)*8)
        return m_BitAsciiStr
    elif typeName.find("Boolean") != -1:
        str_val = rs.getString(col)
        if str_val is None:
            return
        else:
            if len(str_val) > 1:
                # 这不是一个标准的Boolean，按照字节内容返回
                return "0b" + str(str_val)
            else:
                if java_val == 0:
                    return "False"
                else:
                    return "True"
    elif typeName.find("BinaryData") != -1:
        m_Byte = java_val.getBytes()
        return "0b" + str(bin(int.from_bytes(m_Byte, sys.byteorder))).lstrip("0b").zfill(len(m_Byte)*8)
    else:
        raise SQLCliJDBCException("SQLCLI-00000: Unknown java class type [" + typeName + "] in _to_bit")


def _to_varbinary(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    typeName = str(java_val.getClass().getTypeName())
    if typeName == "byte[]":
        # 截断所有后面为0的字节数组内容
        m_TrimPos = -1
        for pos in range(len(java_val) - 1, 0, -1):
            if java_val[pos] != 0:
                m_TrimPos = pos
                break
        if m_TrimPos == -1:
            return bytearray(java_val)
        else:
            return bytearray(java_val[:m_TrimPos + 1])
    elif typeName.find("Boolean") != -1:
        str_val = rs.getString(col)
        if str_val is None:
            return
        else:
            if java_val == 0:
                return False
            else:
                return True
    else:
        raise SQLCliJDBCException("SQLCLI-00000: Unknown java class type [" + typeName + "] in _to_binary")


def _to_bfile(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    typeName = str(java_val.getClass().getTypeName())
    if typeName.find("BFILE") != -1:
        return "bfilename(" + java_val.getDirAlias() + ":" + java_val.getName() + ")"
    else:
        raise SQLCliJDBCException("SQLCLI-00000: Unknown java class type [" + typeName + "] in _to_bfile")


def _to_binary(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    typeName = str(java_val.getClass().getTypeName())
    if typeName == "byte[]":
        return bytearray(java_val)
    elif typeName.find("Boolean") != -1:
        str_val = rs.getString(col)
        if str_val is None:
            return
        else:
            if java_val == 0:
                return False
            else:
                return True
    else:
        raise SQLCliJDBCException("SQLCLI-00000: Unknown java class type [" + typeName + "] in _to_binary")


def _pyobj_to_javaobj(p_pyobj):
    if type(p_pyobj) == datetime.datetime:
        m_javaobj = jpype.JClass("java.sql.Timestamp")(round(time.mktime(p_pyobj.timetuple())))
        return m_javaobj
    return p_pyobj


def _javaobj_to_pyobj(p_javaobj, p_objColumnSQLType=None):
    if p_javaobj is None:
        return None
    if type(p_javaobj) == str:
        return p_javaobj
    typeName = str(p_javaobj.getClass().getTypeName())
    if typeName == "java.lang.Float":
        return float(p_javaobj.floatValue())
    elif typeName == "java.lang.Short":
        return int(p_javaobj.shortValue())
    elif typeName == "java.lang.Integer":
        return int(p_javaobj.intValue())
    elif typeName == "java.lang.Byte":
        return int(p_javaobj.byteValue())
    elif typeName == "java.lang.Boolean":
        return bool(p_javaobj.booleanValue())
    elif typeName == "java.lang.Long":
        return decimal.Decimal(p_javaobj.toString())
    elif typeName == "java.math.BigInteger":
        return decimal.Decimal(p_javaobj.toString())
    elif typeName == "java.lang.Double":
        return decimal.Decimal(p_javaobj.toString())
    elif typeName == "java.math.BigDecimal":
        return decimal.Decimal(p_javaobj.toPlainString())
    elif typeName == "java.sql.Timestamp":
        ld = p_javaobj.toLocalDateTime()
        d = datetime.datetime.strptime(str(ld.getYear()).zfill(4) + "-" + str(ld.getMonthValue()).zfill(2) + "-" +
                                       str(ld.getDayOfMonth()).zfill(2) + " " + str(ld.getHour()).zfill(2) + ":" +
                                       str(ld.getMinute()).zfill(2) + ":" + str(ld.getSecond()).zfill(2) + " " +
                                       str(ld.getNano() // 1000), "%Y-%m-%d %H:%M:%S %f")
        return d
    elif typeName == "java.time.LocalDateTime":
        d = datetime.datetime.strptime(str(p_javaobj.getYear()).zfill(4) + "-" +
                                       str(p_javaobj.getMonthValue()).zfill(2) + "-" +
                                       str(p_javaobj.getDayOfMonth()).zfill(2) + " " +
                                       str(p_javaobj.getHour()).zfill(2) + ":" +
                                       str(p_javaobj.getMinute()).zfill(2) + ":" +
                                       str(p_javaobj.getSecond()).zfill(2) + " " +
                                       str(p_javaobj.getNano() // 1000), "%Y-%m-%d %H:%M:%S %f")
        return d
    elif typeName == 'dm.jdbc.driver.DmdbTimestamp':
        d = datetime.datetime.strptime(str(p_javaobj.getYear()).zfill(4) + "-" +
                                       str(p_javaobj.getMonth()).zfill(2) + "-" +
                                       str(p_javaobj.getDay()).zfill(2) + " " +
                                       str(p_javaobj.getHours()).zfill(2) + ":" +
                                       str(p_javaobj.getMinutes()).zfill(2) + ":" +
                                       str(p_javaobj.getSeconds()).zfill(2) + " " +
                                       str(p_javaobj.getNanos() // 1000), "%Y-%m-%d %H:%M:%S %f")
        return d
    elif typeName == "oracle.sql.TIMESTAMP":
        ld = p_javaobj.toJdbc().toLocalDateTime()
        d = datetime.datetime.strptime(str(ld.getYear()).zfill(4) + "-" + str(ld.getMonthValue()).zfill(2) + "-" +
                                       str(ld.getDayOfMonth()).zfill(2) + " " + str(ld.getHour()).zfill(2) + ":" +
                                       str(ld.getMinute()).zfill(2) + ":" + str(ld.getSecond()).zfill(2) + " " +
                                       str(ld.getNano() // 1000), "%Y-%m-%d %H:%M:%S %f")
        return d
    elif typeName in ['java.sql.Date', 'java.time.LocalDateTime']:
        d = datetime.date(year=p_javaobj.toLocalDate().getYear(),
                          month=p_javaobj.toLocalDate().getMonthValue(),
                          day=p_javaobj.toLocalDate().getDayOfMonth())
        return d
    elif typeName.upper().find('SQLDATE') != -1:
        d = datetime.date(year=p_javaobj.toLocalDate().getYear(),
                          month=p_javaobj.toLocalDate().getMonthValue(),
                          day=p_javaobj.toLocalDate().getDayOfMonth())
        return d
    elif typeName.upper().find('STRUCT') != -1:
        m_retVal = []
        for java_item in p_javaobj.getAttributes():
            m_retVal.append(_javaobj_to_pyobj(java_item))
        return m_retVal
    elif typeName.find('Object[]') != -1:
        m_retVal = []
        for java_item in p_javaobj:
            m_retVal.append(_javaobj_to_pyobj(java_item))
        return m_retVal
    elif typeName.upper().find('ARRAY') != -1:
        m_BaseTypeName = p_javaobj.getBaseTypeName()
        java_val = p_javaobj.getArray()
        d = []
        for java_item in java_val:
            d.append(_javaobj_to_pyobj(java_item, m_BaseTypeName))
        return d
    elif typeName == "byte[]":
        if p_objColumnSQLType in ["VARBINARY", "LONGVARBINARY"]:
            # 截断所有后面为0的字节数组内容
            m_TrimPos = -1
            for pos in range(len(p_javaobj) - 1, 0, -1):
                if p_javaobj[pos] != 0:
                    m_TrimPos = pos
                    break
            if m_TrimPos == -1:
                return bytearray(p_javaobj)
            else:
                return bytearray(p_javaobj[:m_TrimPos + 1])
        else:
            return bytearray(p_javaobj)
    elif typeName.upper().find('CLOB') != -1:
        m_Length = p_javaobj.length()
        largeObject = SQLCliJDBCLargeObject()
        largeObject.setColumnTypeName(p_objColumnSQLType)
        largeObject.setObjectLength(m_Length)
        largeObject.setObject(p_javaobj)
        return largeObject
    elif typeName.upper().find('BLOB') != -1:
        m_Length = p_javaobj.length()
        largeObject = SQLCliJDBCLargeObject()
        largeObject.setColumnTypeName(p_objColumnSQLType)
        largeObject.setObjectLength(m_Length)
        largeObject.setObject(p_javaobj)
        return largeObject
    elif typeName.upper() in ['ORACLE.SQL.ROWID']:
        return p_javaobj.toString()
    elif typeName.upper() in ['ORACLE.XDB.XMLTYPE']:
        return p_javaobj.getString()
    elif typeName.upper().find('DMDBROWID') != -1:
        return p_javaobj.toString()
    else:
        raise SQLCliJDBCException("SQLCLI-00000: Unknown java class type [" + typeName + "] in _javaobj_to_pyobj")


def _java_to_py(conn, rs, col, p_objColumnSQLType=None):
    if conn:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    return _javaobj_to_pyobj(java_val, p_objColumnSQLType)


def _java_to_py_timestampwithtimezone(conn, rs, col, p_objColumnSQLType=None):
    if p_objColumnSQLType:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    typeName = str(java_val.getClass().getTypeName())
    if typeName == "java.time.OffsetDateTime":
        ld = java_val.toLocalDateTime()
        d = datetime.datetime.strptime(str(ld.getYear()).zfill(4) + "-" + str(ld.getMonthValue()).zfill(2) + "-" +
                                       str(ld.getDayOfMonth()).zfill(2) + " " + str(ld.getHour()).zfill(2) + ":" +
                                       str(ld.getMinute()).zfill(2) + ":" + str(ld.getSecond()).zfill(2) + " " +
                                       str(ld.getNano() // 1000) + " " + java_val.getOffset().getId(),
                                       "%Y-%m-%d %H:%M:%S %f %z")
        return d
    elif typeName in ["java.sql.Timestamp"]:
        ld = java_val.toLocalDateTime()
        d = datetime.datetime.strptime(str(ld.getYear()).zfill(4) + "-" + str(ld.getMonthValue()).zfill(2) + "-" +
                                       str(ld.getDayOfMonth()).zfill(2) + " " + str(ld.getHour()).zfill(2) + ":" +
                                       str(ld.getMinute()).zfill(2) + ":" + str(ld.getSecond()).zfill(2) + " " +
                                       str(ld.getNano() // 1000),
                                       "%Y-%m-%d %H:%M:%S %f")
        return d
    elif typeName in ["dm.jdbc.driver.DmdbTimestamp"]:
        ld = java_val.toLocalDateTime()
        timeZoneOffset = java_val.getTimezone()
        if timeZoneOffset >= 0:
            offsetId = "+"
        else:
            offsetId = "-"
        offsetId = offsetId + str(int(timeZoneOffset / 60)).zfill(2) + ":" + str(int(timeZoneOffset % 60)).zfill(2)
        d = datetime.datetime.strptime(str(ld.getYear()).zfill(4) + "-" + str(ld.getMonthValue()).zfill(2) + "-" +
                                       str(ld.getDayOfMonth()).zfill(2) + " " + str(ld.getHour()).zfill(2) + ":" +
                                       str(ld.getMinute()).zfill(2) + ":" + str(ld.getSecond()).zfill(2) + " " +
                                       str(ld.getNano() // 1000) + " " + offsetId,
                                       "%Y-%m-%d %H:%M:%S %f %z")
        return d
    elif typeName in ['oracle.sql.TIMESTAMPTZ', 'oracle.sql.TIMESTAMPLTZ']:
        java_val = java_val.offsetDateTimeValue(conn)
        ld = java_val.toLocalDateTime()
        try:
            d = datetime.datetime.strptime(str(ld.getYear()).zfill(4) + "-" + str(ld.getMonthValue()).zfill(2) + "-" +
                                           str(ld.getDayOfMonth()).zfill(2) + " " + str(ld.getHour()).zfill(2) + ":" +
                                           str(ld.getMinute()).zfill(2) + ":" + str(ld.getSecond()).zfill(2) + " " +
                                           str(ld.getNano() // 1000) + " " + java_val.getOffset().getId(),
                                           "%Y-%m-%d %H:%M:%S %f %z")
        except ValueError:
            d = str(java_val.format(
                jpype.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS Z")))
        return d
    elif typeName in ['org.h2.api.TimestampWithTimeZone', ]:
        java_val = rs.getObject(col, jpype.JClass("java.time.OffsetDateTime"))
        ld = java_val.toLocalDateTime()
        d = datetime.datetime.strptime(str(ld.getYear()).zfill(4) + "-" + str(ld.getMonthValue()).zfill(2) + "-" +
                                       str(ld.getDayOfMonth()).zfill(2) + " " + str(ld.getHour()).zfill(2) + ":" +
                                       str(ld.getMinute()).zfill(2) + ":" + str(ld.getSecond()).zfill(2) + " " +
                                       str(ld.getNano() // 1000) + " " + java_val.getOffset().getId(),
                                       "%Y-%m-%d %H:%M:%S %f %z")
        return d
    else:
        raise SQLCliJDBCException(
            "SQLCLI-00000: Unknown java class type [" + typeName +
            "] in _java_to_py_timestampwithtimezone")


def _java_to_py_stru(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    typeName = str(java_val.getClass().getTypeName())
    if typeName == "java.lang.Object[]":
        m_retVal = []
        for java_item in java_val:
            m_retVal.append(_javaobj_to_pyobj(java_item))
        return tuple(m_retVal)
    elif typeName in ["oracle.sql.STRUCT", "java.sql.Struct"]:
        m_retVal = []
        for java_item in java_val.getAttributes():
            m_retVal.append(_javaobj_to_pyobj(java_item))
        return tuple(m_retVal)
    else:
        raise SQLCliJDBCException(
            "SQLCLI-00000: Unknown java class type [" + typeName +
            "] in _java_to_py_stru")


def _java_to_py_array(conn, rs, col, p_objColumnSQLType=None):
    if conn or p_objColumnSQLType:
        pass
    java_val = rs.getObject(col)
    if java_val is None:
        return
    typeName = str(java_val.getClass().getTypeName())
    if typeName.upper().find('ARRAY') != -1:
        m_BaseTypeName = java_val.getBaseTypeName()
        java_val = java_val.getArray()
        m_retVal = []
        for java_item in java_val:
            m_retVal.append(_javaobj_to_pyobj(java_item, m_BaseTypeName))
        return m_retVal
    elif typeName.find('Object[]') != -1:
        m_retVal = []
        for java_item in java_val:
            m_retVal.append(_javaobj_to_pyobj(java_item))
        return m_retVal
    else:
        raise SQLCliJDBCException(
            "SQLCLI-00000: Unknown java class type [" + typeName +
            "] in _java_to_py_array")


def _init_types(types_map):
    global _jdbc_name_to_const
    _jdbc_name_to_const = types_map
    global _jdbc_const_to_name
    _jdbc_const_to_name = dict((y, x) for x, y in types_map.items())
    _init_converters(types_map)


def _init_converters(types_map):
    # 存在不属于标准JDBC的convert情况，所以如果types_map找不到，这里不报错
    global _converters
    _converters = {}
    for i in _DEFAULT_CONVERTERS:
        if i in types_map:
            const_val = types_map[i]
            _converters[const_val] = _DEFAULT_CONVERTERS[i]


# Mapping from java.sql.Types field to converter method
_converters = None

_DEFAULT_CONVERTERS = {
    # see
    # http://download.oracle.com/javase/8/docs/api/java/sql/Types.html
    # for possible keys
    'CHAR':                             _java_to_py,
    'LONGVARCHAR':                      _java_to_py,
    'VARCHAR':                          _java_to_py,
    'TIMESTAMP':                        _java_to_py,
    'DATE':                             _java_to_py,
    'DECIMAL':                          _java_to_py,
    'NUMERIC':                          _java_to_py,
    'DOUBLE':                           _java_to_py,
    'REAL':                             _java_to_py,
    'BIGINT':                           _java_to_py,
    'FLOAT':                            _java_to_py,
    'TINYINT':                          _java_to_py,
    'INTEGER':                          _java_to_py,
    'SMALLINT':                         _java_to_py,
    'BOOLEAN':                          _java_to_py,
    'NCLOB':                            _java_to_py,
    'CLOB':                             _java_to_py,
    'BLOB':                             _java_to_py,
    'BIT':                              _to_bit,
    'STRUCT':                           _java_to_py_stru,
    'ARRAY':                            _java_to_py_array,
    'VARBINARY':                        _to_varbinary,
    'LONGVARBINARY':                    _to_varbinary,
    'TIME WITH TIME ZONE':              _java_to_py_timestampwithtimezone,
    'TIMESTAMP_WITH_TIMEZONE':          _java_to_py_timestampwithtimezone,
    'TIMESTAMP_WITH_LOCAL_TIME_ZONE':   _java_to_py_timestampwithtimezone,
    'TIME':                             _to_time,
    'YEAR':                             _to_year,
    'BINARY':                           _to_binary,
    'BFILE':                            _to_bfile,
    'ROWID':                            _java_to_py,
}
