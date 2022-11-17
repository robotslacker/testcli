import json
import os
import re
import sys

import requests
from requests.adapters import HTTPAdapter, Retry

from .httpexception import HTTPException
from .apiutil import is_json, get_content_by_key
from .httpfileparser import HTTPParser


class HTTPExecutor:
    def __init__(self, http_file_path, timeout=10, retry_count=0, retry_interval=1):
        if isinstance(http_file_path, str):
            self.http_path = http_file_path
            self.request_block_list = HTTPParser(self.http_path).request_block_list
        else:
            self.http_path = None
            self.request_block_list = http_file_path
        self.execute_timeout = timeout
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        self.execute_result = self.__execute_http_file()

    def __execute_request_block(self, parse_request_block):
        result_dict = {}
        request_block_dict = parse_request_block.get("REQUEST BLOCK")
        error_block_dict = parse_request_block.get("ERROR BLOCK")
        if len(error_block_dict) == 0:
            request_alias = request_block_dict.get("REQUEST ALIAS")
            request_method = request_block_dict.get("REQUEST METHOD")
            request_url = request_block_dict.get("REQUEST URL")
            request_version = request_block_dict.get("REQUEST VERSION")
            request_headers = request_block_dict.get("REQUEST HEADER")
            request_body = request_block_dict.get("REQUEST BODY")
            test_data = request_body
            test_files = None
            content_type = dict(request_headers).get("Content-Type")
            if content_type == "application/x-www-form-urlencoded" or content_type is None:
                test_data = request_body.encode('utf-8')
            elif content_type == "application/json":
                if is_json(request_body):
                    test_data = json.dumps(json.loads(request_body), ensure_ascii=False)
                else:
                    test_data = request_body
            elif content_type == "application/xml":
                test_data = request_body.encode('utf-8')
            elif str(content_type).find('boundary='):
                boundary = "--" + str(content_type).split("boundary=")[1] + "\n"
                split_body = [i for i in str(request_body).split(boundary) if i != ""]
                for i in split_body:
                    body_part = [j.strip() for j in i.split("\n") if j != ""]
                    if body_part[0].find("name=\"param\"") != -1:
                        test_data = {'param': " ".join(body_part[1: len(body_part)+1])}
                    elif body_part[0].find("name=\"file\"") != -1:
                        test_files = []
                        file_type = None
                        file_path = None
                        if body_part[1].find("Content-Type: ") != -1:
                            con_type = None
                            for tmp_i in ([k.strip() for k in body_part[0].split(";") if k != ""] + [body_part[1]]):
                                if re.search("^name=", tmp_i, re.M | re.I):
                                    file_type = tmp_i.replace("name=", "").replace("\"", "").strip()
                                elif re.search("^filename=", tmp_i, re.M | re.I):
                                    file_path = tmp_i.replace("filename=", "").replace("\"", "").strip()
                                elif tmp_i.find("Content-Type: ") != -1:
                                    con_type = tmp_i.replace("Content-Type: ", "").replace("\"", "").strip()
                            test_files.append((file_type, (os.path.basename(file_path), open(file_path, 'rb'), con_type)))
                        else:
                            for tmp_i in [k for k in body_part[0].split(";") if k != ""] + [body_part[1]]:
                                if re.search("^name=", tmp_i, re.M | re.I):
                                    file_type = tmp_i.replace("name=", "").replace("\"", "").strip()
                                elif re.search("^filename=", tmp_i, re.M | re.I):
                                    file_path = tmp_i.replace("filename=", "").replace("\"", "").strip()
                            test_files.append((file_type, (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream')))
                    else:
                        pass
            else:
                test_data = request_body
            result = None
            if test_data is not None and len(test_data) != 0 and isinstance(test_data, str):
                test_data = test_data.encode('utf-8')
            try:
                request_method_list = frozenset(["POST", "POST", "OPTIONS", "HEAD", "PUT", "DELETE", "TRACE", "PATCH"])
                request = requests.Session()
                request.mount("https://", HTTPAdapter(
                    max_retries=Retry(total=self.retry_count, method_whitelist=request_method_list,
                                      backoff_factor=self.retry_interval)))
                if request_method == "POST":
                    if test_files:
                        result = requests.post(request_url, data=test_data, timeout=self.execute_timeout,
                                               files=test_files)
                    else:
                        result = request.post(request_url, data=test_data, headers=request_headers,
                                              timeout=self.execute_timeout, files=test_files)
                elif request_method == "GET":
                    result = request.get(request_url, params=test_data, headers=request_headers,
                                         timeout=self.execute_timeout)
                elif request_method == "OPTIONS":
                    result = request.options(request_url, data=test_data, headers=request_headers,
                                             timeout=self.execute_timeout)
                elif request_method == "HEAD":
                    result = request.head(request_url, data=test_data, headers=request_headers,
                                          timeout=self.execute_timeout)
                elif request_method == "PUT":
                    if test_files:
                        result = request.put(request_url, data=test_data, timeout=self.execute_timeout,
                                             files=test_files)
                    else:
                        result = request.put(request_url, data=test_data, headers=request_headers,
                                             timeout=self.execute_timeout, files=test_files)
                elif request_method == "DELETE":
                    result = request.delete(request_url, data=test_data, headers=request_headers,
                                            timeout=self.execute_timeout)
                elif request_method == "TRACE":
                    pass
                elif request_method == "PATCH":
                    result = request.patch(request_url, data=test_data, headers=request_headers,
                                           timeout=self.execute_timeout)
                elif request_method == "CONNECT":
                    pass
                elif request_method == "MOVE":
                    pass
                elif request_method == "COPY":
                    pass
                elif request_method == "LINK":
                    pass
                elif request_method == "UNLINK":
                    pass
                elif request_method == "WRAPPED":
                    pass
                else:
                    pass
                result.encoding = "utf-8"
                response_header = result.headers
                request_header = result.request.headers
                response_content = result.text if result.text != "" else ""
                response_status_code = result.status_code
                # 每个request block返回的结果包含内容
                result_dict.update({"request_alias": request_alias})
                result_dict.update({"request_method": request_method})
                result_dict.update({"request_url": request_url})
                result_dict.update({"request_header": dict(request_header)})
                result_dict.update({"request_body": request_body})
                result_dict.update({"request_timeout": self.execute_timeout})
                result_dict.update({"request_retry_total_count": self.retry_count})
                result_dict.update({"request_retry_interval": self.retry_interval})
                result_dict.update({"response_header": dict(response_header)})
                # result_dict.update({"response_content": response_content})
                result_dict.update({"response_content": json.loads(response_content) if is_json(response_content) else response_content})
                result_dict.update({"response_status_code": response_status_code})
            except Exception as e:
                result_dict.update({"CONNECTION ERROR": str(e)})
                raise HTTPException(r"[CONNECTION ERROR]: %s" % str(e))
        else:
            result_dict = error_block_dict
        return result_dict

    def __get_request_var_dependence(self):
        request_block_name = [
            r"{{\s*%s\s*}}.(?:json_path\(.*\)|contain\(.*\)|sub_content\(.*\))" % i.get('REQUEST BLOCK').get(
                'REQUEST ALIAS') for i in self.request_block_list]
        request_var_dependence = []
        request_block_list = []
        for i in self.request_block_list:
            request_block_list.append(i.get("REQUEST BLOCK"))
        for i in request_block_list:
            var_flag = False
            tmp_var_list = []
            for j in request_block_name:
                request_block_var = re.findall(j, str(i), re.M | re.I)
                if len(request_block_var) != 0:
                    tmp_var_list += request_block_var
                    var_flag = True
            if not var_flag:
                tmp_dict = {}
                tmp_dict.update({"CHILD ELEMENT": i.get('REQUEST ALIAS')})
                tmp_dict.update({"VAR VALUE": []})
                request_var_dependence.append(tmp_dict)
            else:
                tmp_dict = {}
                tmp_dict.update({"CHILD ELEMENT": i.get('REQUEST ALIAS')})
                tmp_dict.update({"VAR VALUE": tmp_var_list})
                request_var_dependence.append(tmp_dict)
        return request_var_dependence

    def __execute_http_file(self):
        execute_result = {}
        var_dependence = self.__get_request_var_dependence()
        for i in range(len(self.request_block_list)):
            request_block = self.request_block_list[i].get("REQUEST BLOCK")
            var_value_list = var_dependence[i].get('VAR VALUE')
            if len(var_value_list) != 0:
                for j in var_value_list:
                    var_values = j.replace("{{", "").replace("}}", "").split(".")
                    parent_element_name = var_values[0]
                    parent_element = ".".join(var_values[1: len(var_values)])
                    source_result = eval(execute_result.get(parent_element_name)) if isinstance(
                        execute_result.get(parent_element_name), str) else execute_result.get(parent_element_name)
                    # parent_var_result = get_json_value_by_key(source_result, parent_element)
                    parent_var_result = get_content_by_key(source_result, parent_element)
                    if parent_var_result is not None:
                        block_result = self.__execute_request_block(
                            eval(str(self.request_block_list[i]).replace(j, parent_var_result)))
                        execute_result.update({request_block.get("REQUEST ALIAS"): block_result})
                    else:
                        execute_result.update({request_block.get("REQUEST ALIAS"): {
                            "%s.%s" % (parent_element_name, parent_element): "Invalid variable"}})

            else:
                if len(self.request_block_list[i].get("ERROR BLOCK")) == 0:
                    block_result = self.__execute_request_block(self.request_block_list[i])
                    execute_result.update({request_block.get("REQUEST ALIAS"): block_result})
                else:
                    execute_result.update(
                        {request_block.get("REQUEST ALIAS"): self.request_block_list[i].get("ERROR BLOCK")})
        return execute_result


if __name__ == "__main__":
    path = sys.argv[1]
    request_block_list = HTTPExecutor(path).execute_result
    for i in request_block_list:
        print(i)
        print(json.dumps(request_block_list[i], indent=4, ensure_ascii=False))
