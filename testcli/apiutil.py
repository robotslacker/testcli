# -*- coding:utf-8 -*-
import base64
import configparser
import hashlib
import json
import os
import re
from urllib import parse

import mysql.connector
from jsonpath import jsonpath
from pip._vendor import chardet


def getFileInfo(file_path):
    """
    获取文件内容
    :param file_path:
    :return: 返回文件内容的list
    """
    f = open(file_path, 'rb')
    data = f.read()
    file_encoding = chardet.detect(data).get('encoding')
    f.close()
    # print("file encoding: "+file_encoding)
    # print(file_path)
    if file_encoding == 'ISO-8859-1' or file_encoding == 'Windows-1254' or file_encoding == 'GB2312':
        file_encoding = 'gbk'
    with open(file_path, 'r+', encoding=file_encoding) as file:
        return file.readlines()


def writeFile(file_path, file_content_list, additional):
    """
    生成文件并写入数据
    :param file_path:
    :param file_content_list:
    :param additional:
    :return:
    """
    additional_flag = False
    if additional:
        additional_flag = 'a+'
    elif not additional:
        additional_flag = 'w+'
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    file_encoding = 'utf-8'
    if os.path.exists(file_path):
        f = open(file_path, 'rb')
        data = f.read()
        file_encoding = chardet.detect(data).get('encoding')
        f.close()
    if file_encoding == 'ISO-8859-1' or file_encoding == 'Windows-1254' or file_encoding == 'GB2312':
        file_encoding = 'gbk'
    elif file_encoding == 'ascii' or file_encoding == 'Windows-1252':
        file_encoding = 'utf-8'
    with open(file_path, additional_flag, encoding=file_encoding) as file:
        for line in file_content_list:
            tmp_str = ''
            if str(line)[len(str(line)) - 1: len(str(line))] != '\n':
                tmp_str = str(line) + '\n'
            else:
                tmp_str = str(line)
            file.write(tmp_str)


def http_request_method_list():
    """
    http请求所包含的关键字
    :return: http request keyword list
    """
    return ["POST", "GET", "OPTIONS", "HEAD",
            "PUT", "DELETE", "TRACE", "PATCH",
            "CONNECT", "MOVE", "COPY", "LINK",
            "UNLINK", "WRAPPED"]


def request_header_list():
    """
    http request header包含的关键字
    :return: http request header list
    """
    return ["Accept: ", "Accept-Charset: ", "Accept-Encoding: ", "Accept-Language: ",
            "Accept-Ranges: ", "Authorization: ", "Cache-Control: ", "Connection: ",
            "Cookie: ", "Content-Length: ", "Content-Type: ", "Date: ", "Expect: ",
            "From: ", "Host: ", "If-Match: ", "If-Modified-Since	: ", "If-None-Match: ",
            "If-Range: ", "If-Unmodified-Since: ", "Max-Forwards: ", "Pragma: ", "Proxy-Authorization: ",
            "Range: ", "Referer: ", "TE: ", "Upgrade: ", "User-Agent: ", "Via: ", "Warning: ", "X-AUTH-TOKEN: ",
            "x-access-token: ", "Content-Disposition: ", "Language: "]


def response_header_list():
    """
    http response header包含的关键字
    :return:
    """
    return ["Accept-Ranges: ", "Age: ", "Allow: ", "Cache-Control: ", "Content-Encoding	: ",
            "Content-Language	: ", "Content-Length: ", "Content-Location	: ", "Content-MD5: ",
            "Content-Range: ", "Content-Type: ", "Date: ", "ETag: ", "Expires: ", "Last-Modified: ",
            "Location: ", "Pragma: ", "Proxy-Authenticate: ", "refresh: ", "Retry-After: ", "Server: ",
            "Set-Cookie: ", "Trailer: ", "Transfer-Encoding: ", "Vary: ", "Via: ", "Warning: ",
            "WWW-Authenticate: ", "Content-Disposition: "]


def get_header_list():
    """
    http文件中header包含的关键字
    :return: http header list
    """
    return list(set(request_header_list() + response_header_list()))


def http_mime_type_list():
    """
    mime_type的类型
    :return: mime type list
    """
    return ["text/html", "text/plain", "text/xml",
            "image/gif", "image/jpeg", "image/png",
            "application/xhtml+xml", "application/xml",
            "application/atom+xml", "application/json",
            "application/pdf", "application/msword",
            "application/octet-stream", "application/x-www-form-urlencoded",
            "multipart/form-data"]


def case_keyword_list():
    """
    测试用例关键字
    :return: case keyword list
    """
    return [r"^SET\s*SLEEP.*", r"^SET\s*TIMEOUT.*", r"^SET\s*RETRY.*INTERVAL.*",
            r"^ASSERT.*", "^//.*", r"^--\s*\[\s*scenario\s*:.*]$",
            r"^--\s*\[\s*setup\s*:.*]$", r"^--\s*\[\s*cleanup\s*:.*]$"]


def case_keyword_list1():
    """
    测试用例关键字
    :return: case keyword list
    """
    return [r"^SET\s*SLEEP.*", r"^SET\s*TIMEOUT.*", r"^SET\s*RETRY.*INTERVAL.*",
            r"^ASSERT.*", "^//.*", r"^--\s*\[\s*scenario\s*:.*]$",
            r"^--\s*\[\s*setup\s*:.*]$", r"^--\s*\[\s*cleanup\s*:.*]$", r"^@.*=.*"]


def is_json(test_str):
    """
    判断字符串是否为json串
    :param test_str:
    :return: TRUE or FALSE
    """
    try:
        json.loads(test_str)
    except Exception:
        return False
    return True


def var_parse(content_list):
    """
    解析文件中的变量
    :param content_list: http文件内容
    :return: 变量替换后的文件内容
    """
    call_match_str = r"call\s{1,}.*.http"
    match_str = r"^@.*=.*"
    var_key_list = []
    var_value_list = []
    var_index_list = []
    for i in range(len(content_list)):
        var_line = content_list[i]
        if re.search(match_str, var_line, re.M | re.I) and re.search(call_match_str, var_line, re.M | re.I) is None:
            split_var_line = var_line.split("=", maxsplit=1)
            var_key_list.append(split_var_line[0].strip().replace("@", ""))
            var_value_list.append("".join(split_var_line[1: len(split_var_line)]).strip())
            var_index_list.append(i)
    distinct_var_key_list = list(set(var_key_list))
    user_define_var_list = []
    # 记录变量信息，其中有重复利用的变量名称，所以进行分块处理
    for i in distinct_var_key_list:
        tmp_index_list = []
        tmp_value_list = []
        for idx, val in enumerate(var_key_list):
            if val == i:
                tmp_index_list.append(var_index_list[idx])
                tmp_value_list.append(var_value_list[idx])
        tmp_index_list.append(len(content_list))
        user_define_var_list.append([i, tmp_index_list, tmp_value_list])
    # 将变量替换为常量
    for i in user_define_var_list:
        for j in range(len(i[1])):
            if i[1][j - 1] < i[1][j]:
                for k in range(i[1][j - 1], i[1][j]):
                    if content_list[k].find("{{%s}}" % i[0]) != -1:
                        content_list[k] = content_list[k].replace("{{%s}}" % i[0], i[2][j - 1])
    # 过滤变量设定的操作
    pop_count = 0
    for i in var_index_list:
        content_list.pop(i - pop_count)
        pop_count += 1
    return content_list


def get_json_value_by_key(source_dict, key):
    """
    根据节点名查找相应value值
    :param source_dict:
    :param key:
    :return:
    """
    separator = '.'
    separator_keys = None
    if key.find(separator) != -1:
        separator_keys = key.split('.')
    else:
        return source_dict.get(key)
    finalValue = None
    for i in range(0, len(separator_keys) - 1):
        if i == 0:
            if isinstance(source_dict, str):
                finalValue = json.loads(json.loads(json.dumps(str(source_dict)))).get(separator_keys[i])
            else:
                finalValue = source_dict.get(separator_keys[i])
            continue
        if finalValue is None:
            break
        if isinstance(finalValue, str):
            finalValue = json.loads(json.loads(json.dumps(str(finalValue)))).get(separator_keys[i])
        else:
            finalValue = finalValue.get(separator_keys[i])
    if isinstance(finalValue, str):
        finalValue = json.loads(json.loads(json.dumps(str(finalValue))))
    return None if finalValue is None else finalValue.get(separator_keys[len(separator_keys) - 1])


def get_content_by_key(source_obj, key):
    inner_fun_result = InnerFunction(source_obj)
    separator = ').'
    separator_keys = key.split(separator)
    separator_keys = separator_keys if len(separator_keys) == 1 else ["%s)" % i if i.endswith(")") is False else i for i
                                                                      in key.split(separator)]
    rx = RegularExpression()
    for i in separator_keys:
        if re.search(r"^%s$" % rx.fun_json_path_match, i, re.I | re.M):
            par = i[0: len(i)-1].replace("json_path(", "").strip()
            par = par[1: len(par)-1].strip()
            inner_fun_result = inner_fun_result.json_path(par)
        elif re.search(r"^%s$" % rx.fun_contain_match, i, re.I | re.M):
            par = i.split('\'')[1]
            inner_fun_result = inner_fun_result.contain(par)
        elif re.search(r"^%s$" % rx.fun_sub_content, i, re.I | re.M):
            split_list = i.lower().split(",")
            par1 = int(split_list[0].replace("sub_content(", "").strip())
            par2 = int(split_list[1].replace(")", "").strip())
            inner_fun_result = inner_fun_result.sub_content(par1, par2)
        elif re.search(r"^%s$" % rx.fun_md5_match, i, re.I | re.M):
            inner_fun_result = inner_fun_result.md5()
        elif re.search(r"^%s$" % rx.fun_base64_match, i, re.I | re.M):
            inner_fun_result = inner_fun_result.base64()
        elif re.search(r"^%s$" % rx.fun_sha1_match, i, re.I | re.M):
            inner_fun_result = inner_fun_result.sha1()
        elif re.search(r"^%s$" % rx.fun_quote_match, i, re.I | re.M):
            inner_fun_result = inner_fun_result.quote()
        elif re.search(r"^%s$" % rx.fun_unquote_match, i, re.I | re.M):
            inner_fun_result = inner_fun_result.unquote()
        elif re.search(r"^%s$" % rx.fun_len_match, i, re.I | re.M):
            inner_fun_result = inner_fun_result.len()
        else:
            return None
    return inner_fun_result.execute_result


def get_api_labels(expr):
    cf = configparser.ConfigParser()
    m_Configfile = os.path.join(os.path.dirname(__file__), "../testenv.ini")
    cf.read(m_Configfile)
    m_host = cf.get("TestReportDB", "host")
    m_user = cf.get("TestReportDB", "user")
    m_passwd = cf.get("TestReportDB", "passwd")
    m_database = cf.get("TestReportDB", "database")

    # 连接mysql数据库, 用来记录测试结果
    mydb = mysql.connector.connect(
        host=m_host,
        user=m_user,
        passwd=m_passwd,
        database=m_database,
        auth_plugin='mysql_native_password'
    )

    # 首先查看Common的环境配置
    m_strSQL = "select json_extract(`Build_Tag`, '" + expr + "') from labels where `Label_ID` like '" + os.environ['Label_ID'] + "'"
    cursor = mydb.cursor()
    cursor.execute(m_strSQL)
    rawData = cursor.fetchall()
    commonresult = []
    for row in rawData:
        for index, value in enumerate(row):
            commonresult.append(value)
    cursor.close()
    if len(commonresult) == 1:
        return commonresult[0].replace("\"", "")
    elif len(commonresult) == 0:
        return None
    else:
        return commonresult[0].replace("\"", "")


class InnerFunction:
    def __init__(self, source_obj, execute_result="⌓‿⌓​"):
        self.source_obj = source_obj
        if isinstance(execute_result, list):
            if len(execute_result) == 1:
                self.execute_result = execute_result[0]
            elif len(execute_result) == 0:
                self.execute_result = None
            else:
                self.execute_result = execute_result
        else:
            self.execute_result = execute_result

    def json_path(self, expr):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        if is_json(performed_obj):
            json_result = jsonpath(json.loads(performed_obj), expr)
        else:
            json_result = jsonpath(performed_obj, expr)
        self.source_obj = performed_obj
        self.execute_result = None if json_result is False else json_result
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def contain(self, expr):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        self.execute_result = None if performed_obj is None else (
            str(True) if str(performed_obj).find(expr) != -1 else str(False))
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def sub_content(self, start_idx, end_idx):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        self.execute_result = None if performed_obj is None else self.source_obj[start_idx: end_idx]
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def md5(self):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        if performed_obj is None:
            self.execute_result = None
        else:
            md5 = hashlib.md5()
            md5.update(str(self.source_obj).encode(encoding='utf-8'))
            self.execute_result = md5.hexdigest()
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def base64(self):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        if performed_obj is None:
            self.execute_result = None
        else:
            self.execute_result = base64.b64encode(str(self.source_obj).encode('utf-8')).decode('utf-8')
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def sha1(self):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        if performed_obj is None:
            self.execute_result = None
        else:
            self.execute_result = hashlib.sha1(str(self.source_obj).encode('utf-8')).hexdigest()
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def quote(self):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        if performed_obj is None:
            self.execute_result = None
        else:
            self.execute_result = parse.quote(self.source_obj)
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def unquote(self):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        if performed_obj is None:
            self.execute_result = None
        else:
            self.execute_result = parse.unquote(self.source_obj)
        return InnerFunction(self.source_obj, execute_result=self.execute_result)

    def len(self):
        performed_obj = self.source_obj if self.execute_result == "⌓‿⌓​" else self.execute_result
        if self.execute_result == str(True):
            performed_obj = self.source_obj
        elif self.execute_result == str(False):
            performed_obj = None
        self.source_obj = performed_obj
        if performed_obj is None:
            self.execute_result = None
        else:
            self.execute_result = str(len(self.source_obj))
        return InnerFunction(self.source_obj, execute_result=self.execute_result)


class RegularExpression:
    def __init__(self):
        self.request_block_match = r"^# @name .*"
        self.http_url_match = r"^(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"
        self.http_version_match = r"HTTP/\d.\d"
        self.iterator_match = r"^--ITERATOR:"
        self.http_file_match = r"call\s{1,}.*.http"
        self.call_http_match = r"call\s{1,}.*.http\s{1,}{.*}"
        self.assert_match = r"^ASSERT\s{1,}.*"
        self.define_var_match = r"^@.*=.*"
        self.or_match = r"\s{1,}or\s{1,}"
        self.and_match = r"\s{1,}and\s{1,}"
        self.scenario_begin_match = r"^--\s*\[\s*scenario\s*:\s*"
        self.setup_begin_match = r"^--\s*\[\s*setup\s*:\s*"
        self.cleanup_begin_match = r"^--\s*\[\s*cleanup\s*:\s*"
        self.end_match = r"\s*end\s*\]$"
        self.sleep_match = r"^SET\s{1,}SLEEP\s{1,}\d{1,}([s,h,m]|)$"
        self.timeout_match = r"^SET\s{1,}TIMEOUT\s{1,}\d{1,}([s,h,m]|)$"
        self.retry_match = r"^SET\s{1,}RETRY\s{1,}\d{1,}\s{1,}INTERVAL\s{1,}\d{1,}([s,h,m]|)$"
        self.ip_match = r"((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}\d{1,3}"
        self.api_ip_match = r"\{\{\s*ENV\s*\(\s*API_IP\s*\)\s*\}\}"
        self.api_ip_match = r"\{\{\s*ENV\s*\(\s*API_IP\s*\)\s*\}\}"
        self.api_port_match = r"\{\{\s*ENV\s*\(\s*API_PORT\s*\)\s*\}\}"
        self.fun_json_path_match = r"json_path\(\s*'.*'\s*\)"
        self.fun_contain_match = r"contain\(\s*'.*'\s*\)"
        self.fun_sub_content = r"sub_content\(\s*\d+\s*,\s*\d+\s*\)"
        self.fun_md5_match = r"md5\(\s*\)"
        self.fun_base64_match = r"base64\(\s*\)"
        self.fun_sha1_match = r"sha1\(\s*\)"
        self.fun_quote_match = r"quote\(\s*\)"
        self.fun_unquote_match = r"unquote\(\s*\)"
        self.fun_len_match = r"len\(\s*\)"
        self.fun_list = [self.fun_json_path_match, self.fun_contain_match, self.fun_sub_content,
                         self.fun_md5_match, self.fun_base64_match, self.fun_sha1_match,
                         self.fun_quote_match, self.fun_unquote_match, self.fun_len_match]
