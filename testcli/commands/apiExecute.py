# -*- coding: utf-8 -*-
import urllib3
import copy
import re
import json
import os
import ssl
from json import JSONDecodeError


def executeAPISet(cls, apiSetRequest):
    if apiSetRequest["option"] == "PROXY":
        cls.api_saved_conn[cls.httpSessionName]["http_proxy"] = apiSetRequest["value"]
    if apiSetRequest["option"] == "HTTPS_VERIFY":
        cls.api_saved_conn[cls.httpSessionName]["https_verify"] = apiSetRequest["value"]
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": [],
        "columnTypes": None,
        "status": "Change(" + cls.httpSessionName + ") HTTP request setting: " +
                  "[" + apiSetRequest["option"] + "]=[" + apiSetRequest["value"] + "] successful."
    }
    return


def executeAPIStatement(cls, apiRequest, apiHints):
    """
    执行指定的API请求

    输入：
        apiRequest             JSON对象，请求的内容
        apiHints               提示信息

    返回内容：
        错误情况下：
        {
            "type": "error",
            "message": apiErrorMessage
        }
        正确情况下：
        {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": content
        }
    """

    # 查看是否需要进行HTTPS的签名验证
    https_verify = cls.cliHandler.api_saved_conn[cls.cliHandler.httpSessionName]["https_verify"]
    if https_verify is None:
        # 如果保存的会话中没有设置HTTPVERIFY，则按照默认值来获得
        https_verify = cls.testOptions.get("API_HTTPSVERIFY")
    else:
        # 如果保存的会话中设置了HTTPVERIFY，则按照会话中设置的来
        https_verify = str(https_verify).strip().upper()

    # 查看是否设置了代理
    http_proxy = cls.cliHandler.api_saved_conn[cls.cliHandler.httpSessionName]["http_proxy"]
    if http_proxy is None:
        # 如果保存的会话中没有设置代理，则按照默认值来获得
        http_proxy = cls.testOptions.get("API_HTTPPROXY")
    else:
        # 如果保存的会话中设置了代理，则按照会话中设置的来
        http_proxy = str(http_proxy).strip()

    if https_verify == "OFF":
        if http_proxy != "":
            httpHandler = urllib3.ProxyManager(proxy_url=http_proxy, cert_reqs=ssl.CERT_NONE)
        else:
            httpHandler = urllib3.PoolManager(cert_reqs=ssl.CERT_NONE)
    else:
        if http_proxy != "":
            httpHandler = urllib3.ProxyManager(proxy_url=http_proxy, cert_reqs=ssl.CERT_REQUIRED)
        else:
            httpHandler = urllib3.PoolManager(cert_reqs=ssl.CERT_REQUIRED)

    httpMethod = apiRequest["httpMethod"]
    httpRequestTarget = apiRequest["httpRequestTarget"]

    headers = {}
    fields = {}
    operator = None
    outputTarget = None
    contentFrom = None

    if "headers" in apiRequest:
        headers = apiRequest["headers"]
    if "httpFields" in apiRequest:
        # fields字段需要复制下来
        # 因为后续会不断更新fields的内容，甚至包括二进制的内容（以file文件上传的时候）
        # 这些二进制的内容没有必要（也做不到）记录到扩展日志中
        fields = copy.copy(apiRequest["httpFields"])

    multiPartBoundary = None
    if "multipart" in apiRequest:
        if "Content-Type" in headers.keys() and headers["Content-Type"] is not None:
            contentType = str(headers["Content-Type"])
            contentTypeList = contentType.split(';')
            for contentType in contentTypeList:
                contentType = str(contentType).strip()
                if contentType.startswith("boundary"):
                    multiPartBoundary = re.sub(r"boundary(\s+)?=(\s+)?", "", contentType).strip()
        else:
            yield {
                "type": "error",
                "message": "Testcli-0000: " +
                           "Missed part Content-Disposition:name in multiPart header."
            }
            return
        if multiPartBoundary is None:
            yield {
                "type": "error",
                "message": "Testcli-0000: " +
                           "Missed multiPart boundary in header."
            }
            return
        for multiPart in apiRequest["multipart"]:
            if "headers" in multiPart.keys() and multiPart["headers"] is not None:
                multiPartHeader = multiPart["headers"]
                if "Content-Disposition" in multiPartHeader.keys() \
                        and multiPartHeader["Content-Disposition"] is not None:
                    contentDisposition = multiPartHeader["Content-Disposition"]
                    contentDispositions = contentDisposition.split(";")
                    contentDispositionName = None
                    contentDispositionFileName = None
                    for contentDisposition in contentDispositions:
                        contentDisposition = str(contentDisposition).strip()
                        if str(contentDisposition).startswith("filename"):
                            contentDispositionFileName = \
                                re.sub(r"filename(\s+)?=(\s+)?", "", contentDisposition).strip()
                            if contentDispositionFileName.startswith('"') and \
                                    contentDispositionFileName.endswith('"'):
                                contentDispositionFileName = contentDispositionFileName[1:-1]
                            if contentDispositionFileName.startswith("'") and \
                                    contentDispositionFileName.endswith("'"):
                                contentDispositionFileName = contentDispositionFileName[1:-1]
                        if str(contentDisposition).startswith("name"):
                            contentDispositionName = \
                                re.sub(r"name(\s+)?=(\s+)?", "", contentDisposition).strip()
                            if contentDispositionName.startswith('"') and \
                                    contentDispositionName.endswith('"'):
                                contentDispositionName = contentDispositionName[1:-1]
                            if contentDispositionName.startswith("'") and \
                                    contentDispositionName.endswith("'"):
                                contentDispositionName = contentDispositionName[1:-1]
                    if contentDispositionName is None:
                        yield {
                            "type": "error",
                            "message": "Testcli-0000: " +
                                       "Missed part Content-Disposition:name in multiPart header."
                        }
                        return
                    if contentDispositionFileName is None:
                        # 上传的内容是一个文本内容
                        multiPartContent = "".join(multiPart["contents"])
                        fields[contentDispositionName] = (None, multiPartContent)
                    else:
                        # 上传的内容是一个文件
                        contentFrom = None
                        if "operate" in multiPart.keys() and multiPart["operate"] is not None:
                            if len(multiPart["operate"]) == 1:
                                multiPartOperate = multiPart["operate"][0]
                                if "content" in multiPartOperate.keys():
                                    contentFrom = multiPartOperate["content"].strip()
                        if contentFrom is None:
                            # 将当前的文本作为上传数据的一部分
                            multiPartContent = "".join(multiPart["contents"])
                            body = multiPartContent.encode(cls.testOptions.get("SCRIPT_ENCODING"))
                            fields[contentDispositionName] = (contentDispositionFileName, body)
                        else:
                            # 如果指定了数据从文件中获取，则不再分析contents的内容
                            if not os.path.exists(contentFrom):
                                yield {
                                    "type": "error",
                                    "message": "Testcli-0000: " + "File [" + str(contentFrom) + "] does not exist."
                                }
                                return
                            with open(contentFrom, mode="rb") as f:
                                body = f.read()
                            fields[contentDispositionName] = (contentDispositionFileName, body)
                        pass
                else:
                    yield {
                        "type": "error",
                        "message": "Testcli-0000: " + "Missed part Content-Disposition in multiPart content."
                    }
                    return
            else:
                yield {
                    "type": "error",
                    "message": "Testcli-0000: " + "Missed part header in multiPart content."
                }
                return

    if "operate" in apiRequest.keys() and apiRequest["operate"] is not None:
        if len(apiRequest["operate"]) == 1:
            operate = apiRequest["operate"][0]
            operator = operate["operator"]
            if operator in [">", ">>"]:
                outputTarget = operate["content"].strip()
            if operator in ["<"]:
                contentFrom = operate["content"].strip()

    if contentFrom is not None:
        # 如果指定了数据从文件中获取，则不再分析contents的内容
        with open(contentFrom, mode="rb") as f:
            body = f.read()
    else:
        if "contents" in apiRequest:
            body = "".join(apiRequest["contents"])
        else:
            body = ""
        if len(fields) != 0:
            # 如果填写了fields字段，且body中仅仅包含一个换行符，则标记body为空字符串
            # Python的urllib3不容许同时出现fields和body内容
            if body.strip() == "":
                body = None
        if body is not None:
            body = body.encode(cls.testOptions.get("SCRIPT_ENCODING"))
            # 重置Header的Content-Length
            headers["Content-Length"] = len(body)
        else:
            # 重置Header的Content-Length
            headers["Content-Length"] = 0
    try:
        if cls.timeout == -1:
            timeoutLimit = None
        else:
            timeoutLimit = cls.timeout
        args = {
            "method": httpMethod,
            "url": httpRequestTarget,
            "fields": fields,
            "headers": headers,
            "timeout": timeoutLimit
        }
        if body is not None:
            args["body"] = body
        if multiPartBoundary is not None:
            args["multipart_boundary"] = multiPartBoundary

        # ret = httpHandler.request(**args)
        ret = httpHandler.request(**args)
        result = {"status": ret.status}
        if outputTarget is not None:
            result["content"] = None
            # 将API执行结果输出到文件中
            mode = None
            if operator == ">":
                mode = "wb"
            if operator == ">>":
                mode = "ab"
            with open(outputTarget, mode=mode) as f:
                f.write(ret.data)
        else:
            data = ret.data.decode('utf-8')
            try:
                data = json.loads(data)
            except JSONDecodeError:
                # 返回的对象不是一个JSON
                pass
            result["content"] = data
        result = json.dumps(obj=result,
                            sort_keys=True,
                            indent=4,
                            separators=(',', ': '),
                            ensure_ascii=False)
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": result
        }
        return
    except urllib3.exceptions.MaxRetryError as ue:
        if cls.timeOutMode == "COMMAND":
            if cls.testOptions.get("API_TIMEOUT") != "-1":
                message = "Request timeout limit command threshold [" + \
                          str(cls.testOptions.get("API_TIMEOUT")) + "] reached."
            else:
                message = str(ue)
        else:
            if cls.testOptions.get("SCRIPT_TIMEOUT") != "-1":
                message = "Request timeout limit script threshold [" + \
                          str(cls.testOptions.get("SCRIPT_TIMEOUT")) + "] reached."
            else:
                message = str(ue)
        yield {
            "type": "error",
            "message": "Testcli-0000: " + message
        }
        return
    except Exception as ex:
        yield {
            "type": "error",
            "message": "Testcli-0000: " + str(ex)
        }
        return
