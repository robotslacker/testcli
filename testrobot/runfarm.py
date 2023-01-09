# -*- coding: utf-8 -*-
import os

if __name__ == "__main__":
    # 指定程序的工作目录， 该目录为一个可写的目录，程序开始运行后，该目录下所有内容将会被清空
    os.environ["T_WORK"] = os.path.join(os.path.dirname(__file__), "work")
    os.environ["TEST_ROOT"] = os.path.dirname(__file__)

    # 指定要运行的任务清单
    # 1. 可以为一个目录，该目录下所有robot文件（包括子目录）都会被运行
    # 2. 可以为一个文件，该文件将会被运行
    # 3. 可以为多个文件或者多个目录，中间用逗号隔开
    os.environ["JOB_LIST"] = \
        os.path.join(os.path.join(os.path.dirname(__file__), "demo", "demo1.robot"))

    # 正式开始运行Case
    from .common.runregress import Regress
    runRegress = Regress(
        maxProcess=3,
        scriptTimeout=36000,
        workerTimeout=7200,
        jobList=os.environ["JOB_LIST"]
    )
    runRegress.run()
