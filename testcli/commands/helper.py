# -*- coding: utf-8 -*-
import copy

from ..helper import helpMessage


def showHelp(cls, topicName: str):
    if topicName == "":
        headers = ["COMMAND", "SUMMARY"]
        rows = []
        for helpTopic in helpMessage:
            row = (helpTopic["topic"].upper(), helpTopic["summary"])
            rows.append(row)
        yield {
            "type": "result",
            "title": None,
            "rows": rows,
            "headers": headers,
            "columnTypes": None,
            "status": "Use \"_HELP <command>\" to get detail help messages."
        }
    else:
        helpTopic = None
        for item in helpMessage:
            if item["topic"].upper() == topicName.upper():
                helpTopic = copy.copy(item)
                break
        if helpTopic is None:
            yield {
                "type": "error",
                "message": "Unrecognized command [" + topicName.upper() + "]. " +
                           "Use \"_HELP\" to list all commands."
            }
            return
        status = "  Command:"
        status = status + "\n    " + str(topicName).upper()
        status = status + "\n"
        status = status + "\n" + "  Summary:"
        status = status + "\n" + "    " + helpTopic["summary"]
        status = status + "\n"
        status = status + "\n" + "  Synatx:"
        synatx = helpTopic["synatx"]
        synatxLines = synatx.split('\n')
        if len(synatxLines[0].strip()) == 0:
            # 去掉第一个空行
            synatxLines = synatxLines[1:]
        lspaceLen = len(synatxLines[0]) - len(synatxLines[0].lstrip())
        for nPos in range(0, len(synatxLines)):
            synatxLines[nPos] = "    " + synatxLines[nPos][lspaceLen:]
        synatx = "\n".join(synatxLines)
        status = status + "\n" + synatx
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": status
        }
