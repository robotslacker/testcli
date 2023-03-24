# -*- coding: utf-8 -*-
import os
import re
import time
import datetime
import random
import traceback
from ..testcliexception import TestCliException

# 定义种子文件的存放目录
seedFileDir = ""
# 定义种子文件的缓存
seedDataCache = {}


# 返回随机的Boolean类型
def random_boolean(p_arg):
    if p_arg:
        pass  # 这里用来避免p_arg参数无用的编译器警告
    return "1" if (random.randint(0, 1) == 1) else "0"


# 返回一个随机的时间
# 有3个参数：
#   stime   开始时间
#   etime   结束时间
#   frmt    日期格式，可以忽略，默认为"%Y-%m-%d"
def random_date(p_arg):
    if len(p_arg) > 2:
        frmt = str(p_arg[2])
    else:
        frmt = "%Y-%m-%d"
    try:
        stime = datetime.datetime.strptime(str(p_arg[0]), frmt)
        etime = datetime.datetime.strptime(str(p_arg[1]), frmt)
    except ValueError:
        raise TestCliException("Invalid date format [" + str(frmt) + "] for [" + str(p_arg[0]) + "]")
    return (random.random() * (etime - stime) + stime).strftime(frmt)


# 返回一个随机的时间戳
# 有3个参数：
#   stime   开始时间
#   etime   结束时间
#   frmt    日期格式，可以忽略，默认为%H:%M:%S
def random_time(p_arg):
    if len(p_arg) > 2:
        frmt = "%Y-%m-%d " + str(p_arg[2])
    else:
        frmt = "%Y-%m-%d %H:%M:%S"
    try:
        stime = datetime.datetime.strptime("2000-01-01 " + str(p_arg[0]), frmt)
        etime = datetime.datetime.strptime("2000-01-01 " + str(p_arg[1]), frmt)
    except ValueError:
        raise TestCliException("Invalid timestamp format [" + str(frmt) + "] for [" + str(p_arg[0]) + "]")
    return (random.random() * (etime - stime) + stime).strftime(frmt)[11:]


# 返回一个随机的时间戳
# 有3个参数：
#   stime   开始时间
#   etime   结束时间
#   frmt    日期格式，可以忽略，默认为%Y-%m-%d %H:%M:%S
def random_timestamp(p_arg):
    if len(p_arg) > 2:
        frmt = str(p_arg[2])
    else:
        frmt = "%Y-%m-%d %H:%M:%S"
    try:
        stime = datetime.datetime.strptime(str(p_arg[0]), frmt)
        etime = datetime.datetime.strptime(str(p_arg[1]), frmt)
    except ValueError:
        raise TestCliException("Invalid timestamp format [" + str(frmt) + "] for [" + str(p_arg[0]) + "]")
    return (random.random() * (etime - stime) + stime).strftime(frmt)


# 返回系统当前时间,Unix时间戳方式
def current_unixtimestamp(p_arg):
    if p_arg:
        pass
    return str(int(time.mktime(datetime.datetime.now().timetuple())))


# 返回系统当前时间
def current_timestamp(p_arg):
    if len(p_arg) == 1:
        frmt = str(p_arg[0]).strip()
        if len(frmt) == 0:
            frmt = "%Y-%m-%d %H:%M:%S"
    else:
        frmt = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.now().strftime(frmt)


def random_digits(p_arg):
    n = int(p_arg[0])
    seed = '0123456789'.encode()
    len_lc = len(seed)
    ba = bytearray(os.urandom(n))
    for i, b in enumerate(ba):
        ba[i] = seed[b % len_lc]
    return ba.decode('ascii')


def random_ascii_uppercase(p_arg):
    n = int(p_arg[0])
    seed = 'ABCDEFGHIJKLMNOPRRSTUVWXYZ'.encode()
    len_lc = len(seed)
    ba = bytearray(os.urandom(n))
    for i, b in enumerate(ba):
        ba[i] = seed[b % len_lc]
    return ba.decode('ascii')


def random_ascii_lowercase(p_arg):
    n = int(p_arg[0])
    seed = 'abcdefghijklmnopqrstuvwxyz'.encode()
    len_lc = len(seed)
    ba = bytearray(os.urandom(n))
    for i, b in enumerate(ba):
        ba[i] = seed[b % len_lc]
    return ba.decode('ascii')


def random_ascii_letters(p_arg):
    n = int(p_arg[0])
    seed = 'ABCDEFGHIJKLMNOPRRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.encode()
    len_lc = len(seed)
    ba = bytearray(os.urandom(n))
    for i, b in enumerate(ba):
        ba[i] = seed[b % len_lc]
    return ba.decode('ascii')


def random_ascii_letters_and_digits(p_arg):
    n = int(p_arg[0])
    seed = 'ABCDEFGHIJKLMNOPRRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'.encode()
    len_lc = len(seed)
    ba = bytearray(os.urandom(n))
    for i, b in enumerate(ba):
        ba[i] = seed[b % len_lc]
    return ba.decode('ascii')


# 返回一个自增长序列
# 有2个参数：
#   identity_name   自增序列号的名字
#   start           即自正常序列的开始值
#   步长目前没有支持，都是1
def identity(p_arg):
    identity_name = str(p_arg[0])
    start = int(p_arg[1])
    if not hasattr(identity, 'x'):
        identity.x = {}
    if identity_name not in identity.x.keys():
        identity.x[identity_name] = start
    else:
        identity.x[identity_name] = identity.x[identity_name] + 1
    return str(identity.x[identity_name])


# 返回一个自增长的时间戳
# 有4个参数：
#   identity_name   自增序列号的名字
#   stime   开始时间
#     若stime写作current_timestamp, 则自增上从当前时间开始
#   frmt    日期格式， 如%Y-%m-%d %H:%M:%S
#   step    步长，可以用ms,us,s来表示，默认情况下是ms
def identity_timestamp(p_arg):
    identity_name = str(p_arg[0])
    ptime = str(p_arg[1])
    frmt = str(p_arg[2])
    step = str(p_arg[3])
    if not hasattr(identity_timestamp, 'x'):
        identity_timestamp.x = {}
    if identity_name not in identity_timestamp.x.keys():
        if ptime == "current_timestamp":
            identity_timestamp.x[identity_name] = datetime.datetime.now()
        else:
            identity_timestamp.x[identity_name] = datetime.datetime.strptime(ptime, frmt)
    else:
        # 判断步长单位，默认是毫秒，可以是s,ms
        if step.endswith("s"):
            if step.endswith("ms"):
                # end with ms 毫秒
                identity_timestamp.x[identity_name] = (identity_timestamp.x[identity_name] +
                                                       datetime.timedelta(milliseconds=float(step[:-2])))
            elif step.endswith("us"):
                # end with us 微妙
                identity_timestamp.x[identity_name] = (identity_timestamp.x[identity_name] +
                                                       datetime.timedelta(microseconds=float(step[:-2])))
            else:
                # end with s 秒
                identity_timestamp.x[identity_name] = (identity_timestamp.x[identity_name] +
                                                       datetime.timedelta(seconds=float(step[:-1])))
        else:
            identity_timestamp.x[identity_name] = (identity_timestamp.x[identity_name] +
                                                   datetime.timedelta(milliseconds=float(step)))
    return identity_timestamp.x[identity_name].strftime(frmt)


# 缓存seed文件
def load_seed_ache():
    global seedFileDir
    global seedDataCache

    if seedFileDir == "":
        raise TestCliException("To generate random data from seed, Please make sure set seed data dir correct.")
    files = os.listdir(seedFileDir)
    for file in files:
        if not file.endswith(".seed"):
            continue
        seed_name = os.path.basename(file)[:-5]  # 去掉.seed的后缀
        with open(os.path.join(seedFileDir, file), mode='r', encoding="utf-8") as f:
            seed_lines = f.readlines()
        for pos in range(0, len(seed_lines)):
            if seed_lines[pos].endswith("\n"):
                seed_lines[pos] = seed_lines[pos][:-1]  # 去掉回车换行
        seedDataCache[seed_name] = seed_lines


def random_from_seed(p_arg):
    global seedDataCache

    seed_name = str(p_arg[0])
    if len(p_arg) == 3:
        # 从指定位置开始截取数据内容
        start_pos = int(p_arg[1])
        max_length = int(p_arg[2])
    elif len(p_arg) == 2:
        # 从头开始截取文件内容
        start_pos = 0
        max_length = int(p_arg[1])
    else:
        start_pos = 0
        max_length = -1

    # 如果还没有加载种子，就先尝试加载
    if seed_name not in seedDataCache:
        load_seed_ache()

    # 在种子中查找需要的内容
    if seed_name in seedDataCache:
        n = len(seedDataCache[seed_name])
        if n == 0:
            # 空的Seed文件，可能是由于Seed文件刚刚创建，则尝试重新加载数据
            load_seed_ache()
            n = len(seedDataCache[seed_name])
            if n == 0:
                raise TestCliException("Seed cache is zero. [" + str(p_arg[0]) + "].")
        random_lines = seedDataCache[seed_name][random.randint(0, n - 1)]
        if max_length == -1:
            return random_lines[start_pos:]
        else:
            return random_lines[start_pos:start_pos + max_length]
    else:
        raise TestCliException("Unknown seed [" + str(p_arg[0]) + "].  Please create it first.")


# 将传递的SQL字符串转换成一个带有函数指针的数组
def parse_formula_str(p_formula_str):
    # 首先按照{}来把所有的函数定义分拆到数组中
    m_row_struct = re.split('[{}]', p_formula_str)
    m_return_row_struct = []

    # 在分拆的数组中依次查找关键字，作为后续函数替换的需要
    for m_nRowPos in range(0, len(m_row_struct)):
        if re.search('random_ascii_lowercase|random_ascii_uppercase|random_ascii_letters' +
                     '|random_digits|identity|identity_timestamp|random_ascii_letters_and_digits|random_from_seed' +
                     '|random_date|random_timestamp|random_time|random_boolean|'
                     'current_timestamp|current_unixtimestamp|value',
                     m_row_struct[m_nRowPos], re.IGNORECASE):
            m_function_struct = re.split(r'[(,)]', m_row_struct[m_nRowPos])
            for pos in range(0, len(m_function_struct)):
                m_function_struct[pos] = m_function_struct[pos].strip()
                if m_function_struct[pos].startswith("'"):
                    m_function_struct[pos] = m_function_struct[pos][1:]
                if m_function_struct[pos].endswith("'"):
                    m_function_struct[pos] = m_function_struct[pos][0:-1]
            if len(m_function_struct[-1]) == 0:
                m_function_struct.pop()
            m_call_out_struct = []
            if m_function_struct[0].upper() == "RANDOM_ASCII_LOWERCASE":
                m_call_out_struct.append(random_ascii_lowercase)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_ASCII_LOWERCASE", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_ASCII_LOWERCASE", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_ascii_lowercase)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_ASCII_UPPERCASE":
                m_call_out_struct.append(random_ascii_uppercase)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_ASCII_UPPERCASE", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_ASCII_UPPERCASE", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_ascii_uppercase)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_ASCII_LETTERS":
                m_call_out_struct.append(random_ascii_letters)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_ASCII_LETTERS", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_ASCII_LETTERS", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_ascii_letters)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_DIGITS":
                m_call_out_struct.append(random_digits)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_DIGITS", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_DIGITS", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_digits)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "IDENTITY_TIMESTAMP":
                m_call_out_struct.append(identity_timestamp)
                # 如果没有列名，第一个参数信息是identity#加上列号的信息
                if len(m_function_struct) == 5:
                    m_function_struct = m_function_struct[1:]
                elif len(m_function_struct) == 4:
                    m_function_struct[0] = "identity#" + str(m_nRowPos)
                else:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure IDENTITY_TIMESTAMP has correct parameters.")
                m_call_out_struct.append(m_function_struct)
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):IDENTITY_TIMESTAMP", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):IDENTITY_TIMESTAMP", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(identity_timestamp)
                # 如果有列名，第一个参数信息是identity#加上列名的信息
                m_function_struct[0] = "identity#" + column_name
                m_call_out_struct.append(m_function_struct)
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "IDENTITY":
                m_call_out_struct.append(identity)
                # 如果没有列名，第一个参数信息是identity#加上列号的信息
                m_function_struct[0] = "identity#" + str(m_nRowPos)
                m_call_out_struct.append(m_function_struct)
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):IDENTITY", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):IDENTITY", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(identity)
                # 如果有列名，第一个参数信息是identity#加上列名的信息
                m_function_struct[0] = "identity#" + column_name
                m_call_out_struct.append(m_function_struct)
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_ASCII_LETTERS_AND_DIGITS":
                m_call_out_struct.append(random_ascii_letters_and_digits)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_ASCII_LETTERS_AND_DIGITS", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_ASCII_LETTERS_AND_DIGITS", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_ascii_letters_and_digits)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_FROM_SEED":
                m_call_out_struct.append(random_from_seed)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_FROM_SEED", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_FROM_SEED", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_from_seed)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_DATE":
                m_call_out_struct.append(random_date)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_DATE", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_DATE", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_date)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_TIMESTAMP":
                m_call_out_struct.append(random_timestamp)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_TIMESTAMP", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_TIMESTAMP", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_timestamp)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_TIME":
                m_call_out_struct.append(random_time)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_TIME", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_TIME", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_time)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "RANDOM_BOOLEAN":
                m_call_out_struct.append(random_boolean)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):RANDOM_BOOLEAN", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):RANDOM_BOOLEAN", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(random_boolean)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "CURRENT_TIMESTAMP":
                m_call_out_struct.append(current_timestamp)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):CURRENT_TIMESTAMP", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):CURRENT_TIMESTAMP", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(current_timestamp)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "CURRENT_UNIXTIMESTAMP":
                m_call_out_struct.append(current_unixtimestamp)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append("__NO_NAME__")
            elif re.search(r"(.*):CURRENT_UNIXTIMESTAMP", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):CURRENT_UNIXTIMESTAMP", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                m_call_out_struct.append(current_unixtimestamp)
                m_call_out_struct.append(m_function_struct[1:])
                m_call_out_struct.append(column_name)
            elif m_function_struct[0].upper() == "VALUE":
                # 必须用：开头来表示字段名称
                if not m_function_struct[1:][0].startswith(":"):
                    raise TestCliException("Invalid pattern. Please use Value(:ColumnName).")
                else:
                    column_name = m_function_struct[1:][0][1:]
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name.upper():
                            found = True
                            break
                if not found:
                    m_ValidColumn = ""
                    for row in m_return_row_struct:
                        if isinstance(row, list):
                            m_ValidColumn = m_ValidColumn + row[2] + "|"
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is valid.\n" +
                                           "Valid Column=[" + m_ValidColumn + "]")
                m_call_out_struct.append(None)
                m_call_out_struct.append(column_name)
                m_call_out_struct.append("VALUE")
            elif re.search(r"(.*):VALUE", m_function_struct[0].upper()):
                match_obj = re.search(r"(.*):VALUE", m_function_struct[0].upper())
                column_name = match_obj.group(1).upper().strip()
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name:
                            found = True
                            break
                if found:
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is not duplicate.")
                # 必须用：开头来表示字段名称
                if not m_function_struct[1:][0].startswith(":"):
                    raise TestCliException("Invalid pattern. Please use Value(:ColumnName).")
                else:
                    column_name = m_function_struct[1:][0][1:]
                # 检查列名是否已经定义
                found = False
                for row in m_return_row_struct:
                    if isinstance(row, list):
                        if row[2] == column_name.upper():
                            found = True
                            break
                if not found:
                    m_ValidColumn = ""
                    for row in m_return_row_struct:
                        if isinstance(row, list):
                            m_ValidColumn = m_ValidColumn + row[2] + "|"
                    raise TestCliException("Invalid pattern. "
                                           "Please make sure column [" + column_name + "] is valid.\n" +
                                           "Valid Column=[" + m_ValidColumn + "]")
                m_call_out_struct.append(None)
                m_call_out_struct.append(column_name)
                m_call_out_struct.append("VALUE")
            else:
                raise TestCliException("Invalid pattern. parse [" + m_row_struct[m_nRowPos] + "] failed. ")
            m_return_row_struct.append(m_call_out_struct)
        else:
            m_return_row_struct.append(m_row_struct[m_nRowPos])
    return m_return_row_struct


def get_final_string(p_row_struct):
    m_Result = ""
    m_Saved_ColumnData = {}
    for col in p_row_struct:
        if isinstance(col, list):
            if col[2] == "VALUE":
                column_name = col[1]
                m_Value = m_Saved_ColumnData[column_name.upper()]
                m_Result = m_Result + m_Value
            elif col[2] == "__NO_NAME__":
                m_Result = m_Result + col[0](col[1])
            else:
                m_Value = col[0](col[1])  # 根据函数指针计算返回后的实际内容
                m_Saved_ColumnData[col[2]] = m_Value
                m_Result = m_Result + m_Value
        else:
            m_Result = m_Result + col
    return m_Result


class FileHandler:
    def __init__(self):
        self.fp = None

    def open(self, fileName: str, mode: str, encoding: str):
        self.fp = open(file=fileName, mode=mode, encoding=encoding)

    def read(self, nByte: int):
        return self.fp.read(nByte)

    def write(self, content: bytes):
        self.fp.write(content)

    def writeLines(self, buf: list):
        self.fp.writelines(buf)

    def close(self):
        self.fp.close()


class MemHandler:
    def __init__(self):
        self.fp = None
        self.fs = None

    def open(self, fileName: str, mode: str, encoding: str):
        from ..globalvar import globalMemFsHandler
        self.fp = globalMemFsHandler.open(path=fileName, mode=mode, encoding=encoding)

    def read(self, nByte: int):
        return self.fp.read(nByte)

    def write(self, content: bytes):
        self.fp.write(content)

    def writeLines(self, buf: list):
        self.fp.writelines(buf)

    def close(self):
        self.fp.close()


fsImplemention = {
    "MEM": MemHandler,
    "FS": FileHandler
}


def createFile(p_filetype: str, p_filename, p_formula_str, p_rows, p_encoding='UTF-8'):
    try:
        if p_filetype.upper() not in fsImplemention.keys():
            raise TestCliException("Unknown target file type [" + str(p_filetype) + "]")
        fsHandler = fsImplemention[p_filetype.upper()]()
        fsHandler.open(fileName=p_filename, mode='w', encoding=p_encoding)

        m_row_struct = parse_formula_str(p_formula_str)
        buf = []
        for i in range(0, p_rows):
            buf.append(get_final_string(m_row_struct) + '\n')
            if len(buf) == 100000:  # 为了提高IO效率，每10W条写入文件一次
                fsHandler.writeLines(buf)
                buf = []
        if len(buf) != 0:
            fsHandler.writeLines(buf)
        fsHandler.close()

        # 重置identity的序列号，保证下次从开头开始
        if hasattr(identity, 'x'):
            delattr(identity, 'x')
        if hasattr(identity_timestamp, 'x'):
            delattr(identity_timestamp, 'x')
    except TestCliException as e:
        raise TestCliException(e.message)
    except Exception as e:
        if "TESTCLI_DEBUG" in os.environ:
            print('traceback.print_exc():\n%s' % traceback.print_exc())
            print('traceback.format_exc():\n%s' % traceback.format_exc())
        raise TestCliException(repr(e))


def convertFile(srcFileType: str, srcFileName: str, dstFileType: str, dstFileName: str):
    blockSize = 8192

    try:
        if srcFileType.upper() not in fsImplemention.keys():
            raise TestCliException("Unknown target file type [" + str(srcFileType) + "]")
        srcHandler = fsImplemention[srcFileType.upper()]()
        srcHandler.open(fileName=srcFileName, mode='rb', encoding=None)
        dstHandler = fsImplemention[dstFileType.upper()]()
        dstHandler.open(fileName=dstFileName, mode='wb', encoding=None)
        while True:
            readContents = srcHandler.read(blockSize)
            dstHandler.write(readContents)
            if len(readContents) <= blockSize:
                break
        srcHandler.close()
        dstHandler.close()
    except TestCliException as e:
        raise TestCliException(e.message)
    except Exception as e:
        if "TESTCLI_DEBUG" in os.environ:
            print('traceback.print_exc():\n%s' % traceback.print_exc())
            print('traceback.format_exc():\n%s' % traceback.format_exc())
        raise TestCliException(repr(e))


def executeDataRequest(cls, requestObject):
    global seedFileDir

    if requestObject["action"] == "set":
        if requestObject["option"] == "seedDir":
            # 设置种子文件的目录
            seedFileDir = requestObject["seedDir"]
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Data seed dir has been setted to [" + str(seedFileDir) + "]."
            }
            return
    if requestObject["action"] == "create":
        rowCount = requestObject["rowCount"]
        fileType = requestObject["fileType"]
        targetFile = requestObject["targetFile"]
        columnExpression = requestObject["columnExpression"]
        if rowCount > 1:
            # 如果需要的数据不是一行，则描述信息中的回车换行符号均无意义
            columnExpression = columnExpression.replace('\r', '').replace('\n', '')
        try:
            createFile(p_filetype=fileType,
                       p_filename=targetFile,
                       p_formula_str=columnExpression,
                       p_rows=rowCount,
                       p_encoding=cls.testOptions.get("RESULT_ENCODING")
                       )
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "File [" + str(targetFile) + "] created successful. " + str(rowCount) + " rows generated."
            }
        except TestCliException as te:
            yield {
                "type": "error",
                "message": te.message,
            }

    if requestObject["action"] == "convert":
        try:
            convertFile(
                srcFileType=requestObject["sourceFileType"],
                srcFileName=requestObject["sourceFile"],
                dstFileType=requestObject["targetFileType"],
                dstFileName=requestObject["targetFile"],
            )
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "File [" + str(requestObject["sourceFile"]) +
                          "] has been converted to [" + requestObject["targetFile"] + "] generated."
            }
        except TestCliException as te:
            yield {
                "type": "error",
                "message": te.message,
            }
