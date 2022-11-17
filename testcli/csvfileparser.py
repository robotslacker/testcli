import os

import pandas as pd
from pandas.errors import EmptyDataError

from .httpexception import HTTPException


class CSVParser:
    def __init__(self, csv_file_path, header=False, sep=","):
        self.csv_path = csv_file_path
        self.csv_header = header
        self.csv_sep = sep
        self.csv_content = self.__get_csv_content()

    def __get_csv_content(self):
        result_list = []
        if os.path.exists(self.csv_path):
            header = 0 if self.csv_header is True else None
            try:
                content = pd.read_csv(self.csv_path, sep=self.csv_sep, header=header, encoding="utf-8", dtype='str')
            except EmptyDataError:
                # 针对csv文件内容为空，直接报错
                result_list = [{"CSV CONTENT ERROR": "There is nothing to read: %s" % self.csv_path.strip()}]
                raise HTTPException(r"[CSV CONTENT ERROR]: There is nothing to read: %s" % self.csv_path.strip())
                return result_list
            if header is not None:
                for i in content:
                    result_list.append({i: list(content[i])})
            else:
                for i in content:
                    result_list.append({"C%s" % str(int(i) + 1): list(content[i])})
            tmp_count = 0
            for i in result_list:
                for j in i:
                    if len(i[j]) == 0:
                        tmp_count += 1
            if tmp_count == len(result_list):
                # 针对csv文件内容为空，直接报错
                result_list = [{"CSV CONTENT ERROR": "There is nothing to read: %s" % self.csv_path.strip()}]
                raise HTTPException(r"[CSV CONTENT ERROR]: There is nothing to read: %s" % self.csv_path.strip())
            else:
                # 当header存在时
                if header == 0:
                    tmp_id_list = []
                    tmp_name_list = []
                    not_scenario_count = 0
                    # 判断csv恩建第一列是否为scenario，如果是，则将scenario列拆分为scenario name和scenario id，没有则报错
                    for i in result_list[0]:
                        if i.strip().lower() == "scenario":
                            for j in result_list[0][i]:
                                line = j.strip().split(":")
                                if len(line) == 2:
                                    tmp_id_list.append(line[0])
                                    tmp_name_list.append(line[1])
                                else:
                                    tmp_id_list = None
                                    tmp_name_list = None
                                    break
                        else:
                            not_scenario_count += 1
                    if not_scenario_count == len(result_list[0]):
                        pass
                    else:
                        if tmp_id_list is None or tmp_name_list is None:
                            result_list = [{"CSV COLUMN ERROR": "Scenario_name or scenario_id not find"}]
                            raise HTTPException(r"[CSV COLUMN ERROR]: Scenario_name or scenario_id not find")
                        else:
                            result_list.pop(0)
                            result_list.insert(0, {"scenario_id": tmp_id_list})
                            result_list.insert(1, {"scenario_name": tmp_name_list})
                # 当header不存在时
                else:
                    # header不存在，这每列的别名从C1开始一直到Cn，cases调用则是{{C1}}
                    # 判断C1列是否为scenario id: scenario name格式，原理同上
                    scenario_col = result_list[0].get("C1")
                    not_scenario_count = 0
                    for i in scenario_col:
                        if i.find(":") == -1:
                            not_scenario_count += 1
                    if not_scenario_count == len(scenario_col):
                        pass
                    else:
                        tmp_id_list = []
                        tmp_name_list = []
                        for i in scenario_col:
                            line = i.strip().split(":")
                            if len(line) == 2:
                                tmp_id_list.append(line[0])
                                tmp_name_list.append(line[1])
                            else:
                                tmp_id_list = None
                                tmp_name_list = None
                                break
                        if tmp_id_list is None or tmp_name_list is None:
                            result_list = [{"CSV COLUMN ERROR": "Scenario_name or scenario_id not find"}]
                            raise HTTPException(r"[CSV COLUMN ERROR]: Scenario_name or scenario_id not find")
                        else:
                            result_list.pop(0)
                            result_list.insert(0, {"scenario_id": tmp_id_list})
                            result_list.insert(1, {"scenario_name": tmp_name_list})
        else:
            result_list.append({"CSV PATH ERROR": "The path does not exist: %s" % self.csv_path.strip()})
            raise HTTPException(r"[CSV PATH ERROR]: The path does not exist: %s" % self.csv_path.strip())
        return result_list


if __name__ == "__main__":
    path = r"G:\workspace\apitest\test\api_demo\csv\test_data.csv"
    csv_content = CSVParser(path, header=True, sep="|").csv_content
    for i in csv_content:
        print(i)