# -*- coding: utf-8 -*-
from ..testcliexception import TestCliException


# 数据库会话管理
def sqlSessionManage(cls, action: str, sessionName: str = None):
    # Session_Context:
    #   0:   Connection
    #   1:   UserName
    #   2:   Password
    #   3:   URL
    if action.strip().lower() == 'show':
        result = []
        for m_Session_Name, m_Connection in cls.db_saved_conn.items():
            if m_Connection[0] is None:
                result.append(['None', str(m_Session_Name), str(m_Connection[1]), '******', str(m_Connection[3])])
            else:
                result.append(['Connection', str(m_Session_Name), str(m_Connection[1]), '******', str(m_Connection[3])])
        if cls.db_conn is not None:
            result.append(['Current', str(cls.db_sessionName), str(cls.db_username), '******', str(cls.db_url)])
        if len(result) == 0:
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "No saved sesssions."
            }
        else:
            yield {
                "type": "result",
                "title": "Saved sessions:",
                "rows": result,
                "headers": ["Session", "Sesssion Name", "User Name", "Password", "URL"],
                "columnTypes": None,
                "status": "Total " + str(len(result)) + " saved sesssions."
            }
        return

    if action.strip().lower() == 'release':
        if cls.db_conn is None:
            raise TestCliException(
                "You don't have a saved session.")
        del cls.db_saved_conn[sessionName]
        cls.db_sessionName = None
    elif action.strip().lower() == 'save':
        if cls.db_conn is None:
            raise TestCliException(
                "Please connect session first before save.")
        cls.db_saved_conn[sessionName] = [cls.db_conn, cls.db_username, cls.db_password, cls.db_url]
        cls.db_sessionName = sessionName
    elif action.strip().lower() == 'saveurl':
        if cls.db_conn is None:
            raise TestCliException(
                "Please connect session first before save.")
        cls.db_saved_conn[sessionName] = [None, cls.db_username, cls.db_password, cls.db_url]
        cls.db_sessionName = sessionName
    elif action.strip().lower() == 'restore':
        if sessionName in cls.db_saved_conn:
            cls.db_username = cls.db_saved_conn[sessionName][1]
            cls.db_password = cls.db_saved_conn[sessionName][2]
            cls.db_url = cls.db_saved_conn[sessionName][3]
            if cls.db_saved_conn[sessionName][0] is None:
                result = cls.connect_db(cls.db_username + "/" + cls.db_password + "@" + cls.db_url)
                for title, cur, headers, columnTypes, status in result:
                    yield {
                        "title": title,
                        "rows": cur,
                        "headers": headers,
                        "columnTypes": columnTypes,
                        "status": status
                    }
            else:
                cls.db_conn = cls.db_saved_conn[sessionName][0]
                cls.cmdExecuteHandler.sqlConn = cls.db_conn
                cls.db_sessionName = sessionName
        else:
            raise TestCliException(
                "Session [" + sessionName + "] does not exist. Please save it first.")
    else:
        raise TestCliException(
            "Wrong argument : " + "Session save|restore <sessionName>.")
    if action.strip().lower() == 'save':
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Session saved successful."
        }
    if action.strip().lower() == 'release':
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Session release successful."
        }
    if action.strip().lower() == 'restore':
        cls.testOptions.set("CONNURL", cls.db_url)
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Session restored successful."
        }
