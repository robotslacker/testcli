# -*- coding:utf-8 -*-
import os
import re
import sys

from .httpexception import HTTPException
from .apiutil import getFileInfo, http_request_method_list, RegularExpression, get_header_list, var_parse, \
    get_api_labels


class HTTPParser:
    def __init__(self, http_file_path):
        self.http_path = http_file_path
        self.source_content = var_parse(getFileInfo(self.http_path))
        self.match_list = RegularExpression()
        self.request_block_list = self.__http_file_parse()

    def __http_file2request_block(self):
        request_index_list = []
        request_content_list = []
        for i in range(len(self.source_content)):
            for j in http_request_method_list():
                line = str(self.source_content[i]).strip()
                if line.find(j) != -1 and line[0: len(j)] == j:
                    request_index_list.append(i)
        # 存储每个request的下标，以便拆分文件内容
        request_index_list.append(len(self.source_content))
        if len(request_index_list) > 1:
            for i in range(1, len(request_index_list)):
                start_index = request_index_list[i - 1]
                if request_index_list[i] != 0 and \
                        re.search(self.match_list.request_block_match, self.source_content[start_index - 1].strip(), re.M | re.I):
                    start_index = start_index - 1
                end_index = request_index_list[i]
                if self.source_content[end_index - 1].find("# @name") != -1:
                    end_index = request_index_list[i] - 1
                # 过滤其中的注释，只存储有用信息
                tmp_content_list = [i for i in self.source_content[start_index: end_index] if i.find("###") == -1]
                request_content_list.append(tmp_content_list)
        return request_content_list

    def __split_request_block(self, request_block):
        request_var_str = ""
        request_str = ""
        match_str = self.match_list.request_block_match
        url_match_str = self.match_list.http_url_match
        http_version_match_str = self.match_list.http_version_match
        request_method, request_url, http_version = "", "", ""
        result_dict = {}
        error_dict = {}
        if re.search(match_str, request_block[0].strip(), re.M | re.I):
            request_var_str = request_block[0].strip()
            request_str = request_block[1].strip()
        else:
            request_str = request_block[0].strip()
        request_str = [i for i in request_str.split(" ") if i != ""]
        if request_var_str != "":
            request_var_name = request_var_str.replace("# @name ", "").strip()
        request_method = request_str[0].strip()
        if len(request_str) == 2:
            request_url = request_str[1].strip()
            http_version = None
        elif len(request_str) == 3:
            request_url = request_str[1].strip()
            http_version = request_str[2].strip()
        else:
            request_url = request_str[1].strip()
            http_version = request_str[2].strip()
            invalid_pars = request_str[3: len(request_str) + 1]
            error_dict.update({"INVALID PARAMETER ERROR": "Invalid request format: " + " ".join(invalid_pars)})
            raise HTTPException(r"[INVALID PARAMETER ERROR]: Invalid request format: %s" % " ".join(invalid_pars))
        match_result = re.search(self.match_list.api_ip_match, request_url, re.M | re.I)
        if os.environ.get("Label_ID"):
            if match_result:
                api_ip = get_api_labels('$.API_IP')
                api_ip = api_ip if api_ip is not None else os.environ.get("Label_ID")
                request_url = request_url.replace(match_result.group(), api_ip)
            else:
                pass
        else:
            if match_result:
                error_dict.update({"INVALID VAR ERROR": "%s: unable to find Label_ID" % match_result.group()})
                raise HTTPException(r"[INVALID VAR ERROR]: %s: unable to find Label_ID" % match_result.group())
            else:
                pass
        match_result = re.search(self.match_list.api_port_match, request_url, re.M | re.I)
        if os.environ.get("API_PORT"):
            if match_result:
                api_port = get_api_labels('$.API_PORT')
                api_port = api_port if api_port is not None else os.environ.get("API_PORT")
                request_url = request_url.replace(match_result.group(), api_port)
            else:
                pass
        else:
            if match_result:
                raise HTTPException(r"[INVALID VAR ERROR]: %s: unable to find API_PORT" % match_result.group())
            else:
                pass
        # request 获取
        header_list = []
        body_str = ""
        request_block = [i for i in request_block if i != '\n']
        last_header_location = 0
        # header 获取
        boundary = None
        for i in range(len(request_block)):
            line = str(request_block[i]).strip()
            if boundary is not None and line.strip() == "--" + boundary:
                break
            else:
                for j in get_header_list():
                    if line.find(j) != -1 and line[0: len(j)] == j:
                        if line.find("Content-Type: ") != -1 and line.find("boundary=") != -1:
                            boundary = line.split("boundary=")[1]
                            last_header_location = i
                            header_list.append(request_block[i])
                        else:
                            last_header_location = i
                            header_list.append(request_block[i])
                        break
        header_dict = {}
        for i in header_list:
            line = i.strip().split(":")
            header_dict.update({line[0]: "".join(line[1: len(line)]).strip()})
        # body 获取，将其拆分为request block dict和error block
        body_str = body_str.join(request_block[last_header_location + 1: len(request_block)])
        result_dict.update({"REQUEST ALIAS": request_var_name})
        result_dict.update({"REQUEST METHOD": request_method})
        result_dict.update({"REQUEST URL": request_url})
        result_dict.update({"HTTP VERSION": http_version})
        result_dict.update({"REQUEST HEADER": header_dict})
        result_dict.update({"REQUEST BODY": body_str.strip()})
        return result_dict, error_dict

    def __http_file_parse(self):
        request_parse_list = []
        request_content_list = self.__http_file2request_block()
        if len(request_content_list) == 0:
            print("ERROR: Invalid file containing no request")
        for i in request_content_list:
            request_block, error_dict = self.__split_request_block(i)
            tmp_dict = {}
            # print({"REQUEST BLOCK": request_block})
            # print({"ERROR BLOCK": error_dict})
            tmp_dict.update({"REQUEST BLOCK": request_block})
            tmp_dict.update({"ERROR BLOCK": error_dict})
            request_parse_list.append(tmp_dict)
        return request_parse_list


if __name__ == "__main__":
    path = sys.argv[1]
    request_block_list = HTTPParser(path).request_block_list
    for i in request_block_list:
        print(i, end="")
        print()
        print('--'*20)