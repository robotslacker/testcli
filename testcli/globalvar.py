# -*- coding: utf-8 -*-
import fs

# 内嵌脚本执行时候的命名空间
globalEmbeddScriptScope = globals()

# 最后一次命令执行后的结果，对于SQL和API执行结果也会有所不同
lastCommandResult = {}

# 全局内存文件文件句柄，用于数据的导入导出
globalMemFsHandler = fs.open_fs("mem://")
