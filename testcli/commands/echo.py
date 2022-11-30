# -*- coding: utf-8 -*-


# 将当前及随后的屏幕输入存放到脚本文件中
def echo_input(cls, fileName: str, block: str):
    try:
        f = open(fileName, "w", encoding=cls.testOptions.get("RESULT_ENCODING"))
        f.write(block)
        f.close()
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "File [" + str(fileName) + "] generated successful."
        }]
    except IOError as ie:
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "File [" + str(fileName) + "] generated failed. " + str(ie)
        }]
