# -*- coding: utf-8 -*-
import time


# 退出当前应用程序
def exitApplication(cls, exitValue):
    if cls.commandScript is not None:
        # 运行在脚本模式下，会一直等待所有子进程退出后，再退出本程序
        while True:
            if not cls.JobHandler.isAllJobClosed():
                # 如果还有没有退出的进程，则不会直接退出程序，会继续等待进程退出
                time.sleep(3)
            else:
                break

        # 等待那些已经Running的进程完成， 但是只有Submitted的不考虑在内
        if cls.testOptions.get("JOBMANAGER") == "TRUE":
            cls.JobHandler.waitjob("all")

        # 断开数据库连接
        if cls.db_conn:
            cls.db_conn.close()
        cls.db_conn = None
        cls.cmdExecuteHandler.sqlConn = None

        # 断开之前保存的其他数据库连接
        for m_conn in cls.db_saved_conn.values():
            m_conn[0].close()

        # 退出应用程序
        cls.exitValue = exitValue
        raise EOFError
    else:
        if cls.testOptions.get("JOBMANAGER") == "ON":
            # 运行在控制台模式下
            if not cls.JobHandler.isAllJobClosed():
                yield {
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Please wait all background process complete."
                }
            else:
                # 退出应用程序
                cls.exitValue = exitValue
                raise EOFError
        else:
            # 退出应用程序
            cls.exitValue = exitValue
            raise EOFError
