# -*- coding: utf-8 -*-
import os
from ..testcliexception import TestCliException


# 将当前及随后的输出打印到指定的文件中
def spool(cls, fileName: str):
    if fileName.strip().upper() == 'OFF':
        # close spool file
        if len(cls.SpoolFileHandler) == 0:
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "not spooling currently"
            }
            return
        else:
            cls.SpoolFileHandler[-1].close()
            cls.SpoolFileHandler.pop()
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return

    if cls.logfilename is not None:
        # 如果当前主程序启用了日志，则spool日志的默认输出目录为logfile的目录
        spoolFileName = os.path.join(os.path.dirname(cls.logfilename), fileName.strip())
    else:
        # 如果主程序没有启用日志，则输出为当前目录
        spoolFileName = fileName.strip()

    # 如果当前有打开的Spool文件，关闭它
    try:
        cls.SpoolFileHandler.append(open(spoolFileName, "w", encoding=cls.testOptions.get("RESULT_ENCODING")))
    except IOError as e:
        raise TestCliException("SQLCLI-00000: IO Exception " + repr(e))
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": None
    }
    return
