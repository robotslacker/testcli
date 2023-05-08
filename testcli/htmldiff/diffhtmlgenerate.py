# -*- coding: utf-8 -*-
import os
import datetime
from difflib import SequenceMatcher
from .renderer import render


class diffHtmlGenerate(object):
    @staticmethod
    def parseHeaderLine(line):
        """
            功能：分解说明区每一行的标志和内容
            参数：
                line:说明区行内容
            返回：
                返回说明区每行的标志和内容
        """
        data = dict()
        flag = line[0]
        source = line[1:]

        data["flag"] = flag
        data["source"] = source

        return data

    @staticmethod
    def parseBodyLine(line):
        """
            功能：分解正文区每一行的标志和内容
            参数：
                line:正文区行内容
            返回：
                返回正文区每行的标志、行号和内容
        """
        data = dict()

        flag = line[0]
        source = line[1:].lstrip()
        parsedList = source.partition(" ")

        data["flag"] = flag
        data["number"] = parsedList[0]
        data["source"] = parsedList[2].strip()

        return data

    @staticmethod
    def generateLineDiff(body):
        """
            功能：比较-+行的差异，并把差异文字并插入Html的P标签
                 利用SequenceMatcher进行分析
            参数：
                body: 正文区行信息
            返回：
                无
        """
        lines = dict()
        for line in body:
            if line["flag"] == '-' or line["flag"] == '+':
                number = line["number"]
                if number in lines.keys():
                    data = lines[number]
                    data.append(line)
                else:
                    # 新行
                    lines[number] = [line]

        for number in lines.keys():
            data = lines[number]
            source = None
            target = None
            # FIXME 只比较一行
            for item in data:
                if item["flag"] == "-":
                    source = item
                if item["flag"] == "+":
                    target = item

            if source is not None and target is not None:
                a = source["source"]
                b = target["source"]
                s = SequenceMatcher(None, a, b)
                na = ""
                nb = ""
                for tag, i1, i2, j1, j2 in s.get_opcodes():
                    if tag == "replace":
                        # 不一样
                        na = na + "<p class='diff'>" + a[i1:i2] + "</p>"
                        nb = nb + "<p class='diff'>" + b[j1:j2] + "</p>"
                    elif tag == "delete":
                        # 删除
                        na = na + "<p class='diff'>" + a[i1:i2] + "</p>"
                        nb = nb + "<p class='diff'>" + b[j1:j2] + "</p>"
                    elif tag == "insert":
                        # 新增
                        na = na + "<p class='diff'>" + a[i1:i2] + "</p>"
                        nb = nb + "<p class='diff'>" + b[j1:j2] + "</p>"
                    elif tag == "equal":
                        na = na + a[i1:i2]
                        nb = nb + b[j1:j2]
                source["source"] = na
                target["source"] = nb
        return

    def generateHtmlFromDif(self, workFile: str, refFile: str, diffLines: list):

        """
            功能：根据diff的内容生成html格式的报告
            参数：
                diffLines diff的内容
            返回：
                生成的Html文件内容
        """
        header = []
        body = []

        for line in diffLines:
            if line[0] == 'M':
                header.append(self.parseHeaderLine(line))
            else:
                body.append(self.parseBodyLine(line))

        # 分析-+对应行的差异
        self.generateLineDiff(body)

        # 生成Html文件
        html = self.generateHtml(workFile, refFile, header, body)

        return html

    @staticmethod
    def generateHtml(workFile: str, refFile: str, header: list, body: list):
        """
            功能: 根据模板生成Html文件
            参数：
                header: 说明区行信息
                body: 正文区行信息
            返回：
                Html文件名称
        """
        # 默认的Html文件名称
        htmlResult = []

        # 说明区生成模板
        with open(
                file=os.path.join(os.path.dirname(__file__), "template", "header.html"),
                mode='r',
                encoding='utf-8') as template:
            data = dict()
            fragment = render(template, data)
            htmlResult.append(fragment)

        # 正文区头部内容生成模板
        # 正文区在Html模板中生成JSON内容，Html内的Javascript根据模式要求生成视图
        with open(
                file=os.path.join(os.path.dirname(__file__), "template", "body.header.html"),
                mode='r',
                encoding='utf-8') as template:
            data = {}
            data.update({'lines': header})
            fragment = render(template, data)
            htmlResult.append(fragment)

        # 正文区内容部分生成模板
        # 包含主要的JS
        with open(
                file=os.path.join(os.path.dirname(__file__), "template", "body.content.html"),
                mode='r',
                encoding='utf-8') as template:
            data = {}
            data.update({'lines': body})
            data.update({'workFile': workFile})
            data.update({'refFile': refFile})
            fragment = render(template, data)
            htmlResult.append(fragment)

        # 页尾模板
        # 包含 上一个、下一个按钮
        with open(
                file=os.path.join(os.path.dirname(__file__), "template", "footer.html"),
                mode='r',
                encoding='utf-8') as template:
            data = {'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            fragment = render(template, data)
            htmlResult.append(fragment)

        return htmlResult
