# -*- coding: utf-8 -*-
import copy


# API会话管理
def apiSessionManage(cls, action: str, sessionName: str = None):
    if action.strip().lower() == 'show':
        result = []
        for _sessionName, sessionProperties in cls.api_saved_conn.items():
            if sessionName is None or str(sessionName) == "":
                if _sessionName == cls.httpSessionName:
                    displaySessionName = "*" + _sessionName
                else:
                    displaySessionName = " " + _sessionName
                result.append(
                    [
                        displaySessionName,
                        str(sessionProperties)
                    ]
                )
            else:
                if sessionName == _sessionName:
                    if _sessionName == cls.httpSessionName:
                        displaySessionName = "*" + _sessionName
                    else:
                        displaySessionName = " " + _sessionName
                    result.append(
                        [
                            displaySessionName,
                            str(sessionProperties)
                        ]
                    )
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
                "headers": ["SessionName", "Properties"],
                "columnTypes": None,
                "status": "Total " + str(len(result)) + " saved sesssions."
            }
        return

    if action.strip().lower() == 'save':
        cls.api_saved_conn[sessionName] = copy.copy(
            cls.api_saved_conn[cls.httpSessionName]
        )
        cls.httpSessionName = sessionName
    if action.strip().lower() == 'release':
        if cls.api_saved_conn[cls.httpSessionName] != "DEFAULT":
            del cls.api_saved_conn[cls.httpSessionName]
            cls.httpSessionName = "DEFAULT"
    if action.strip().lower() == 'restore':
        cls.httpSessionName = sessionName
