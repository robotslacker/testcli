import os
import re
import sys

from .httpexception import HTTPException
from .apiutil import getFileInfo, var_parse, RegularExpression, case_keyword_list, case_keyword_list1
from .csvfileparser import CSVParser


class APIParser:
    def __init__(self, api_file_path):
        self.api_path = api_file_path
        self.source_content = var_parse(getFileInfo(self.api_path))
        # self.parse_result = self.__flat_json_from_content()
        self.parse_result = self.__flat_assert_from_content()

    def __parse_iterator(self, part_content):
        # 对iterator title进行拆分，其中可能包含headeer，分隔符，必然包含csv文件路径
        iterator_info_list = []
        csv_file_info = str(part_content[0]).strip()[11: len(part_content[0].strip())].strip().split(",")
        csv_info_dict = {}
        for i in csv_file_info:
            line = i.split(":")
            csv_info_dict.update({line[0].strip().lower(): line[1].strip()})
        os.chdir(os.path.dirname(self.api_path))
        csv_path = csv_info_dict.get("csv_path").replace("\\", os.path.sep).replace("/", os.path.sep)
        header = csv_info_dict.get("header")
        if header.lower() == "true":
            header = True
        elif header.lower() == "false":
            header = False
        else:
            # 如果header为奇怪的值，则直接报错，header默认为FALSE
            iterator_info_list = [
                {"ITERATOR HEADER ERROR": "Invalid header, which must be True or False: %s" % part_content[0].strip()}]
            raise HTTPException("[ITERATOR HEADER ERROR]: Invalid header, which must be True or False: %s" % part_content[0].strip())
            return iterator_info_list
        # sep默认为逗号
        sep = csv_info_dict.get("sep")
        csv_content = CSVParser(csv_path, header=header, sep=sep).csv_content
        if len(csv_content) == 1:
            if csv_content[0].get("CSV CONTENT ERROR") is not None or \
                    csv_content[0].get("CSV COLUMN ERROR") is not None or \
                    csv_content[0].get("CSV PATH ERROR") is not None:
                iterator_info_list = csv_content
                return iterator_info_list
        csv_rows = 0
        for i in csv_content:
            for j in i:
                csv_rows = len(i[j])
                break
            break
        # 根据csv文件数据量进行相应的n次迭代
        iterator_content = part_content[1: len(part_content) - 1]
        iterator_content_str = "".join(iterator_content)
        csv_content_dict = {}
        for i in csv_content:
            csv_content_dict.update(i)
        for i in range(csv_rows):
            tmp_content = iterator_content_str
            for j in csv_content_dict:
                tmp_content = tmp_content.replace("{{%s}}" % j, str(csv_content_dict[j][i]))
            iterator_info_list.append(tmp_content)
        return iterator_info_list

    def __get_iterator_index(self):
        execution_order_list = []
        match_str = RegularExpression().iterator_match
        label_list = []
        begin_count = 0
        end_count = 0
        for i in range(len(self.source_content)):
            line = self.source_content[i].strip()
            contain_line = re.search(match_str, line, re.I | re.M)
            if contain_line:
                if line[contain_line.span()[1] + 1: len(line)].lower().strip() == "end":
                    label_list.append(2)
                    end_count += 1
                else:
                    label_list.append(1)
                    begin_count += 1
            else:
                label_list.append(0)
        # 每个iterator的起始与结束标签需一一对应，否则直接报错
        if begin_count == end_count:
            tmp_begin_list = []
            for i in range(len(label_list)):
                if label_list[i] == 1:
                    tmp_begin_list.append(i)
                if label_list[i] == 2:
                    if len(tmp_begin_list) == 1:
                        execution_order_list.append([tmp_begin_list[0], i])
                        tmp_begin_list = []
                    else:
                        execution_order_list.append([tmp_begin_list[len(tmp_begin_list) - 1], i])
                        tmp_begin_list.pop(len(tmp_begin_list) - 1)
        else:
            execution_order_list.append({"ITERATOR ERROR": "--ITERATOR: and --ITERATOR: END must correspond"})
            raise HTTPException(
                "[ITERATOR ERROR]: --ITERATOR: and --ITERATOR: END must correspond")
        return execution_order_list

    def __remove_iterator_from_content(self):
        split_list = []
        iterator_index_list = self.__get_iterator_index()
        content_index_list = []
        all_iter_ind_list = iterator_index_list.copy()
        for i in range(len(iterator_index_list)):
            for j in range(len(iterator_index_list)):
                if iterator_index_list[i][0] > iterator_index_list[j][0]:
                    all_iter_ind_list[i] = None
                    break
        all_iter_ind_list = [i for i in all_iter_ind_list if i is not None]
        # print(all_iter_ind_list)
        if len(all_iter_ind_list) != 0:
            for i in range(1, len(all_iter_ind_list)):
                content_index_list.append({"iterator": [all_iter_ind_list[i - 1]]})
                content_index_list.append({"content": [all_iter_ind_list[i - 1][1] + 1, all_iter_ind_list[i][0] - 1]})
            content_index_list.append({"iterator": [all_iter_ind_list[len(all_iter_ind_list) - 1]]})
            if all_iter_ind_list[0][0] - 1 > 0:
                content_index_list.insert(0, {"content": [0, all_iter_ind_list[0][0] - 1]})
            if len(self.source_content) - 1 > all_iter_ind_list[len(all_iter_ind_list) - 1][1] + 1:
                content_index_list.append(
                    {"content": [all_iter_ind_list[len(all_iter_ind_list) - 1][1] + 1, len(self.source_content) - 1]})
            for i in iterator_index_list:
                for j in range(len(content_index_list)):
                    line = content_index_list[j].get("iterator")
                    if line is not None:
                        for k in range(len(line)):
                            if i[0] > line[k][0] and i[1] < line[k][1]:
                                line.insert(k, i)
                                content_index_list[j] = {"iterator": line}
                                break
                    else:
                        pass
            for i in content_index_list:
                c_list = i.get("content")
                i_list = i.get("iterator")
                if c_list is not None:
                    split_list.append(self.source_content[c_list[0]: c_list[1] + 1])
                if i_list is not None:
                    tmp_i = i_list[len(i_list) - 1]
                    split_list.append(self.source_content[tmp_i[0]: tmp_i[1] + 1])
            # print(content_index_list)
            for i in range(len(content_index_list)):
                tmp_line = content_index_list[i].get("iterator")
                if tmp_line is not None:
                    if len(tmp_line) == 1:
                        split_list[i] = self.__parse_iterator(split_list[i])
                    else:
                        last_one = tmp_line[len(tmp_line)-1]
                        max_content = self.source_content[last_one[0]: last_one[1]]
                        # print(max_content)
                        # print("=="*20)
                        for j in range(len(tmp_line)):
                            s_content = self.source_content[tmp_line[j][0]: tmp_line[j][1]+1]
                            t_content = self.__parse_iterator(s_content)
                            if isinstance(max_content, list):
                                max_content = "".join(max_content).replace("".join(s_content), "".join(t_content))
                            else:
                                max_content = max_content.replace("".join(s_content), "".join(t_content))
                        # print(self.__parse_iterator([a + "\n" for a in max_content.split("\n")])[0])
                        # print("--"*20)
                        split_list[i] = self.__parse_iterator([a + "\n" for a in max_content.split("\n")])
        else:
            split_list.append(self.source_content)
        final_content_list = []
        for i in split_list:
            for j in i:
                if isinstance(j, dict):
                    for k in j:
                        final_content_list.append("[%s] %s\n" % (k, j[k]))
                else:
                    tmp_line = j.strip()
                    tmp_split = tmp_line.split("\n")
                    if len(tmp_split) > 1:
                        final_content_list += [l + "\n" for l in tmp_split]
                    else:
                        final_content_list.append(j if j[len(j) - 1: len(j)] == "\n" else j + "\n")
        # for i in final_content_list:
        #     print(i, end="")
        return final_content_list

    def __flat_json_from_content(self):
        real_content_list = self.__remove_iterator_from_content()
        call_match_str = RegularExpression().http_file_match
        call_index_list = []
        split_content_list = []
        for i in range(len(real_content_list)):
            if re.search(call_match_str, real_content_list[i].strip(), re.I | re.M):
                call_index_list.append(i)
        call_index_list.append(len(real_content_list))
        split_content_list += real_content_list[0: call_index_list[0]]
        for i in range(1, len(call_index_list)):
            tmp_content = real_content_list[call_index_list[i - 1]: call_index_list[i]]
            end_index = None
            for j in range(len(tmp_content)):
                for k in case_keyword_list():
                    if re.search(k, tmp_content[j], re.I | re.M):
                        end_index = j
                        break
                if end_index is not None:
                    break
            if end_index:
                split_content_list.append(" ".join(
                    [l.strip() for l in tmp_content[0: end_index] if
                     re.search(r"^--.*", l, re.I | re.M) is None]) + "\n")
            split_content_list += tmp_content[end_index: len(tmp_content) + 1]
        return split_content_list

    def __flat_assert_from_content(self):
        flat_json_content = self.__flat_json_from_content()
        assert_match_str = RegularExpression().assert_match
        assert_index_list = []
        split_content_list = []
        for i in range(len(flat_json_content)):
            if re.search(assert_match_str, flat_json_content[i].strip(), re.I | re.M):
                assert_index_list.append(i)
        assert_index_list.append(len(flat_json_content))
        split_content_list += flat_json_content[0: assert_index_list[0]]
        for i in range(1, len(assert_index_list)):
            tmp_content = flat_json_content[assert_index_list[i - 1]: assert_index_list[i]]
            end_index = None
            for j in range(1, len(tmp_content)):
                end_index = None
                for k in case_keyword_list1():
                    if re.search(k, tmp_content[j], re.I | re.M):
                        end_index = j
                        break
                if end_index is not None:
                    break
            if end_index:
                split_content_list.append(" ".join(
                    [l.strip() for l in tmp_content[0: end_index] if
                     re.search(r"^--.*", l, re.I | re.M) is None]) + "\n")
            split_content_list += tmp_content[end_index: len(tmp_content) + 1]
        return split_content_list


if __name__ == "__main__":
    path = sys.argv[1]
    api_parser = APIParser(path)
    api_block_list = api_parser.parse_result
    for i in api_block_list:
        print(i, end="")