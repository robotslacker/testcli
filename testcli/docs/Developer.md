## 以下为程序员修改程序所需要掌握的内容

#### 程序代码结构
```
TestCli
│  LICENSE.txt                                        # 许可信息描述，没啥不许可的，Github非要提供一个不可
│  README.md                                          # 说明文档
│  setup.py                                           # 打包配置
│  uploadpypi.bat                                     # 上传当前发布包到Pypi网站
│
└─testcli
    │  apiparse.py                                    # API语句解析，将Antlr访问结果转为Object
    │  apivisitor.py                                  # Antlr访问脚本，用来描述APIParser叶子节点行为
    │  cmdexecute.py                                  # 根据解析结果，执行相关语句
    │  cmdmapping.py                                  # 脚本映射关系，将脚本内容在执行前根据需要进行改写
    │  compare.py                                     # 公用方法，完成文件差异化比对，提供LCS以及MYES算法
    │  datawrapper.py                                 # 业务实现。用来完成随机数据的生成
    │  global_var.py                                  # 全局变量，其中定义内置脚本的命名空间，程序最后一次执行结果等
    │  hdfswrapper.py                                 # 业务实现。用来完成HDFS数据操作
    │  main.py                                        # 主程序入口。只能用模块的方式启动
    │  sqlclijdbc.py                                  # 业务实现。通过JDBC的方式来实现SQL操作
    │  sqlparse.py                                    # SQL语句解析，将Antlr访问结果转为Object
    │  sqlvisitor.py                                  # Antlr访问脚本，用来描述SQLParser叶子节点行为
    │  testcli.py                                     # 主程序。处理命令行输入信息，根据脚本调用不同的业务实现
    │  testcliexception.py                            # 例外程序定义
    │  testclijobmanager.py                           # 并发任务，任务调度管理
    │  testclimeta.py                                 # 并发业务，数据字典信息
    │  testoption.py                                  # 程序运行选项配置
    │  __init__.py                                    # 模块声明
    │  
    ├─antlr
    │      antlr-4.11.1-complete.jar                  # Antlr编译开发依赖。非运行需要
    │      APILexer.g4                                # API词法定义，继承来自Base
    │      APIParser.g4                               # API语法解析，继承来自Base
    │      BaseLexer.g4                               # 基本词法定义
    │      BaseParser.g4                              # 基础语法解析
    │      generate.bat                               # 辅助工具，编译g4文件，生成antlrgen下文件，非运行需要
    │      SQLLexer.g4                                # SQL词法定义，继承来自Base
    │      SQLParser.g4                               # SQL语法解析，继承来自Base
    │      
    ├─antlrgen                                        # 该目录下所有文件均为Antlr自动生成，不能自行编辑，无说明
    │  │  ...
    │  │  
    ├─commands
    │  │  assertExpression.py                         # 命令实现。 ASSERT语句
    │  │  cliSleep.py                                 # 命令实现。 SLEEP语句
    │  │  compare.py                                  # 命令实现。 COMPARE语句
    │  │  connectdb.py                                # 命令实现。 CONNECT语句
    │  │  echo.py                                     # 命令实现。 ECHO语句
    │  │  embeddScript.py                             # 命令实现。 {% %} 内置脚本语句
    │  │  exit.py                                     # 命令实现。 EXIT|QUIT语句
    │  │  host.py                                     # 命令实现。 HOST语句
    │  │  load.py                                     # 命令实现。 LOAD语句
    │  │  session.py                                  # 命令实现。 SESSION语句
    │  │  spool.py                                    # 命令实现。 SPOOL语句
    │  │  ssh.py                                      # 命令实现。 SSH语句
    │  │  start.py                                    # 命令实现。 START语句
    │  │  userNameSpace.py                            # 命令实现。 USE语句
    │  │  whenever.py                                 # 命令实现。 WHENEVER语句
    │  │  setOptions.py                               # 命令实现。 SET语句
    │  │  __init__.py
    │      
    ├─conf
    │      testcli.ini                                # 配置文件，用来记录SQL驱动程序的驱动信息
    │      
    ├─docs
    │      PyCharm运行配置.png                         # IDE环境配置说明。非运行需要
    │      UserGuide.md                               # 用户使用手册。非运行需要
    │      Developer.md                               # 程序员使用手册。非运行需要
    │      
    ├─jlib
    │      h2-1.4.200.jar                             # H2数据库驱动程序。运行JOB管理必须
    │      README                                     # 驱动简要说明。非运行必须。
    │      ....
    │      
    ├─profile
    │      default                                    # 程序默认初始化执行脚本
    │      
    ├─test                                            # 测试程序目录，非运行必须。
    │  │  pytest.ini                                  # unittest测试程序配置
    │  │  testcliunittest.py                          # 单元测试主程序
    │  │  testmockserver.py                           # 本地模拟HTTP Server程序，用来完成API测试
    │  │  ...
    │  │  
    └───────
```

#### 线程安全性
目前程序在设计上，是考虑到了线程安全性的。但未充分测试这部分。

#### 从源代码中启动应用程序
```
    # 进入到工程目录
    cd testcli
    > python -m testcli.main
```

#### 程序调试
```
   SQL> _set DEBUG ON
   打开DEBUG后，程序将会输出大量的调试信息，以及错误发生时的堆栈信息

```

#### Pycharm中IDE运行-开发插件要求
```
   以下是IDEA的插件为说明。
   必须安装的插件为：
      ANTLR v4
   请注意插件的版本，其版本应该和testcli\antlr\antlr-4.x.x-complete.jar相对应
```

#### Pycharm中IDE运行-工程配置
```
   由于使用了大量的相对引用，所以必须用模块的方式来运行，而不能执行运行main.py中代码
   Prompt_ToolKit需要控制台的一些设置以保证正确运行
```
![PyCharm运行配置](PyCharm运行配置.png)

#### 调试Antlr语法定义
```
   程序中对语法的解析采用Antlr的访问器来解析表达

   如果要修改Antlr语法，请：
   1. 按照要求安装Antlr IDEA插件
   2. 修改g4文件
   3. 右键单击修改后的g4文件，执行Generate Antlr Recognizer, 生成Python运行文件
      第一次Generate前需要配置默认Generate选项(Configure ANTLR...)，选项为：
          Language： 填入Python3
          Generate parse tree listener:  取消选择，即不需要监听器
          Generate parse tree visitor:   选择，即需要访问器      
   3. 修改后可以利用IDEA插件提供的预览器（ANTLR Preview)来检查修改是否正确
   4. 确认修改无误后用generate.bat中的语句来重新生成Antlr的Python运行文件(放置在antlrgen目录下)
      ！！！请不要直接修改antlrgen目录下的文件，此处的修改将不会被保留!!!   
   5. 修改对应的sqlvisitor.py和apivisitor.py文件
      确认能修解析到新的语法内容
   6. 如果修改基础命令，则修改BaseLexer或者BaseParse文件
   7. 对于基础命令，如果visitor文件需要改变，则sqlvisitor文件和apivisitor文件需要同步修改
```

#### 单元测试
```
   程序修改后请运行test\testcliunittest.py，确保测试运行无误，改动没有引起非预期的变化
   
   运行时间大概几分钟，也可以通过命令行中的selftest参数来运行，比如：
   testcli --selftest
```

#### 从应用程序的角度直接调用该程序
TestCli是一个控制台应用，但是你也可以直接绕过控制台应用来直接调用      
结果会用yield的方式非阻塞性逐行返回，包括统计信息、提示信息等：
返回信息的详细解释：
```
    执行错误的语句，返回内容为：
        {
            "type":     "error"
            "message":  错误消息
        }
    对于命令语句解析，返回内容为：
        {
            "type":             "parse"
            "rawCommand":       用数组表示的解析前的语句，包括注释信息
            "formattedCommand": 对语句进行解析后的结果，包含了格式化后的内容信息
            "rewrotedCommand":  语句重写机制的提示信息
            "script":           执行该语句的脚本文件名
        }
    对于数据库语句执行结果，返回内容为：
        {
            "type":        "result"
            "title":        输出内容的标题信息,
            "rows":         结果数据集，用一个二维的元组信息表示，((1,2),(3,4),(5,6),...)
                            每一行数据被记录在一个元组中，所有行的记录再被记录到整个的元组中
            "headers":      表头信息
                            数组。其维数一定和列数相同。 如["COL1", "COL2"]
            "columnTypes":  结果字段类型
                            数组。其维数一定和列数相同。 如["VARCHAR", "INTEGER"]
                            具体列表参考： sqlclijdbc.py中的_DEFAULT_CONVERTERS中信息
            "status":       输出的后提示信息，字符串格式
        }
    对于API语句执行结果，返回内容为：
        {
            "type":        "result"
            "title":       恒定为None
            "rows":        恒定为None
            "headers":     恒定为None
            "columnTypes": 恒定为None
            "status":      JSON格式，内容为：
                           "status"     HTTP请求响应结果
                           "content"    可能为字符串格式（如果可以被解析为JSON格式，则返回JSON格式）
        }
    对于语句执行统计信息，返回内容为：
            "type":             "statistics",
            "startedTime":      语句开始执行时间。 UNIX时间秒单位
            "elapsed":          语句累计执行时间，整形，单位为秒
            "processName":      当前执行语句进程名称
            "rawCommand":       原始语句信息（包含注释等）
            "commandType":      语句类型，字符串，如SQL，HTTP, SLEEP，....
            "command":          解析后的语句，JSON格式表达
            "commandStatus":    命令执行后提示信息
            "errorCode":        错误代码
            "scenarioId":       测试场景ID
            "scenarioName":     测试场景名称
    
    任何语句执行，包括API，包括SQL，总是会用三段返回， 即解析内容、结果内容、统计内容 
```
例子：
```
    testcliHandler = TestCli(HeadlessMode=True, namespace='SQL')
    for result in testcliHandler.cmdExecuteHandler.runStatement(
            statement="_Connect admin/123456@jdbc:linkoopdb:tcp://192.168.10.74:9105/ldb\nselect 1+3 from dual;"
    ):
        if result['type'] in ['parse', 'statistics']:
            continue
        if result['type'] == 'error':
            print("error message: " + str(result['message']))
            break
        print("result = " + str(result))

```
例子2（结果会一次性返回，不会包含统计信息、提示信息等）：
```
    testcliHandler = TestCli(HeadlessMode=True, namespace='SQL')
    command = "_Connect admin/123456@jdbc:linkoopdb:tcp://192.168.10.74:9105/ldb\nselect 1+3 from dual;"
    testcliHandler.DoCommand(command)
    print("rsult = " + str(testcliHandler.getLastCommandResult()))
```
