import json
import os
import re
import sys
import time

from .httpexception import HTTPException
from .apiparser import APIParser
from .apiutil import is_json, RegularExpression, get_content_by_key
from .httpexecutor import HTTPExecutor
from .httpfileparser import HTTPParser


class APIExecutor:
    def __init__(self, api_file_path):
        self.api_path = api_file_path
        self.match_list = RegularExpression()
        self.api_parse_list = APIParser(self.api_path).parse_result
        self.execute_log, self.execute_xlog = self.__execute_api()

    def __call_http_file(self, http_file_path, dataset_str, timeout, retry_count, retry_interval):
        http_parser = HTTPParser(http_file_path)
        execute_result = {}
        try:
            content_list = http_parser.request_block_list
        except Exception as e:
            # 判断http文件是否存在，不存在直接报错
            execute_result.update({"[HTTP FILE PATH ERROR]": str(e)})
            raise HTTPException("[HTTP FILE PATH ERROR]:  %s" % str(e))
            return execute_result
        # 判断传入的参数是否满足json格式或dict格式，不满足则直接报错
        if isinstance(dataset_str, dict) or isinstance(dataset_str, str) and is_json(dataset_str):
            if isinstance(dataset_str, str) and is_json(dataset_str):
                dataset_str = json.loads(dataset_str)
            # 将http文件中的变量替换为传入json格式数据对应的值，要注意http文件变量名需与json数据变量名一致，大小写敏感
            match_str_list = [r'{{\s*%s.*?}}' % i for i in dataset_str]
            for i in range(len(content_list)):
                for j in match_str_list:
                    # tmp_line = str(content_list[i])
                    tmp_line = json.dumps(content_list[i], ensure_ascii=False)
                    is_contain_str = re.search(j, tmp_line, re.M | re.I)
                    if is_contain_str is not None:
                        content_list[i] = eval(tmp_line.replace(is_contain_str.group(), str(dataset_str.get(j.replace(r"{{\s*", "").replace(r".*?}}", "")))))
            # 执行替换变量后的http文件
            http_executor = HTTPExecutor(content_list, timeout=timeout, retry_count=retry_count,
                                         retry_interval=retry_interval)
            execute_result = http_executor.execute_result
        else:
            execute_result.update({dataset_str: "ERROR: Invalid argument string, the value is in dict or json format"})
            raise HTTPException("[ARGUMENT ERROR]:  Invalid argument string, the value is in dict or json format")
        return execute_result

    def __handle_assertions(self, var_dict, assert_list):
        assert_result = []
        fail_result = []
        fail_count = 0
        for i in assert_list:
            tmp_fail_result = []
            for j in i:
                operator = None
                actual_result = None
                expect_result = None
                # 目前仅支持 == 与 !=，其预期结果都会转为str，而不做numeric的判断处理
                if j.find("==") != -1:
                    operator = "=="
                    tmp_result = j.split("==")
                    if len(tmp_result) > 2:
                        actual_result = "==".join(tmp_result[0: len(tmp_result) - 1]).strip()
                        expect_result = tmp_result[len(tmp_result) - 1].strip()
                    else:
                        actual_result = tmp_result[0].strip()
                        expect_result = tmp_result[1].strip()
                elif j.find("!=") != -1:
                    operator = "!="
                    tmp_result = j.split("!=")
                    if len(tmp_result) > 2:
                        actual_result = "!=".join(tmp_result[0: len(tmp_result) - 1]).strip()
                        expect_result = tmp_result[len(tmp_result) - 1].strip()
                    else:
                        actual_result = tmp_result[0].strip()
                        expect_result = tmp_result[1].strip()
                else:
                    # 如果不满足以上比较符，则报错
                    tmp_fail_result.append(
                        "[ASSERT OPERATOR ERROR] There is no corresponding comparison operator: %s" % j)
                    raise HTTPException("[ASSERT OPERATOR ERROR] There is no corresponding comparison operator: %s" % j)
                    break
                # 根据http报文变量名匹配对应的结果，若没有找到则为None
                # print(type(actual_result), actual_result)
                # print(type(expect_result), expect_result)
                # print("--"*20)
                for z in var_dict:
                    actual_result = str(actual_result)
                    expect_result = str(expect_result)
                    if actual_result.find("{{%s}}" % z) != -1:
                        actual_result = get_content_by_key(var_dict[z], actual_result.replace("{{%s}}." % z, ""))
                    elif expect_result.find("{{%s}}" % z) != -1:
                        expect_result = get_content_by_key(var_dict[z], expect_result.replace("{{%s}}." % z, ""))
                    else:
                        pass
                # print(actual_result)
                # print(expect_result)
                actual_result = str(actual_result)
                expect_result = str(expect_result)
                # print("=="*20)
                # 支持双引号括起的预期结果
                if actual_result[0] == '"' and actual_result[len(actual_result) - 1] == '"':
                    actual_result = actual_result[1: len(actual_result) - 1]
                if expect_result[0] == '"' and expect_result[len(expect_result) - 1] == '"':
                    expect_result = expect_result[1: len(expect_result) - 1]
                # 判断实际结果与预期结果是否相符
                if operator == "==":
                    if actual_result == expect_result:
                        pass
                    else:
                        tmp_fail_result.append(
                            "[ASSERT RESULT ERROR] Expectations do not correspond with reality: %s, %s" % (
                                actual_result, expect_result))
                        break
                elif operator == "!=":
                    if actual_result != expect_result:
                        pass
                    else:
                        tmp_fail_result.append(
                            "[ASSERT RESULT ERROR] Expectations do not correspond with reality: %s, %s" % (
                                actual_result, expect_result))
                        break
            # 针对于一个assert包含多个判断条件的，统计失败的数量，最后返回断言的结果
            if len(tmp_fail_result) != 0:
                fail_result += tmp_fail_result
                fail_count += 1
        if fail_count == len(assert_list):
            assert_result.append("TEST RESULT: TEST FAILURE")
            assert_result += fail_result
        else:
            assert_result.append("TEST RESULT: TEST PASS")
        return assert_result

    def __execute_api(self):
        call_match_str = self.match_list.call_http_match
        assert_match_str = self.match_list.assert_match
        var_match_str = self.match_list.define_var_match
        cmd_timeout = None
        cmd_sleep = None
        cmd_retry = None
        result_list = []
        var_dict = {}
        # 对于相对路径的解决文件执行路径的方法
        parent_path = os.path.dirname(self.api_path)
        os.chdir(parent_path)
        # 将cases文件中call http file传入的数据平展化，方便之后进行分割
        content_list = self.api_parse_list
        for i in content_list:
            # 先确定执行call http文件的内容，然后再判断其是否有对应的变量来接收执行http文件的结果
            if re.search(call_match_str, i, re.I | re.M):
                if re.search(var_match_str, i, re.I | re.M):
                    # 有相应变量被赋予执行结果的情况
                    split_var = [line.strip() for line in i.split("=", maxsplit=1)]
                    var_name = split_var[0].replace("@", "")
                    var_value = "".join(split_var[1: len(split_var)])
                    http_path = var_value.split(".http")[0].strip()
                    http_path = os.path.abspath(
                        (http_path[4: len(http_path)] + ".http").strip().replace("\\", os.path.sep).replace("/",
                                                                                                            os.path.sep))
                    json_str = var_value.split(".http")[1].strip()
                    replace_json = json_str
                    for tmp_i in dict(eval(json_str)).values():
                        tmp_i = str(tmp_i)
                        if len(var_dict) != 0:
                            for result_var in var_dict:
                                if tmp_i.find("{{%s}}" % result_var) != -1:
                                    # print("AA", var_dict[result_var])
                                    # print("BB", tmp_i.replace("{{%s}}." % result_var, ""))
                                    replace_content = get_content_by_key(var_dict[result_var],
                                                                         tmp_i.replace("{{%s}}." % result_var, ""))
                                    # print("CC", replace_content)
                                    # print("--" * 20)
                                    if replace_content is not None:
                                        replace_json = replace_json.replace(tmp_i, str(replace_content))
                                    else:
                                        replace_json = replace_json.replace(tmp_i, "null")
                                else:
                                    cut_idx = None
                                    for match in self.match_list.fun_list:
                                        tmp_match = re.search(match, tmp_i, re.I | re.M)
                                        if tmp_match:
                                            if cut_idx is not None:
                                                cut_idx = cut_idx if cut_idx < tmp_match.span()[0] else \
                                                    tmp_match.span()[0]
                                            else:
                                                cut_idx = tmp_match.span()[0]
                                        else:
                                            pass
                                    if cut_idx is not None:
                                        replace_content = get_content_by_key(tmp_i[0: cut_idx - 1],
                                                                             tmp_i[cut_idx: len(tmp_i)])
                                        if replace_content:
                                            replace_json = replace_json.replace(tmp_i, str(replace_content))
                        else:
                            cut_idx = None
                            for match in self.match_list.fun_list:
                                tmp_match = re.search(match, tmp_i, re.I | re.M)
                                if tmp_match:
                                    if cut_idx is not None:
                                        cut_idx = cut_idx if cut_idx < tmp_match.span()[0] else tmp_match.span()[0]
                                    else:
                                        cut_idx = tmp_match.span()[0]
                                else:
                                    pass
                            if cut_idx is not None:
                                replace_content = get_content_by_key(tmp_i[0: cut_idx - 1], tmp_i[cut_idx: len(tmp_i)])
                                if replace_content:
                                    replace_json = replace_json.replace(tmp_i, str(replace_content))
                    # 记录http文件执行前的内容
                    result_list.append("Perform before:\n%s" % i.replace(json_str, replace_json))
                    http_result = self.__call_http_file(http_path, replace_json,
                                                        cmd_timeout if cmd_timeout is not None else 10,
                                                        cmd_retry.get("COUNT") if cmd_retry.get(
                                                            "COUNT") is not None else 0,
                                                        cmd_retry.get("INTERVAL") if cmd_retry.get(
                                                            "INTERVAL") is not None else 1)
                    # 记录http文件执行后的内容
                    result_list.append(
                        "After performing:\n%s\n" % (
                                "@" + var_name + " = " + json.dumps(http_result, indent=4, ensure_ascii=False)))
                    # 将其http文件中每个http block的名称和结果存储到dict中，作为变量替换的参考
                    var_dict.update({var_name: http_result})
                else:
                    # 没有相应变量被赋予执行结果的情况
                    # 操作同上
                    if i.strip().lower()[0:4] == "call":
                        result_list.append("Perform before:\n%s" % i)
                        http_path = i.split(".http")[0].strip()
                        http_path = os.path.abspath(
                            (http_path[4: len(http_path)] + ".http").strip().replace("\\", os.path.sep).replace("/",
                                                                                                                os.path.sep))
                        json_str = i.split(".http")[1].strip()
                        replace_json = json_str
                        for tmp_i in dict(eval(json_str)).values():
                            tmp_i = str(tmp_i)
                            if len(var_dict) != 0:
                                for result_var in var_dict:
                                    if tmp_i.find("{{%s}}" % result_var) != -1:
                                        replace_content = get_content_by_key(var_dict[result_var],
                                                                             tmp_i.replace("{{%s}}." % result_var, ""))
                                        if replace_content is not None:
                                            replace_json = replace_json.replace(tmp_i, str(replace_content))
                                        else:
                                            replace_json = replace_json.replace(tmp_i, "null")
                                    else:
                                        cut_idx = None
                                        for match in self.match_list.fun_list:
                                            tmp_match = re.search(match, tmp_i, re.I | re.M)
                                            if tmp_match:
                                                if cut_idx is not None:
                                                    cut_idx = cut_idx if cut_idx < tmp_match.span()[0] else \
                                                        tmp_match.span()[0]
                                                else:
                                                    cut_idx = tmp_match.span()[0]
                                            else:
                                                pass
                                        if cut_idx is not None:
                                            replace_content = get_content_by_key(tmp_i[0: cut_idx - 1],
                                                                                 tmp_i[cut_idx: len(tmp_i)])
                                            replace_json = replace_json.replace(tmp_i, str(replace_content))
                            else:
                                cut_idx = None
                                for match in self.match_list.fun_list:
                                    tmp_match = re.search(match, tmp_i, re.I | re.M)
                                    if tmp_match:
                                        if cut_idx is not None:
                                            cut_idx = cut_idx if cut_idx < tmp_match.span()[0] else tmp_match.span()[0]
                                        else:
                                            cut_idx = tmp_match.span()[0]
                                    else:
                                        pass
                                if cut_idx is not None:
                                    replace_content = get_content_by_key(tmp_i[0: cut_idx - 1],
                                                                         tmp_i[cut_idx: len(tmp_i)])
                                    replace_json = replace_json.replace(tmp_i, str(replace_content))
                        http_result = self.__call_http_file(http_path, replace_json,
                                                            cmd_timeout if cmd_timeout is not None else 10,
                                                            cmd_retry.get("COUNT") if cmd_retry.get(
                                                                "COUNT") is not None else 0,
                                                            cmd_retry.get("INTERVAL") if cmd_retry.get(
                                                                "INTERVAL") is not None else 1)
                        result_list.append(
                            "After performing:\n%s\n" % (json.dumps(http_result, indent=4, ensure_ascii=False)))
                    else:
                        result_list.append(i)
            # 确定断言的内容，然后将断言判断条件进行拆分，生成一个二维list
            elif re.search(assert_match_str, i, re.I | re.M):
                result_list.append(i)
                assert_list = []
                assert_line = i.strip()[6: len(i.strip())]
                or_match_str = self.match_list.or_match
                and_match_str = self.match_list.and_match
                for j in re.findall(or_match_str, assert_line, re.I | re.M):
                    assert_line = assert_line.replace(j, "@o@")
                or_assert_list = assert_line.split("@o@")
                for j in or_assert_list:
                    tmp_line = j
                    for k in re.findall(and_match_str, j, re.I | re.M):
                        tmp_line = tmp_line.replace(k, "@o@")
                    assert_list.append([a.strip() for a in tmp_line.split("@o@")])
                for j in self.__handle_assertions(var_dict, assert_list):
                    result_list.append(j + "\n")
                result_list.append("\n")
                pass
            # 对于既不是执行http文件命令也不是断言的内容进行记录
            else:
                if re.search(self.match_list.timeout_match, i.strip(), re.I | re.M):
                    tmp_value = i.strip().split(" ")[2].lower().strip()
                    if tmp_value[len(tmp_value) - 1] == "s":
                        cmd_timeout = int(tmp_value[0: len(tmp_value) - 1])
                    elif tmp_value[len(tmp_value) - 1] == "m":
                        cmd_timeout = int(tmp_value[0: len(tmp_value) - 1]) * 60
                    elif tmp_value[len(tmp_value) - 1] == "h":
                        cmd_timeout = int(tmp_value[0: len(tmp_value) - 1]) * 60 * 60
                    else:
                        cmd_timeout = int(tmp_value)
                elif re.search(self.match_list.sleep_match, i.strip(), re.I | re.M):
                    tmp_value = i.strip().split(" ")[2].lower().strip()
                    if tmp_value[len(tmp_value) - 1] == "s":
                        cmd_sleep = int(tmp_value[0: len(tmp_value) - 1])
                    elif tmp_value[len(tmp_value) - 1] == "m":
                        cmd_sleep = int(tmp_value[0: len(tmp_value) - 1]) * 60
                    elif tmp_value[len(tmp_value) - 1] == "h":
                        cmd_sleep = int(tmp_value[0: len(tmp_value) - 1]) * 60 * 60
                    else:
                        cmd_sleep = int(tmp_value)
                    time.sleep(cmd_sleep)
                elif re.search(self.match_list.retry_match, i.strip(), re.I | re.M):
                    tmp_value = i.strip().split(" ")
                    retry_count = int(tmp_value[2].strip())
                    retry_interval = tmp_value[4].strip()
                    if retry_interval[len(retry_interval) - 1] == "s":
                        retry_interval = int(retry_interval[0: len(retry_interval) - 1])
                    elif retry_interval[len(retry_interval) - 1] == "m":
                        retry_interval = int(retry_interval[0: len(retry_interval) - 1]) * 60
                    elif retry_interval[len(retry_interval) - 1] == "h":
                        retry_interval = int(retry_interval[0: len(retry_interval) - 1]) * 60 * 60
                    else:
                        retry_interval = int(retry_interval)
                    cmd_retry = {"COUNT": retry_count, "INTERVAL": retry_interval}
                result_list.append(i)
        # 根据执行结果生成对应的xlog内容
        xlog_result = self.__split_scenario_block_result(result_list)
        return result_list, xlog_result

    def __split_scenario_block_result(self, content_list):
        splited_scenario_dict = {}
        scenario_begin_match_str = self.match_list.scenario_begin_match
        setup_begin_match_str = self.match_list.setup_begin_match
        cleanup_begin_match_str = self.match_list.cleanup_begin_match
        end_match_str = self.match_list.end_match
        label_list = []
        begin_count = 0
        end_count = 0
        # 将setup,cleanup,scenario都当成一个scenario  block进行拆分
        for i in range(len(content_list)):
            line = content_list[i].strip()
            scenario_line = re.search(scenario_begin_match_str, line, re.I | re.M)
            setup_line = re.search(setup_begin_match_str, line, re.I | re.M)
            cleanup_line = re.search(cleanup_begin_match_str, line, re.I | re.M)
            contain_line = None
            if setup_line:
                contain_line = setup_line
            elif scenario_line:
                contain_line = scenario_line
            elif cleanup_line:
                contain_line = cleanup_line
            if contain_line:
                if re.search(end_match_str, line[contain_line.span()[1]: len(line) + 1].strip(), re.I | re.M):
                    label_list.append(2)
                    begin_count += 1
                else:
                    label_list.append(1)
                    end_count += 1
            else:
                label_list.append(0)
        scenario_block_index_range = []
        # 判断scenario block label是否一一对应，不对应则直接报错
        if begin_count == end_count:
            tmp_begin_list = []
            for i in range(len(label_list)):
                if label_list[i] == 1:
                    tmp_begin_list.append(i)
                if label_list[i] == 2:
                    if len(tmp_begin_list) == 1:
                        scenario_block_index_range.append([tmp_begin_list[0], i])
                        tmp_begin_list = []
            # 判断scenario是否有嵌套，有嵌套则直接报错
            if len(scenario_block_index_range) == begin_count:
                # 将每个scenario block拆分为xlog对应的格式
                for i in scenario_block_index_range:
                    scenario_name = ""
                    scenario_id = ""
                    scneario_status = ""
                    message = ""
                    scenario_title = content_list[i[0]].strip()[0: len(content_list[i[0]].strip()) - 1].replace("--",
                                                                                                                "",
                                                                                                                1).replace(
                        "[", "", 1).split(",")
                    for sc_i in scenario_title:
                        tmpline = sc_i.split(":")
                        if tmpline[0].strip().lower() == "scenario":
                            scenario_name = tmpline[1].strip()
                        elif tmpline[0].strip().lower() == "id":
                            scenario_id = tmpline[1].strip()
                        elif tmpline[0].strip().lower() == "setup":
                            scenario_name = "setup"
                        elif tmpline[0].strip().lower() == "cleanup":
                            scenario_name = "cleanup"
                    # 判断一个scenario block是否包含错误的结果，没有则测试通过，主要针对一个scenario block可能包含n个assert的情况
                    if "".join(content_list[i[0]: i[1]]).find("TEST RESULT: TEST FAILURE") != -1:
                        scneario_status = "FAILURE"
                        # message = "".join(
                        #     [i for i in content_list[i[0] + 1: i[1]] if i.find("[ASSERT RESULT ERROR] ") != -1])
                        message = "".join(content_list[i[0] + 1: i[1]])
                    else:
                        scneario_status = "Successful"
                    single_scenario = {"Id": scenario_id}
                    single_scenario.update({"Status": scneario_status})
                    single_scenario.update({"message": message})
                    splited_scenario_dict.update({scenario_name: single_scenario})
            else:
                splited_scenario_dict.update({"SCENARIO ERROR": r"Scenario does not support nesting"})
                raise HTTPException("[SCENARIO ERROR]: Scenario does not support nesting")
        else:
            splited_scenario_dict.update(
                {"SCENARIO ERROR": r"\"--[scenario:]\" and \"--[scenario:end]\" must correspond"})
            raise HTTPException(r"[SCENARIO ERROR]: \"--[scenario:]\" and \"--[scenario:end]\" must correspond")
        return splited_scenario_dict


if __name__ == "__main__":
    os.environ["Label_ID"] = r"192.168.10.80"
    path = sys.argv[1]
    api_executor = APIExecutor(path)
    api_block_list = api_executor.execute_log
    api_xlog = api_executor.execute_xlog
    for i in api_block_list:
        print(i, end="")
    print("--"*20)
    print(json.dumps(api_xlog, indent=4, ensure_ascii=False))
