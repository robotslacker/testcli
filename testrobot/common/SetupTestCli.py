# -*- coding: utf-8 -*-
import os
import shutil
import sys
from robot.api import logger


class SetupRobotException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class SetupTestCli(object):
    # TEST SUITE 在suite中引用，只会实例化一次
    # 也就是说多test case都引用了这个类的方法，但是只有第一个test case调用的时候实例化
    # 如果一个Suite多个Case引用设置类的方法，要注意先后的影响
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    # 初始化文件，文件加载后会自动执行这个文件，用来放置文件的目录
    def __init__(self):
        self.FirstTest = True

        # 将当前目录添加进入Python的ModulePath。 主要是为了多进程并发，子进程能够找到对应的PythonPath
        modulePath = str(os.path.dirname(os.path.realpath(__file__)))
        if modulePath not in sys.path:
            sys.path.append(modulePath)

    @staticmethod
    def SetupRoot_CD_CurrentDirectory(p_szDirectory):
        logger.write("Current directory: [" + str(os.path.dirname(p_szDirectory)) + "]")
        os.chdir(os.path.dirname(p_szDirectory))

    def RecusiveRemove_WorkDirectory(self, p_szDirectoryPath):
        if self.FirstTest:
            logger.write("Will recusive remove work directory ...  [" + p_szDirectoryPath + "]")
            self.FirstTest = False
            if os.path.exists(p_szDirectoryPath):
                files = os.listdir(p_szDirectoryPath)
                for m_file in files:
                    filepath = os.path.join(p_szDirectoryPath, m_file)
                    if os.path.isdir(filepath):
                        if not str(os.path.basename(filepath)) in ["profile", ".gitignore"]:
                            shutil.rmtree(path=filepath, ignore_errors=True)
                    else:
                        # 删除具体某一个文件， 不会删除特定文件
                        if os.path.basename(m_file).endswith("xml"):
                            continue
                        if os.path.basename(m_file).endswith("stdout"):
                            continue
                        if os.path.basename(m_file).endswith("stderr"):
                            continue
                        if os.path.basename(m_file).endswith("cases"):
                            continue
                        if os.path.basename(m_file) in [".gitignore", "farmregress-executor.log"]:
                            continue
                        os.remove(filepath)
        else:
            logger.write("Skip RecusiveRemove_WorkDirectory ... ")

    def __del__(self):
        try:
            import jpype
            if getattr(jpype, "isThreadAttachedToJVM")():
                jpype.java.lang.Thread.detach()
        except ImportError:
            # JPype可能已经被卸载，不再重复操作
            pass
