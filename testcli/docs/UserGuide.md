![机器人小懒](robotslacker.jpg)

# TestCli & TestRobot 命令行测试工具
## 快速说明

本项目是一个主要用Python语言完成，基于命令行下运行的、精致的、小巧的测试工具。      
目前比较全面的覆盖了SQL测试，简单的覆盖了API测试。  

工程包含两个部分：
1. testcli  
交互命令行工具，用来执行SQL脚本、API脚本等，可以独立使用，作为工作小工具；
2. clirobot 
语句命令行工具，用来执行Robot测试程序。
clirobot是基于RobotFrameWork的脚本构建，这个工程中提供了针对TestCli的扩展宏，也提供了运行Python单体程序，Pytest测试程序的宏。


***
### 概要
#### TestCli设计目的：  
* 能够作为一个日常小工具，进行数据库的日常操作，进行数据查询、更新等。      
* 满足数据库的各种功能性测试。执行SQL语句，并验证执行结果是否正确。
* 满足数据库方面的简单的压力测试、稳定性测试需要。   
* 满足API方面的相关功能测试需要。
* 工具内置了一些方便的功能，这些工具用在测试和日常维护方面，会带来很大便利。比如：
  * 方便地用来快速的生成随机数据文件 
  * 内置了Hint的功能，在执行语句后能够根据Hint完成信息过滤、信息掩码、附加排序等
    * 这些可以确保输出的结果文件更加稳定，避免程序结果文件收到噪音干扰
  * 使用TermOut，FeedBack，ECHO来控制显示输出的内容
    * 同样目的是为了使得结果文件更加稳定，避免程序结果文件收到噪音干扰
  * 使用ECHO来生成一些临时性的文件
  * 使用COMPARE来进行文件级别的内容比对，比对过程中支持了正则表达过滤，正则表达掩码
    * 通常我们把经过验证的、正确的结果存盘为参考文件
    * 当参考文件和当前输出存在不一致的现象，则说明存在测试脚本的潜在问题或者代码行为存在潜在问题。
  * 脚本内使用SSH来完成远程主机命令的操作，文件的上传和下载
  * 使用JobManager（任务管理器）来并行执行多个脚本
    * 并行多脚本操作主要用来测试多测试之间需要严格控制时序、验证并发锁冲突的测试
    * 提供了聚合点的完整支持，如多个脚本运行到同一个时刻点后等待
  * 使用MonitorManager（监控管理器）来在测试执行的时候监控系统、进程性能信息，并作为测试的结果输出
    * 监控管理器提供了简单的性能监控、性能数据记录能力
    * 不建议复杂的压力测试或者稳定性测试依赖MonitorManager，大压力下使用第三方的JMeter能获得更好的测试效果和更完善的监控能力
  * 支持在测试脚本中嵌入Python语法来完成一些常规难以完整的验证
    * 建议将脚本进行模块化封装后，再直接嵌入模块的调用，避免直接在脚本中嵌入复杂Python脚本后的阅读性下降问题
  * 使用LOAD SCRIPT来加载用户自己提供的Python文件作为测试内嵌Python语法的扩展
  * 使用LOAD PLUGIN来加载用户自己提供的Python文件作为新的脚本命令
  * 支持对测试脚本中的变量信息进行宏替换，包括基于映射文件的替换，基于应用变量的替换，基于环境变量的替换
  * 支持在程序中捕捉返回的上下文信息，利用前面执行的结果来影响后续的执行逻辑
  * 支持在程序中使用简单的LOOP，IF等循环、条件判断表达式，来完成复杂的测试逻辑
  * 使用ASSERT来判断运行的结果
  * 使用SESSION来完成多个数据库会话客户端的切换和状态保存
  * 使用SESSION来完成多个API会话客户端的切换和状态保存
  * 在API测试中可以灵活地处置API测试的上下文关系，变量的传递，环境信息的针对性处理
  * 在API测试中上传或者下载数据文件

#### CliRobot设计目的：
  * 封装TestCli的运行，封装中完善考虑测试用例场景、测试结果展现等应用需求
  * 封装了Python单体程序，Pytest测试程序的运行、测试结果展现等应用需求
  * 基于RobotFrameWork，提供了多个测试脚本之间的并发控制、超时控制
  * 基于RobotFrameWork，提供了HTML格式、JUNIT格式的测试报告生成

***

***
#### TestCli目前支持的数据库  
   * Oracle,MySQL,PostgreSQL,SQLServer,TeraData, Hive, H2等主流通用数据库  
   * 达梦，神通， 金仓， 南大通用，快立方等众多国产数据库  
   * ClickHouse数据库      
   * 其他符合标准JDBC规范的数据库
   * 以上描述的支持是指在相关数据库上进行过基本的测试，但显然我们没法覆盖全部的测试点

***
#### TestCli的数据类型映射
以下是数据库类型到TestCli中数据类型的映射关系（右面的数据类型均为Python的原生数据类型）：
```  
    CHAR                                  ====>     str
    VARCHAR                               ====>     str
    LONGVARCHAR                           ====>     str
    TIMESTAMP_WITH_TIMEZONE               ====>     datetime.datetime
    TIMESTAMP                             ====>     datetime.datetime
    TIME                                  ====>     datetime.time
    DATE                                  ====>     datetime.date
    BINARY                                ====>     bytearray  
    VARBINARY                             ====>     bytearray
    LONGVARBINARY                         ====>     bytearray
    DECIMAL                               ====>     decimal.Decimal  
    NUMERIC                               ====>     decimal.Decimal
    DOUBLE                                ====>     decimal.Decimal
    REAL                                  ====>     decimal.Decimal
    FLOAT                                 ====>     float
    TINYINT                               ====>     int
    INTEGER                               ====>     int
    SMALLINT                              ====>     int  
    INTEGER                               ====>     int
    BOOLEAN                               ====>     bool
    BFILE                                 ====>     str "bfilename(dirpath:filename)"
    BIGINT                                ====>     decimal.Decimal
    BIT                                   ====>     decimal.Decimal
    STRUCT                                ====>     tuple()
    ARRAY                                 ====>     list()
    CLOB                                  ====>     TestCliLargeObject.getData() ==> str
    BLOB                                  ====>     TestCliLargeObject.getData() ==> bytearray
```
***

### 这个工具不能做什么
这个工具的存在目的不是为了替代各种数据库的命令行工具，如Oracle的SQLPlus，MYSQL的mysql等  
这个工具的存在目的是在尽可能地兼容这些命令行工具的同时提供测试工作需要的相关特性。    
选择了Python作为代码开发工具，Python本身部署的复杂性和对环境的依赖性决定了这个工具无法作为交付产品的功能之一提供给客户。  
这个工具的存在目的不是为了替代PostMan，JMeter等测试工具。

虽然可以用作压力测试，但是这个工具的并发机制是基于多进程，而不是多线程。  
这句话的意思是：在非常高地并发下，由于多进程机制的自身资源消耗，测试工具本身成了资源消耗重点。  
所以： 工具本身不适合非常高地并发压力，比如并发超过100或者更高。

***
### 安装
安装的前提有：
   * 有一个Python 3.6以上的环境
   * 安装JDK8或者JDK11  （目前我的调试环境和测试环境均为JDK11，已知JDK8无问题，未对其他JDK环境进行验证） 
   * 对于Windows平台，需要提前安装微软的C++编译器（或者CMake，未测试，原因是jpype1使用了JNI技术，需要动态编译）  
   * 对于Linux平台，  需要提前安装gcc编译器
     yum install -y gcc-c++ gcc  
   * 对于MAC平台，  需要提前安装gcc编译器    
     brew install gcc  

依赖的第三方安装包：  
   * 这些安装包会在robotslacker-testcli安装的时候自动随带安装
   ```
   JPype1                   : Python的Java请求封装，用于完成运行时JDBC请求调用  
   setproctitle             : Python通过setproctitle来设置进程名称，从而在多进程并发时候给调试人员以帮助
   urllib3                  : HTTP客户端请求操作
   click                    : Python的命令行参数处理
   prompt_toolkit           : 用于提供交互式命令行和终端应用程序
   paramiko                 : Python的SSH协议支持，用于完成远程主机操作  
   fs                       : 构建虚拟文件系统，用来支撑随机数据文件的生成
   psutil                   : Python的监控管理
   glom                     : 用于API返回结果中的过滤
   antlr4-python3-runtime   : Antlr4运行时引用(由于程序放置的是编译好的Antlr文件，所以这里需要对版本进行精确控制。 目前版本是4.11.1)
   python-multipart         : urllib用来完成多段API请求
   
   pytest                   ：程序自身的测试需要，并不是运行必须项
   fastapi                  ：程序自身的测试需要，并不是运行必须项
   uvicorn                  ：程序自身的测试需要，并不是运行必须项
   
   coloredlogs              : 颜色化的日志输出，testRobot需要
   robotframework           : Python命令行驱动测试框架，testRobot需要
   beautifulsoup4           : 测试报告格式化输出，testRobot需要
   lxml                     : 测试报告结果处理，testRobot需要
   ```

利用pip来安装：
```
   pip install -U robotslacker-testcli
```

***

### 程序的自检
运行selftest可以在当前运行环境上快速检查程序是否存在问题  
尽管这不是程序运行所必须的，但是仍然建议在部署应用之前运行该命令以帮助发现潜在的问题。  
命令大概需要几分钟的时间，为了测试API业务，程序还会占用8000,19091的端口作为测试的需要。  
```
(base) C:\>testcli --selftest
=========================== test session starts =======================
platform win32 -- Python 3.9.7, pytest-7.2.0, pluggy-0.13.1 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
....
================================== 65 passed in 72.25s ================
```
如果你看到所有项目都是Passed信息，那说明程序自检完全正常，几乎不会有太大的其他问题。你可以放心的在当前环境下开展你的工作了。 

### TestCli

#### 程序命令行参数

```
(base) C:\>testcli --help
Usage: testcli [OPTIONS]

Options:
  --logon TEXT             SQL logon user name and password. user/pass
  --namespace TEXT         Command default name space(SQL|API). Default is
                           depend on file suffix.

  --execute TEXT           Execute command script.
  --reference TEXT         Test result reference.
  --logfile TEXT           Log every command and its results to file.
  --xlogoverwrite          Overwrite extended log if old file exists. Default
                           is false.

  --xlog TEXT              Save command extended log.
  --commandmap TEXT        Command mapping file.
  --profile TEXT           Startup profile. Default is none.
  --clientcharset TEXT     Set client charset. Default is UTF-8.
  --resultcharset TEXT     Set result charset. Default is same to
                           clientCharset.

  --scripttimeout INTEGER  Script timeout(seconds). Default is -1, means no
                           limit.

  --suitename TEXT         Test suite name.
  --casename TEXT          Test case name.
  --runid TEXT             Test run unique id. Default is 0. will save in
                           extend log for later analyze.

  --silent                 Run script in silent mode, no console output.
                           Default is false.

  --daemon                 Run script in daemon mode. Default is false.
  --debug                  Run in debug mode. Default is False.
  --pidfile TEXT           Set pid file path and filename. Default is no pid
                           control.

  --selftest               Run self test and exit.
  --version                Show TestCli version.
  --nologo                 Execute with no-logo mode.
  --help                   Show this message and exit.
      
```

##### --version 

用来显示当前工具的版本号

```
(base) C:\>testcli --version
Version: 0.0.7
```

##### --logon  

用来输入连接数据的的连接字符串
使用完成的连接字符串：

``` 
(base) C:\>testcli --logon user/pass@jdbc:mysql://127.0.0.1:3306/testdb
TestCli Release 0.0.7
SQL> Database connected.
SQL>
```

也可以在设置了TESTCLI_CONNECTION_URL后省略连接字符串后面部分：

```
(base) C:\>testcli --logon admin/123456
TestCli Release 0.0.7
SQL> Database connected.
SQL>

user/pass : 数据库连接的用户名和口令  
成功执行这个命令的前提是你已经在环境变量中设置了数据库连接的必要信息。  
这里的必要信息是指：
   环境变量：  TESTCLI_CONNECTION_URL
   参数格式：  jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名]
```

##### --logfile   

用来记录本次命令行操作的所有过程信息    

```
(base) C:\>testcli --logfile example.log
TestCli Release 0.0.7
SQL> _connect /mem
Database connected.
SQL> create table aaa (id int);
0 row affected.
SQL> insert into aaa values(10);
1 row affected.
SQL> select * from aaa;
+--------+----+
|   ##   | ID |
+--------+----+
|      1 | 10 |
+--------+----+
1 row selected.
SQL> _exit
Disconnected.

(base) C:\>type example.log
SQL> _connect /mem
Database connected.
SQL> create table aaa (id int);
0 row affected.
SQL> insert into aaa values(10);
1 row affected.
SQL> select * from aaa;
+--------+----+
|   ##   | ID |
+--------+----+
|      1 | 10 |
+--------+----+
1 row selected.
SQL> _exit
Disconnected.
```

##### --execute 

在TestCli启动后执行特定的脚本  
通过execute参数，可以让testcli来执行这个脚本，而不再需要我们一行一行的在控制台输入  
脚本的后缀将影响执行的默认命名空间。  

```
(base) C:\>type example.sql
_connect /mem
create table aaa(id int);
insert into aaa values(10);
select * from aaa;

(base) C:\>testcli --execute example.sql
TestCli Release 0.0.7
SQL> _connect /mem
Database connected.
SQL> create table aaa(id int);
0 row affected.
SQL> insert into aaa values(10);
1 row affected.
SQL> select * from aaa;
+--------+----+
|   ##   | ID |
+--------+----+
|      1 | 10 |
+--------+----+
1 row selected.
Disconnected.

(base) type test.sql
select * from test_tab;

注意： 即使你的脚本中不包含Exit/Quit语句，在TestCli执行完当前脚本后，他也会自动执行exit语句
```

##### --commandmap   

在命令执行的时候，指定命令的映射文件信息  
提供映射信息文件的目的是为了解决一个测试场景。  
即：有的测试脚本需要反复多次的运行，其区别仅仅是部分参数信息的不同。  
需要注意的是，映射文件仅仅是一种用来支撑上述测试场景的做法，实际上还可以使用变量方法，具体使用哪一种方法，要看测试的实际需要。

```
# aa.map以下是一个典型的映射文件, 这里我们将TAB映射为了TAB1
(base) C:\> type testsqlmapping.map
#..*:
TABA=>TAB1
#.

# 再定义一个测试脚本
(base) C:\> type testsqlmapping.sql
_connect /mem
create table {{TABA}}
(
    id  int
);

insert into {{TABA}} values(3);
insert into {{TABA}} values(4);

# 指定测试脚本，并明确指定映射文件
(base) C:\> testcli --execute testsqlmapping.sql --commandmap testsqlmapping.map
TestCli Release 0.0.7
SQL> _connect /mem
Database connected.
SQL> create table {{TABA}}
   > (
   >     id  int
   > );
REWROTED SQL> Your SQL has been changed to:
REWROTED    > create table TAB1
REWROTED    > (
REWROTED    >     id  int
REWROTED    > )
0 row affected.
SQL>
SQL> insert into {{TABA}} values(3);
REWROTED SQL> Your SQL has been changed to:
REWROTED    > insert into TAB1 values(3)
1 row affected.
SQL> insert into {{TABA}} values(4);
REWROTED SQL> Your SQL has been changed to:
REWROTED    > insert into TAB1 values(4)
1 row affected.
Disconnected.

# 以上我们注意到，脚本中的{{TAB}}在实际运行中被替换成了TAB1
# 类似的，如果我们定义testsqlmapping.map中，将TAB1改为TAB2. 我们就会收到TAB2的替换
# 通过这种方法，我们可以通过定义一个测试脚本，多个MAP的方法来让测试脚本复用在不同的测试环境中
```

##### --nologo    

选项，用来控制TestCli是否会在连接的时候显示当前的程序版本

```
(base) testCli 
TestCli Release 0.0.7
SQL>   
区别：
(base) testCli --nologo
SQL>
```

##### --xlog  

输出测试运行的扩展日志，并指定扩展日志的文件名      
这里说的日志不是指程序的logfile，而是用sqlite格式文件记录的测试日志    
这些日志将作为后续对测试运行行为的一种分析    
运行日志共包括如下信息：  

```
     Id              INTERGER  整数，自增长序列
     Script          TEXT      当前运行的测试脚本名称  
     Started         DATETIME  当前语句执行时间
     Elapsed         NUMERIC   当前语句执行耗时，秒为单位，最多精确两位小数
     RawCommand      TEXT      当前语句的原始命令信息
     CommandType     TEXT      当前命名类型，枚举的字符串类型，如LOAD，SSH，ASSERT等...
     Command         TEXT      语句被Antlr解析后的解析结果，用JSON格式记录下来
     CommandStatus   TEXT      语句的命令行状态输出。 注意，这里不是数据结果的输出，而是命令结果
                               对于错误语句，可能得到的错误的详细信息
                               对于正确语句，可能得到的语句影响的记录数量等
     ErrorCode       TEXT      错误代码。如果错误，会填写正确的错误代码。如果不填写，或者填写为0，表示语句执行正常
     WorkerName      TEXT      执行器名称，对于多线程执行，其中包含线程信息。对于单线程执行，其中包含进程PID信息
     SuiteName       TEXT      测试套件名称。这个来源于外界的参数输入，只是作为记录被保存在这里
     CaseName        TEXT      测试用例名称。这个来源于外界的参数输入，只是作为记录被保存在这里
     ScenarioId      TEXT      测试场景ID，这个来源于测试脚本中的Hint定义，随后会详细介绍如何定义测试场景ID
     ScenarioName    TEXT      测试场景名称，这个来源于测试脚本中的Hint定义，随后会详细介绍如何定义测试场景名称
```

以下是实际的一行扩展日志效果：

```
     Id              =>  2
     Script          =>  aa.api  
     Started         =>  2022-12-28 22:33:27  
     Elapsed         =>  1.09
     RawCommand      =>  _connect /mem  
     CommandType     =>  CONNECT 
     Command         =>  {"driver": "jdbc", "driverSchema": "h2mem", "driverType": "mem", "host": "0.0.0.0" ...  
     CommandStatus   =>  Database connected.
     ErrorCode       =>  0
     WorkerName      =>  MAIN-9709
     SuiteName       =>  suite1
     CaseName        =>  cas1
     ScenarioId      =>  13279
     ScenarioName    =>  测试数据库连接
```

##### --xlogoverwrite      

控制如果扩展日志文件已经存在的方式下，是否会覆盖掉原有的扩展日志文件。默认是不覆盖，即追加模式

##### --clientcharset      

定义客户端的字符集，默认为UTF-8  
客户端的字符集影响了脚本的字符集，命令行中输入信息的字符集  

##### --resultcharset      

定义了结果输出文件的字符集，包括日志文件，也包括SPOOL导出的文件，也包括ECHO生成的回显文件

##### --profile            

定义程序的启动文件，在程序启动之前会首先运行该文件，随后开始正式的执行测试脚本文件。  
以下是一个在启动文件里头连接数据库，并随后在测试脚本中完成测试的例子。  

```
(base) C:\>type myprofile.sql
_connect /mem

(base) C:\>type testprofile.sql
create table aaa (id int);
insert into aaa values(10);
select * from aaa;

(base) C:\>testcli --execute testprofile.sql --profile myprofile.sql
TestCli Release 0.0.7
PROFILE SQL> _connect /mem
PROFILE Database connected.
SQL> create table aaa (id int);
0 row affected.
SQL> insert into aaa values(10);
1 row affected.
SQL> select * from aaa;
+--------+----+
|   ##   | ID |
+--------+----+
|      1 | 10 |
+--------+----+
1 row selected.
Disconnected.

# 上述的例子中会首先执行myprofile.sql，随后才会执行testprofile.sql中的测试内容
```

##### --scripttimeout   

控制脚本的最大超时时间，这里的计数单位是秒。默认为-1，即完全不控制。    
以下是一个设置了scriptTimeout为3的时候的执行例子，当达到3秒的限制后，脚本会立刻结束运行，不再继续下去。 

```
TestCli Release 0.0.7
API> _use sql
Current NameSpace: SQL.
SQL> _sleep 5
TestCli-000: Script Timeout (3) expired. Abort this Script.
Disconnected.
```

需要注意的是：  

1. Abort操作受限于编程语言的实现，只能尽力去释放资源，并不保证资源的完全释放完毕。
2. 这里的超时时间并不是一个精确时间，对于一些快速的操作，如语句解析，打印输出等并没有被统计在运行耗时内，所以超时控制是一个相对准确的限制，不能作为绝对的时间依赖。  
3. 除了在命令行上指定脚本的全局超时时间限制外，还可以在脚本中指定具体语句的执行时间显示。 具体地介绍将在后面部分描述。  

##### --namespace    

指定程序的默认命名空间，如果不指定，命名空间的默认依赖于文件后缀，具体的规则是：  

1. 文件后缀为.sql， 则默认的命名空间为SQL
2. 文件后缀为.api， 则默认的命名空间为API
3. 其他文件后缀，默认的命名空间为SQL  
   命名空间的不同将影响语句的解析执行， 你也可以在脚本中进行命名空间的切换  

##### --selftest      

运行自测脚本并退出  
这个选项仅仅用于测试当前环境下是否已经正确安装了本工具。  

##### --suitename     

指定测试套件的名称，这个通常用于记录在扩展日志，或者完成测试报告的时候协助统计分析测试结果使用

##### --casename      

指定测试用例的名称，这个通常用于记录在扩展日志，或者完成测试报告的时候协助统计分析测试结果使用  

##### --silent

指定是否为静默方式调用，如果是静默方式，则屏幕上不会输出任何信息

##### --daemon

指定是否为后台进程方式运行（只针对非Windows平台）  
后台方式下由于无法输入，所以只能用指定脚本方式来运行  

##### --pidfile

是否打印PID信息到指定的文件中，默认是不打印，即不产生pidfile文件  

##### --runid

为每次测试提供一个唯一ID，ID会被记录到扩展日志中，作为日后统计分析的需要

##### --help          

显示本帮助信息并退出

#### 驱动程序的下载和配置
TestCli是一个基于JDBC的数据库工具，基于JDBC操作数据库的前提当前环境下有对应的数据库连接jar包。 

##### 驱动程序的配置
配置文件可能存放在：
1. 环境变量${TESTCLI_CONF}所指定的文件
2. 环境变量${TESTCLI_HOME}下的conf/testcli.ini文件
3. TestCli的Python安装目录下的conf目录中，配置文件名为:testcli.ini
上述3个文件按照优先级依次查找，当找到配置文件时，即采用当前配置文件。 

配置例子:

```
[env]
JAVA_HOME=${PATH}

[driver]
oracle=oracle_driver
mysql=mysql_driver
.... 

[oracle_driver]
filename=ojdbc8.jar
driver=oracle.jdbc.driver.OracleDriver
jdbcurl=jdbc:oracle:thin:@${host}:${port}/${service}

[mysql_driver]
filename=mysql-connector-java-8.0.20.jar
driver=com.mysql.cj.jdbc.Driver
jdbcurl=jdbc:mysql://${host}:${port}/${service}
```
配置文件说明：  
    env.JAVA_HOME: 配置程序使用的JAVA_HOME信息。   
    这个参数可以不配置，如果不配置，程序讲读取操作系统的JAVA_HOME变量定义。  
    这个参数如果配置，将优先使用这个参数，而不再去读取系统环境信息。  


如果数据库要新增其他数据库的连接，则应仿效上述配置例子。  
其中：  
* 所有的数据库名称及配置项名称均应该出现在[driver]的配置项中  
  如果某一种数据库连接需要不止一个jar包，则这里应该配置多个配置项  
  例如：   mydb=mydb1_driver1, mydb1_driver2
* 数据库的具体配置应该在具体的配置项中  
  filename：      可选配置项，jar包具体的名字  
  driver:         可选配置项，数据库连接的主类  
  jdbcurl:        可选配置项，jdbc连接字符串，其中${host} ${port} ${service}分别表示数据库连接主机，端口，数据库名称  
  jdbcprop:       可选配置项，若该数据库连接需要相应的额外参数，则在此处配置



***

#### 在TestCli里面使用帮助
```
(base) TestCli 
TestCli Release 0.1.1
SQL> _help
+--------+-------------+----------------------------------------------------------------------------+-----------+
|   ##   |   COMMAND   |                                  SUMMARY                                   | NAMESPACE |
+--------+-------------+----------------------------------------------------------------------------+-----------+
|      1 | EXIT        | exit current script with exitValue (Default is 0)                          | ALL       |
|      2 | QUIT        | force exit current script with exitValue (Default is 0)                    | ALL       |
|      3 | LOAD        | load external map/driver/plugin files.                                     | ALL       |
|      4 | SSH         | Remote SSH operation.                                                      | ALL       |
|      5 | COMPARE     | Diff test result and reference log.                                        | ALL       |
|      6 | ECHO        | echo some message to file.                                                 | ALL       |
|      7 | SPOOL       | spool following command and command output to file.                        | ALL       |
|      8 | JOB         | Run slave script in parallel.                                              | ALL       |
|      9 | DATA        | Generate test random data.                                                 | ALL       |
|     10 | SLEEP       | sleep app some time                                                        | ALL       |
|     11 | ASSERT      | Execute the assertion. Determine whether the specified conditions are met. | ALL       |
|     12 | USE         | Switch the namespace of the current script.                                | ALL       |
|     13 | HOST        | Execute local system commands.                                             | ALL       |
|     14 | SET         | Set/View app runtime options.                                              | ALL       |
|     15 | START       | Run sub command script.                                                    | ALL       |
|     16 | SCRIPT      | Run embedded python script.                                                | ALL       |
|     17 | MONITOR     | Monitor system perference.                                                 | ALL       |
|     18 | SPOOL       | Print subsequent run commands and results to the specified file.           | ALL       |
|     19 | IF          | Conditional statement.                                                     | ALL       |
|     20 | LOOP        | LOOP statement.                                                            | ALL       |
|     21 | CONNECT     | Connect to JDBC database.                                                  | SQL       |
|     22 | SQL         | Execute sql statement.                                                     | SQL       |
|     23 | SQLSESSION  | SQL session management.                                                    | SQL       |
|     24 | HTTPSET     | Set http request behavior.                                                 | API       |
|     25 | HTTP        | Execute http statement.                                                    | API       |
|     26 | HTTPSESSION | Http session management.                                                   | API       |
+--------+-------------+----------------------------------------------------------------------------+-----------+
Use "_HELP <command>" to get detail help messages.
```
这里显示的是TestCli自身支持的命令(示例，并不是全部语句)，不包括SQL语句，API执行语句部分。  
具体SQL语句的写法参考具体数据库对SQL的要求；    
具体API语句的写法参考HTTP协议报文要求；  

查看命令的详细信息，以下用COMPARE命令作为例子（其他命令的描述格式类似，不再重复说明）：  
```
SQL> _help compare
  Command:
    COMPARE

  Summary:
    Diff test result and reference log.

  Synatx:
    _COMPARE <work file name> <reference file name> {MASK | NOMASK | CASE | NOCASE | IGBLANK | NOIGBLANK | TRIM | NOTRIM}
    _COMPARE SKIPLINE <the line expression to skip>
    _COMPARE NOSKIPLINE <the skip line to undefine>
    _COMPARE MASKLINE <<src pattern to mask> >= <target string after mask>>
    _COMPARE NOMASKLINE <the mask line to undefine>
    _COMPARE RESET
    _COMPARE SET {MASK | NOMASK | CASE | NOCASE | IGBLANK | NOIGBLANK | TRIM | NOTRIM}
    _COMPARE SET OUTPUT { CONSOLE | DIFFFILE | HTMLFILE }
    _COMPARE SET ALGORITHM [LCS | MYERS]
    _COMPARE SET WORK ENCODING <work file codec, default is UTF-8>
    _COMPARE SET REFERENCE ENCODING <reference file codec. default is UTF-8>
```
对于上述语法描述中，遵循BNF格式。 即：
```
1. <>     表示需要输入的内容    
2. []     表示可选输入的内容
3. |      表示必须是几个选项之一
4. {}     表示为其中一项或者多项
5. 无符号  表示需要输入的关键字
```

***
#### 设置程序的运行选项
通过SET命令，我们可以改变TestCli的一些行为或者显示选项。
```
    SQL> _set
    Current Options:
    +--------+---------------------------+----------------------+-----------------------------------------------------+
    |   ##   |            Name           |        Value         |                       Comments                      |
    +--------+---------------------------+----------------------+-----------------------------------------------------+
    |      1 | WHENEVER_ERROR            | CONTINUE             |                                                     |
    |      2 | PAGE                      | OFF                  | ON|OFF                                              |
    |      3 | ECHO                      | ON                   | ON|OFF                                              |
    |      4 | TIMING                    | OFF                  | ON|OFF                                              |
    |      5 | TIME                      | OFF                  | ON|OFF                                              |
    |      6 | FEEDBACK                  | ON                   | ON|OFF                                              |
    |      7 | TERMOUT                   | ON                   | ON|OFF                                              |
    |      8 | SQL_FETCHSIZE             | 10000                |                                                     |
    |      9 | LOB_LENGTH                | 20                   |                                                     |
    |     10 | FLOAT_FORMAT              | %.7g                 |                                                     |
    |     11 | DECIMAL_FORMAT            |                      |                                                     |
    |     12 | DATE_FORMAT               | %Y-%m-%d             |                                                     |
    |     13 | DATETIME_FORMAT           | %Y-%m-%d %H:%M:%S.%f |                                                     |
    |     14 | TIME_FORMAT               | %H:%M:%S.%f          |                                                     |
    |     15 | DATETIME-TZ_FORMAT        | %Y-%m-%d %H:%M:%S %z |                                                     |
    |     16 | OUTPUT_SORT_ARRAY         | ON                   | Print Array output with sort order. ON|OFF          |
    |     17 | OUTPUT_PREFIX             |                      | Output Prefix                                       |
    |     18 | OUTPUT_ERROR_PREFIX       |                      | Error Output Prefix                                 |
    |     19 | OUTPUT_FORMAT             | TAB                  | TAB|CSV                                             |
    |     20 | OUTPUT_CSV_HEADER         | OFF                  | ON|OFF                                              |
    |     21 | OUTPUT_CSV_DELIMITER      | ,                    |                                                     |
    |     22 | OUTPUT_CSV_QUOTECHAR      |                      |                                                     |
    |     23 | SQLCONN_RETRYTIMES        | 1                    | Connect retry times.                                |
    |     24 | CONNURL                   |                      | Connection URL                                      |
    |     25 | CONNSCHEMA                |                      | Current DB schema                                   |
    |     26 | SQL_EXECUTE               | PREPARE              | DIRECT|PREPARE                                      |
    |     27 | JOBMANAGER                | OFF                  | ON|OFF                                              |
    |     28 | JOBMANAGER_METAURL        |                      |                                                     |
    |     29 | SCRIPT_TIMEOUT            | -1                   |                                                     |
    |     30 | SQL_TIMEOUT               | -1                   |                                                     |
    |     31 | API_TIMEOUT               | -1                   |                                                     |
    |     32 | SCRIPT_ENCODING           | UTF-8                |                                                     |
    |     33 | RESULT_ENCODING           | UTF-8                |                                                     |
    |     34 | SSH_ENCODING              | UTF-8                | SSH channel default encoding.                       |
    |     35 | COMPARE_DIFFLIB_THRESHOLD | 1000                 | Threshold(lines) for use difflib compare algorithm. |
    |     36 | NAMESPACE                 | SQL                  | Script Namespace, SQL|API                           |
    |     37 | MONITORMANAGER            | OFF                  | ON|OFF                                              |
    |     38 | API_HTTPSVERIFY           | OFF                  | ON|OFF (Default)                                    |
    |     39 | API_HTTPPROXY             |                      | Proxy address of http request. (Default)            |
    +--------+---------------------------+----------------------+-----------------------------------------------------+    
    没有任何参数的set命令将会列出程序所有的配置情况。
```

##### 控制参数解释-WHENEVER_ERROR
&emsp; 用来控制在执行命令过程中遇到命令错误，是否继续。 默认是CONTINUE，即继续。   
&emsp; 目前支持的选项有：    
```
       CONTINUE      |     遇到SQL语句错误继续执行 
       EXIT <int>    |     遇到SQL语句错误直接退出TestCli程序, int为退出时候的返回值
```
WHENEVER_ERROR不支持用SET命令来调整，如果需要调整，需要使用_WHENEVER ERROR <EXIT <int> | CONTINUE>

##### 控制参数解释-PAGE
&emsp; 是否分页显示，当执行的命令结果超过了屏幕显示的内容，是否会暂停显示，等待用户输入任意键后继续显示下一页，默认是OFF，即不中断。  
&emsp; 以下是中断的效果， 中断后单击任意键将显示下一篇内容。  
&emsp; PAGE的设置在脚本执行中将被忽略。
```
+--------+----+
|   ##   | ID |
+--------+----+
|      1 |  1 |
|      2 |  1 |
|      3 |  1 |
|      4 |  1 |
|      5 |  1 |
|      6 |  1 |
|      7 |  1 |
|      8 |  1 |
|      9 |  1 |
|     10 |  1 |
|     11 |  1 |
|     12 |  1 |
|     13 |  1 |
-- More  --
```

##### 控制参数解释-ECHO
&emsp; &emsp; 命令回显标志， 默认为ON，即命令内容在LOG中需要回显
```
        SQL> _set ECHO ON      # 在LOG中将会回显命令语句
        SQL> _set ECHO OFF     # 在LOG中不会回显命令语句

        例如：执行SELECT 3 + 5 COL1 FROM DUAL，

        在ECHO打开下，log文件内容如下:
        SQL> SELECT 3 + 5 COL1 FROM DUAL;
        SQL> ===========
        SQL> =  COL1 ===
        SQL> ===========
        SQL>           8
        SQL> 1 rows selected.

        在ECHO关闭下，log文件内容如下:
        SQL> ===========
        SQL> =  COL1 ===
        SQL> ===========
        SQL>           8
        SQL> 1 rows selected.
```

##### 控制参数解释-TIMING
&emsp; 语句运行结束后打印当前语句的执行时间  
```
    SQL> _set timing ON
    Running time elapsed:      0.00 seconds
    SQL> delete from aaa;
    510 rows affected.
    Running time elapsed:      0.04 seconds
```

##### 控制参数解释-TIME
&emsp; 语句运行结束后打印当前系统时间  
```
    SQL> _set time ON
    Current clock time  :2023-01-28 20:02:12
    SQL> _connect /mem
    Database connected.
    Current clock time  :2023-01-28 20:02:18
    SQL> create table aaa (id int);
    0 row affected.
    Current clock time  :2023-01-28 20:02:25
```

##### 控制参数解释-FEEDBACK
&emsp; 控制是否回显执行影响的行数，默认是ON，显示  
```
       SQL> _set feedback on
       SQL> select * from test_tab;
       +----+----------+
       | ID | COL2     |
       +----+----------+
       | 1  | XYXYXYXY |
       | 1  | XYXYXYXY |
       +----+----------+
       2 rows selected.
       SQL> _set feedback off
       SQL> select * from test_tab;
       +----+----------+
       | ID | COL2     |
       +----+----------+
       | 1  | XYXYXYXY |
       | 1  | XYXYXYXY |
       +----+----------+
```
##### 控制参数解释-TERMOUT
&emsp; 控制是否显示命令结果的返回，默认是ON，显示  

```
       SQL> _set termout on
       SQL> select * from test_tab;
       +----+----------+
       | ID | COL2     |
       +----+----------+
       | 1  | XYXYXYXY |
       | 1  | XYXYXYXY |
       +----+----------+
       2 rows selected.
       SQL> set termout off
       SQL> select * from test_tab;
       2 rows selected.

```

##### 控制参数解释-SQL_FETCHSIZE
&emsp; SQL数据预读取Fetch的缓冲区大小  
```
    默认是10000，设置值为非零的正整数
    如果数据量很大，一次性从数据源读取，会造成数据库过大压力
    通过这个参数，可以控制每次从数据库读取的记录集大小
    如果没有十分必要的需求，不建议修改这个参数。过低的参数将导致程序运行性能下降
```

##### 控制参数解释-OUTPUT_FORMAT
&emsp; 结果集显示格式， 默认是TAB
&emsp; 目前支持的选项有：
```
      CSV       |     显示格式为CSV文件的格式
      TAB       |     显示格式为表格的格式
```
&emsp; 以下是一个例子：
```
       SQL> _set output_format csv
       SQL> select * from test_tab;
       "ID","COL2"
       "1","XYXYXYXY"
       "1","XYXYXYXY"
       2 rows selected.

       SQL> _set output_format tab
       SQL> select * from test_tab;
       +--------+----+----------+
       |   ##   | ID | COL2     |
       +--------+----+----------+
       |      1 | 1  | XYXYXYXY |
       |      2 | 1  | XYXYXYXY |
       +--------+----+----------+
       2 rows selected.
```

##### 控制参数解释-LOB_LENGTH
&emsp; 控制LOB字段的输出长度，默认是20  
&emsp; 由于LOB字段中的文本长度可能会比较长，所以默认不会显示出所有的LOB内容到当前输出中，而是最大长度显示LOB_LENGTH值所代表的长度对于超过默认显示长度的，将在输出内容后面添加...省略号来表示   
&emsp; 对于BLOB类型，输出默认为16进制格式。对于超过默认显示长度的，将在输出内容后面添加...省略号来表示 
```       
        SQL> create table aaa(id clob);
        0 row affected.
        SQL> insert into aaa values('123123123131221321jfdlasjfsdalfjdsalf;jdsaf;dssjf;sadjfads;fsdafasfafafdafdajfoieqwupqewrqweerqp');
        1 row affected.
        SQL> -- 默认的LOB_LENGTH长度不足数据长度
        SQL> select * from aaa;
        +--------+------------------------------------------+
        |   ##   |                    ID                    |
        +--------+------------------------------------------+
        |      1 | Len:96;Content:[12312312313122132...rqp] |
        +--------+------------------------------------------+
        1 row selected.
        SQL> -- 设置的长度不足数据长度
        SQL> _set LOB_LENGTH 5
        SQL> select * from aaa;
        +--------+---------------------------+
        |   ##   |             ID            |
        +--------+---------------------------+
        |      1 | Len:96;Content:[12...rqp] |
        +--------+---------------------------+
        1 row selected.
        SQL> -- 设置的长度超过数据的长度 
        SQL> _set LOB_LENGTH 300
        SQL> select * from aaa;
        +--------+--------------------------------------------------------------------------------------------------+
        |   ##   |                                                ID                                                |
        +--------+--------------------------------------------------------------------------------------------------+
        |      1 | 123123123131221321jfdlasjfsdalfjdsalf;jdsaf;dssjf;sadjfads;fsdafasfafafdafdajfoieqwupqewrqweerqp |
        +--------+--------------------------------------------------------------------------------------------------+
        1 row selected.
```

##### 控制参数解释-FLOAT_FORMAT/DECIMAL_FORMAT/DATE_FORMAT/DATETIME_FORMAT/TIME_FORMAT
&emsp; FLOAT_FORMAT    控制浮点数字的显示格式，默认是%.7g
```
    SQL> _set DECIMAL_FORMAT %0.7g
    SQL> select abs(1.234567891234) from dual;
    +----------+
    | C1       |
    +----------+
    | 1.234568 |
    +----------+
    1 row selected.
    SQL> _set DECIMAL_FORMAT %0.10g
    SQL> select abs(1.234567891234) from dual;
    +-------------+
    | C1          |
    +-------------+
    | 1.234567891 |
    +-------------+
    1 row selected.
    类似的参数还有FLOAT_FORMAT
    
    SQL> _set DATE_FORMAT %Y%m%d
    SQL> select CAST('2000-02-02' AS DATE) from dual;
    +-------------+
    | C1          |
    +-------------+
    | 20000111    |
    +-------------+
    1 row selected.
    类似的参数还有DATETIME_FORMAT, TIME_FORMAT
```

##### 控制参数解释-CSV_HEADER/CSV_DELIMITER/CSV_QUOTECHAR
&emsp; CSV格式控制  
```
    CSV_HEADER        控制CSV输出中是否包括字段名称信息， 默认是OFF
    CSV_DELIMITER     CSV输出中字段的分隔符, 默认为逗号，即,  
    CSV_QUOTECHAR     CSV中字符类型字段的前后标记符号，默认为不标记

    SQL> select * from cat where rownum<10;
    ADATA_1000W,TABLE
    ADATA_100W,TABLE
    ADATA_10W,TABLE
    ADATA_1W,TABLE
    ADATA_2000W,TABLE
    ADATA_500W,TABLE
    BIN$p+HZrV/nKjTgU1ABqMCZxw==$0,TABLE
    BIN$p+HaveUdKjzgU1ABqMC4xg==$0,TABLE
    BIN$p+HbAAWeKlfgU1ABqMCSUg==$0,TABLE
    
    SQL> select 1.2+2.2 from dual
       > union
       > select 3+4 from dual;
    3.4
    7
```

##### 控制参数解释-SQL_EXECUTE
&emsp; SQL_EXECUTE  
```
    控制Jpype调用JDBC测试的时候，使用的具体行为方式。有两个可能的选项，分别是DIRECT和PREPARE
    对于DIRECT的行为类似：
        conn.createStatement().execute("sql ...")
    对于PREPARE的行为类似：
        PrepareStatement m_pstmt == conn.PrepareStatement(sql)
        m_pstmt.execute()
    在某些特定的情况下，这个参数将影响显示输出效果。
```


##### 控制参数解释-SQLCONN_RETRYTIMES
&emsp;  数据库连接尝试次数  
```
    默认是1，即数据库只尝试一次数据库连接，失败后即退回。
    可以调整到其他数值，来应用不稳定的数据库连接环境。
    每次重试中间会休息2秒
    
```

##### 控制参数-SQL_TIMEOUT，SCRIPT_TIMEOUT，API_TIMEOUT
&emsp; 脚本/语句超时控制
```
   程序实现了超时管理，默认的超时时间为无限制，即不做任何控制
   SCRIPT_TIMEOUT    脚本的最大运行时间，单位为秒，当脚本运行超过这个时间后，脚本将失败，程序将退出
   SQL_TIMEOUT       单个SQL语句的最大运行时间，单位为秒，当单个语句运行超过这个时间后，当前语句将失败，程序将继续
   API_TIMEOUT       单个API语句的最大运行时间，单位为秒，当单个语句运行超过这个时间后，当前语句将失败，程序将继续
   几个参数可以同时设置，同时生效，也可以根据需要设置其中一个
   
   注意（非常重要）： 
   当发生SQL超时中断后，程序将会启动调用数据库的cancel机制来回退当前运行状态，但不是每个数据库都能支持cancel机制
   所以，不要对超时退出后，数据库的连接状态有所预期，可能（非常可能）会导致后续的所有SQL执行失败

   说明：
   这里的超时判断不是一个精确时间，只是一个相对时间，程序存在检查点问题，实际中存在可能实际运行时间会略微超过此处控制时间的可能
   不要把精准的时间判断寄希望于这个TIMEOUT设置   
```

##### 控制参数  API_HTTPSVERIFY
```
   设置API默认的情况下请求是否验证远程的HTTPS签名。 可选值为ON或者OFF
   默认值为OFF，即不验证
   如果设置为ON，且没有合适的HTTPS证书信息，访问请求将失败
   
   需要注意：这里的配置只是一个默认值。
   如果在API空间内，用户用脚本设置了当前会话的这个参数(SET HTTPS_VERIFY ON|OFF)，则默认值将失效
   
```

##### 控制参数  API_HTTPPROXY
```
   设置API的代理地址。 
   合法有效的格式是： http://<ip address>:<port>
   例如： http://127.0.0.1:8000 

   默认值为空，即不需要代理
   
   需要注意：这里的配置只是一个默认值。
   如果在API空间内，用户用脚本设置了当前会话的这个参数(SET HTTPS_PROXY ....)，则默认值将失效
   
```

#### 让程序休息一会
```
(base) TestCli 
TestCli Release 0.0.32
SQL> _SLEEP 10
SQL> _DISCONNECT
Database disconnected.
这里的10指的是10秒，通过这个命令可以让程序暂停10秒钟。
Sleep的做法主要用在一些定期循环反复脚本的执行上
```

#### 执行主机的操作命令
```
(base) TestCli 
TestCli Release 0.0.32
SQL> _HOST date
2020年 10月 29日 星期四 11:24:34 CST
SQL> _DISCONNECT
Database disconnected.
这里的date是主机的命令，需要注意的是：在Windows和Linux上命令的不同，脚本可能因此无法跨平台执行
```

#### 从脚本中执行其他脚本
我们可以把语句保存在一个其他文件中，在当前控制台或当前脚本中进行调用  
语法格式为：
```
    _START <script1.sql>,<script2.sql> ...    <para1> <para2> ... <paran>
```
例如：
```
(base) TestCli 
TestCli Release 0.0.32
SQL> _START aa.api
SQL> ....
SQL> _DISCONNECT
这里将执行aa.api
如果有多个文件，可以依次填写，中间用逗号分隔, 如SQL> _START aa.api,bb.sql ....

para1, para2, paran 是子程序的运行参数。具体处理逻辑由子脚本处理.
```

#### 执行数据库测试
##### 连接数据库
在TestCli命令行里头，可以通过connect命令来连接到具体的数据库  
执行数据库的连接，前提是你的程序处于SQL的命名空间下
```
(base) TestCli 
TestCli Release 0.0.11
SQL> _connect user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> 
能够成功执行connect的前提是： 数据库驱动已经放置到jlib下，并且在conf中正确配置

如果已经在环境变量中指定了TestCli_CONNECTION_URL，连接可以简化为
(base) TestCli 
TestCli Release 0.0.11
SQL> _CONNECT user/pass
Database connected.
SQL> 

在数据库第一次连接后，第二次以及以后的连接可以不再输入连接字符串，程序会默认使用上一次已经使用过的连接字符串信息，比如：
(base) TestCli 
TestCli Release 0.0.32
SQL> _CONNECT user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> _CONNECT user2/pass2
Database connected.
SQL> 

常见数据库的连接方式示例：
H2:
    _CONNECT mem
ORACLE:
    _CONNECT username/password@jdbc:oracle:tcp://IP:Port/Service_Name
MYSQL:
    _CONNECT username/password@jdbc:mysql:tcp://IP:Port/Service_Name
PostgreSQL：
    _CONNECT username/password@jdbc:postgresql:tcp://IP:Port/Service_Name
SQLServer：
    _CONNECT username/password@jdbc:sqlserver:tcp://IP:Port/DatabaseName
TeraData：
    _CONNECT username/password@jdbc:teradata:tcp://IP/DatabaseName
Hive:
    _CONNECT hive/hive@jdbc:hive2://IP:Port/DatabaseName
ClickHouse:
    _CONNECT default/""@jdbc:clickhouse:tcp://IP:Port/DatabaseName
LinkoopDB:
    _CONNECT username/password@jdbc:linkoopdb:tcp://IP:Port/Service_Name
连接Oracle的Sysdba用户：
    _CONNECT username/password@jdbc:oracle:tcp://IP:Port/Service_Name?internal_logon=sysdba
```

##### 断开数据库连接
```
(base) TestCli 
TestCli Release 0.0.11
SQL> _connect user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> _disconnect
Database disconnected.
```
***

##### 执行SQL语句块
&emsp; SQL语句块的结束符为【/】，且【/】必须出现在具体一行语句的开头  比如：
```
    SQL> CREATE PROCEDURE PROC_TEST()
       > BEGIN
       >     bulabulabula....;
       > END;
       > /
    SQL> 
```
&emsp; 对于SQL语句块，TestCli将被等待语句结束符后把全部的SQL一起送给SQL引擎（不包括语句结束符）。

##### 执行单行SQL语句
&emsp; 单行SQL结束符为分号【 ；】 比如：
```
    SQL> CREATE TABLE TEST_TAB (ID INT);
    0 row affected.
    SQL> 
```

##### 单行SQL语句中包含多个语句
&emsp; 每个SQL语句的分隔符【 ；】 比如：
```
    SQL> DROP TABLE TEST_TAB IF EXISTS; CREATE TABLE TEST_TAB (ID INT);
    0 row affected.
    0 row affected.
    SQL>
```

##### 执行多行SQL语句
* 对于多行SQL语句的格式要求：  
   多行SQL语句是指不能在一行内写完，需要分成多行来写的SQL语句。  
   多行SQL语句的判断依据是： 语句用如下内容作为关键字开头
```
    'CREATE' | 'REPLACE' | 'ALTER'|  '+ | 'OR')+ ('PROCEDURE'|'FUNCTION'|'CLASS'|'TRIGGER'|'PACKAGE'

```

&emsp; 多行SQL结束符为分号【 ；】 比如：
```
    SQL> CREATE TABLE TEST_TAB
       > (
       >    ID   CHAR(20),
       >    COL1 CHAR(20)
       > );
    SQL> 
    对于多行SQL语句，同样也可以使用行首的【/】作为多行语句的结束符
```
&emsp; 对于SQL多行语句，TestCli将被等待语句结束符后把全部的SQL一起送给SQL引擎（包括可能的语句结束符分号）。


##### 其他SQL语句
* 其他SQL语句  
  不符合上述条件的，即不是语句块也不是多行语句的，则在输入或者脚本回车换行后结束当前语句。  
  结束后的语句会被立刻送到SQL引擎中执行。

##### SQL语句中的注释
  这些注释信息不会被送入到SQL引擎中，而是会被TestCli直接忽略。  

  注释的写法是： 【 ...SQL...   -- Comment 】  
  即单行中任何【--】标识符后的内容都被理解为行注释信息。  

```
    SQL> CREATE TABLE TEST_TAB
       > (
       >    ID   CHAR(20),          -- ID信息，这是是一个行注释
       >    COL1 CHAR(20)           -- 第一个CHAR字段，这也是一个行注释
       > );
    SQL> 
```

##### 在SQL中使用Hint信息
&emsp; &emsp; 在一些场景中，我们通过Hint隐含提示符来控制SQL的具体行为
```
    SQL> -- [Hint] Order
    SQL> Select ID,Name From TestTab;
    ....
    加入这个提示符后，TestCli将会把随后的SQL语句进行排序输出，原程序的输出顺序被忽略

    SQL> -- [Hint] LogFilter  .*Error.*
    SQL> Select ID,Name From TestTab;
    ....
    加入这个提示符后，TestCli将不再显示随后输出中任何包含Error字样的行
    .*Error.* 是一个正则表达式写法

    SQL> -- [Hint] LogFilter  ^!^Error.*$
    SQL> Select ID,Name From TestTab;
    ....
    加入这个提示符后，TestCli仅显示输出中包含Error字样的行

    SQL> -- [Hint] LogMask  Password:.*=>Password:******
    SQL> Select ID,Name From TestTab;
    ....
    加入这个提示符后，TestCli将把日志输出中所有符合Password:.*的内容替换成Password:*****

    SQL> -- [Hint] SQL_PREPARE
    SQL> Select ID,Name From TestTab;
    ....
    加入这个提示符后，随后的TestCli程序在执行的时候将首先解析SQL语句，随后再执行，
    这是默认的方式

    SQL> -- [Hint] SQL_DIRECT
    SQL> Select ID,Name From TestTab;
    ....
    加入这个提示符后，随后的语句在TestCli执行中将跃过解析(PrepareStatement)层面
    这不是默认方式，和之前的SQL_PREPARE相互斥的一个设置
    在某些情况下，有的特殊SQL语句不支持PREPARE，这是一个可以绕开问题的办法
    可以通过设置变量的方式来全局影响这个设置.
    SQL> _SET SQL_EXECUTE PREPARE|DIRECT

```

##### 数据库会话的切换和保存
通过_SESSION语句可以保存当前数据库会话，并切换到新的数据库会话上进行工作。  
如果需要的话，还可以通过SESSION的语句切换回之前保留的会话。

```
    _SESSION [SAVE|RELEASE|RESTOR|SAVEURL|SHOW] <Session Name> 
```
```
(base) TestCli 
TestCli Release 0.0.32
SQL> _CONNECT user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> _SESSION save sesssion1
Session saved.
# 这里会把当前会话信息保存到名字为session1的上下文中，session1为用户自定义的名字
# 注意：这里并不会断开程序的Session1连接，当Restore的时候也不会重新连接
SQL> _CONNECT user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名]
Database connected.
# 连接到第一个会话
SQL> _SESSION save sesssion2
Session saved.
# 这里会把当前会话信息保存到名字为session2的上下文中，session2为用户自定义的名字
# 注意：这里并不会断开程序的Session2连接，当Restore的时候也不会重新连接
SQL> _SESSION show
+---------------+-----------+-----------------------------------------------+
| Sesssion Name | User Name | URL                                           |
+---------------+-----------+-----------------------------------------------+
| session1      | xxxxx     | jdbc:xxxxx:xxx://xxx.xxx.xxx.xxx/xxxx         |
| session2      | yyyyy     | jdbc:yyyy:xxx://xxx.xxx.xxx.xxx/yyyyy         |         
+---------------+-----------+-----------------------------------------------+
# 显示当前保存的所有会话信息

SQL> _SESSION restore sesssion1
Session stored.
# 这里将恢复当前数据库连接为之前的会话1

SQL> _SESSION restore sesssion2
Session stored.
# 这里将恢复当前数据库连接为之前的会话2

SQL> _SESSION saveurl sesssion3
Session saved.
# 这里会把当前会话信息的URL保存到名字为session3的上下文中，session3为用户自定义的名字
# 注意：这里并不会保持程序的Session3连接，仅仅记录了URL信息，当Restore的时候程序会自动重新连接

SQL> _SESSION release sesssion3
Session released.
# 这里将释放之前保存的数据库连接，和针对具体一个连接的DisConnect类似
```
***


#### 执行API测试
在切换到API命名空间后，你就可以使用REST API的语法来书写测试脚本了。  
REST API的语法结构，这个文档里不会详细描述，具体可以参考网上资料。  
##### 请求的大致结果：
``` 
    Method Request-URI HTTP-Version
    Header-field: Header-value
    
    Request-Body
```
其中Method可以为POST，GET，或者其他任何合法的HTTP请求方法。  
Request-URI为请求的地址，地址可能包含请求参数。 如果请求参数列表很长，可以用多行表达。  
##### 单行表达的请求：
```
   ### GET请求，一行表达
   GET http://example.com:8080/api/get/html?firstname=John&lastname=Doe&planet=Tatooine&town=Freetown  HTTP/1.1
   
   ###
```
##### 多行表达的请求：
```
   ### GET请求，多行表达
    GET http://example.com:8080/api/get/html?  HTTP/1.1
        firstname=John&
        lastname=Doe&
        planet=Tatooine&
        town=Freetown   
   
   ###
```

##### 包含请求体的请求示例：
```
    ### POST请求，包含请求体
    POST http://example.com:8080/api/html/post HTTP/1.1
    Content-Type: application/json
    Cookie: key=first-value
    
    { "key" : "value", "list": [1, 2, 3] }
   ###
```

##### 从一个外部文件中加载消息体：
```
    ### POST请求，包含请求体
    POST http://example.com:8080/api/html/post HTTP/1.1
    Content-Type: application/json
    Cookie: key=first-value
    
    < input.json
   ###
```

##### 把执行结果输出到外部文件中(也可以使用>>来追加输出)：
```
    ### POST请求，包含请求体
    POST http://example.com:8080/api/html/post HTTP/1.1
    Content-Type: application/json
    Cookie: key=first-value

    { "key" : "value", "list": [1, 2, 3] }

    > output.json    
   ###
```

##### API多段提交：
``` 
    ### POST多段请求
    POST http://example.com/api/upload HTTP/1.1
    Content-Type: multipart/form-data; boundary=boundary
    
    --boundary
    Content-Disposition: form-data; name="first"; filename="input.txt"
    
    // The 'input.txt' file will be uploaded
    < ./input.txt
    
    --boundary
    Content-Disposition: form-data; name="second"; filename="input-second.txt"
    
    // A temporary 'input-second.txt' file with the 'Text' content will be created and uploaded
    Text
    --boundary
    Content-Disposition: form-data; name="third";
    
    // The 'input.txt' file contents will be sent as plain text.
    < ./input.txt --boundary--
   ###

```

##### HTTPS签名校验
```
   如果不设置，则是否需要验证的配置来源于程序的全局默认参数 API_HTTPSVERIFY
   
   如果设置，则以当前会话为准，忽略系统的默认配置
   SET HTTPS_VERIFY ON|OFF 
   
   ON    启用HTTPS签名验证
   OFF   关闭HTTPS签名验证
```

##### HTTP代理
```
   如果不设置，则HTTP地址来源于系统的全局默认参数 API_HTTPPROXY
   
   如果设置，则以当前会话为准，忽略系统的默认配置
   SET HTTP_PROXY http://<ip address>:<port> 
   
   例如：
   SET HTTP_PROXY http://127.0.0.1:8000
```

##### API会话的切换和保存
通过_SESSION语句可以保存当前API会话，并切换到新的API会话上进行工作。  
如果需要的话，还可以通过SESSION的语句切换回之前保留的会话。

```
   _SESSION SAVE <sessonName>
   _SESSION RELEASE
   _SESSION RESTORE <sessonName>
   _SESSION SHOW [<sessonName>]
   
   SAVE:
     保存当前会话，并给它起名
   
   RELEASE
     释放当前会话，并清空之前保存的内容
    
   RESTORE
     切换当前会话到指定的会话中

   SHOW
     显示所有会话信息，或者指定的会话信息     
 
```

##### 在API请求中使用Hint信息
&emsp; &emsp; 在一些场景中，我们通过Hint隐含提示符来控制SQL的具体行为
```    
    JsonFilter：
    如果返回结果是Json格式，则可以使用JsonFilter来过滤指定指定
    这里的Filter格式为glom格式，具体格式要求可以参考glom的格式写法
    
    我们这里假设http://127.0.0.1:8000/jsonfiltertest的正常返回结果是：
    {
        "content": {
            "data1": "data1XXXX",
            "data2": "data2XXXX",
            "data3": "data3XXXX",
            "data4": {
                "subdata4": "subdata4XXX"
            },
            "data5": [
                {
                    "data51": {
                        "subdata51": "subdata51XXX"
                    }
                },
                {
                    "data51": {
                        "subdata52": "subdata52XXX"
                    }
                }
            ]
        },
        "status": 200
    }
    
    API> -- [Hint] JsonFilter  data1
    API> ### 样例API
    API> GET http://127.0.0.1:8000/jsonfiltertest HTTP/1.1
    API> Content-Type: application/json
    API> 
    API> ###
    上述例子过滤结果集，并保留data1下来，过滤后的结果是：
    {
        "content": "data1XXXX",
        "status": 200
    }    
    
    API> -- [Hint] JsonFilter  data4.subdata4
    API> ### 样例API
       > GET http://127.0.0.1:8000/jsonfiltertest HTTP/1.1
       > Content-Type: application/json
       >
       > ###
    上述例子过滤结果集，并保留data1.data4下来，过滤后的结果是：
    {
        "content": "subdata4XXX",
        "status": 200
    }

    API> -- [Hint] JsonFilter  {"data1": "data1", "dataX": "data3"}
    API> ### 样例API
       > GET http://127.0.0.1:8000/jsonfiltertest HTTP/1.1
       > Content-Type: application/json
       >
       > ###
    上述例子过滤结果集，并重新构建结果集，重新构建后的结果是：
    {
        "content": {
            "data1": "data1XXXX",
            "dataX": "data3XXXX"
        },
        "status": 200
    }
    
    glom格式非常强大，这里不能列出所有的可能性，建议阅读glom文档
```

***
#### 脚本中使用变量：
测试脚本中支持使用变量，便于灵活的运行测试。  
变量的表示方法为：  {{var}}  
如： 如下的SQL语句中将查询的表名作为一个变量来表达：
```
   SQL>  Select * from {{TAB_NAME}}
```
以及，如下的API语句中将请求的内容用一个变量来表达：
```
   ### GET请求，多行表达
    GET http://{{SERVER_IP}}:8080/api/get/html?  HTTP/1.1
        firstname={{FIRST_NAME}}&
        lastname=Doe&
        planet=Tatooine&
        town=Freetown   
   
   ###
```
变量的来源可以为：  
1： 主机环境的环境变量， 如Linux下，通过export设置的环境变量信息  
2： 内置脚本中的变量名称， 如

```
   <%  SERVER_IP="127.0.0.1" %>
   <%  FIRST_NAME="John" %>
   ### GET请求，多行表达
   GET http://{{SERVER_IP}}:8080/api/get/html?  HTTP/1.1
       firstname={{FIRST_NAME}}&
       lastname=Doe&
       planet=Tatooine&
       town=Freetown   
   
   ###
```

***
#### 定义TestCli的初始化文件
```
    TestCli在执行的时候可以指定初始化文件，初始化文件会在真正的脚本执行之前被执行
    可以通过以下三种方式来定义TestCli的初始化文件：
    1： 通过在TestCli的命令行参数中执行，   
    $>  TestCli --profile xxxx
    2. 通过创建TestCli_HOME/profile/default文件，并在其中输入相关信息
    3. 通过修改程序的安装目录中对应文件来指定，即<PYTHON_PACKAGE>/TestCli/profile/default
    同时存在上述3类文件的时候，3类文件都会被执行。叠加执行的顺序是：3，2，1

    除非打开调试模式，否则初始化脚本的执行不会有任何输出日志，不会影响到日志校验等

```

#### 在脚本中使用简单的_IF/_ENDIF语句来进行条件判断
```
    TestCli支持在脚本中，添加简单的IF和ENDIF来进行逻辑判断
    在IF和ENDIF之间的语句只有条件满足，才会被执行。否则将被跳过
    目前还不支持多个IF的嵌套
    
    语法是：
       _IF {% <IF_EXPRESSION> %}
           -- 一些其他的语句
       _ENDIF
       
    其中： <IF_EXPRESSION>是标准的Python表达式，可以使用环境变量，或者引用内置的lastCommandResult
    
    以下是一个简单的IF，在满足aaa表中包含3条记录的情况下，将会执行删除操作    
    select * from aaa;
    _IF {% len(lastCommandResult["rows"]) == 3 %}
        Delete From AAA;
    _ENDIF
```

#### 在脚本中使用简单的_LOOP语句来进行循环处理
```
    TestCli支持在脚本中，添加简单的LOOP以及相对应的break，continue来进行循环执行    
    目前还不支持多个LOOP的嵌套

    语法是：
          单语句循环：
          _LOOP [<maxRetriedTimes>] UNTIL {% <LOOP_EXPRESSION> %} INTERVAL <intervalTime>

          多语句循环：
          _LOOP BEGIN UTIL {% <LOOP_EXPRESSION> %}
          _LOOP END
          _LOOP CONTINUE
          _LOOP BREAK
        ;
    
    单语句循环：
        用于反复执行在该LOOP语句之后的下一个语句，直到满足循环条件
        
        1： 即使循环条件天生不可能被满足，如语句 _LOOP UNTIL {% 1>2 %} INTERVAL 3， 后面随后的命令语句仍然会被执行一次
        2： 在循环过程中，除最后一次的屏幕输出外，过程中的信息并不会产生任何屏幕输出
        3： maxRetriedTimes 表示最多可以循环的次数， 整形， 可选项。 默认为不限制，即不达到条件不会退出
        4： intervalTime 表示每次循环判断的时间间隔，必选项，整形。
        5： 当语句结束后，最后输出的命令执行时间elapsed并不是最后一次执行的时间，而是包含了LOOP在内的整体时间
        6： <LOOP_EXPRESSION>是标准的Python表达式，可以使用环境变量，或者引用内置的lastCommandResult
        
    多语句循环：
        用于反复执行一段语句，直到满足循环条件
        
        1： 段落语句从_LOOP BEGIN开始，截止到_LOOP END结束
        2： 遇到_LOOP CONTINUE将会跳转当前语句_LOOP BEGIN开始的地方
        3:  遇到_LOOP BREAK将会中断当前循环，无论判断表达式是否满足
    
    以下是一个使用了单语句语句的典型例子：
    _LOOP 10 UNTIL {% len(lastCommandResult["rows"]) == 3 %}  INTERVAL 3;
    select * from test_singleloop order by 1;
    表达的意思是将每隔3秒检查一次test_singleloop表中的记录数是否已经达到3条，如果达到，退出循环
    即使总也不满足3条的条件，循环10次后也会退出
        
    以下是一个使用了多段语句的典型例子：
    > {% i=1 %}
    _LOOP BEGIN UNTIL {% i>=10 %}
         insert into aaa values(10);
         select * from aaa;
         _IF {% len(lastCommandResult["rows"]) == 3 %}
             _LOOP BREAK
         _ENDIF
         > {% i=i+1 %}
    _LOOP END;
    上述的例子中最多循环10次，10次后由于判断表达式不满足，而会中断循环
    在10次循环过程中，如果发现aaa表中的记录中已经达到3条，则立即终止循环，不再继续
```
***
#### 在脚本中使用ASSERT语句来判断运行结果
使用Assert可以判断测试运行的结果，结果作为测试运行的结论
```
   _ASSERT {% <python表达式> %} [, <AssertName>]   
```
上面语法中的python表达式是任何合法的python表达式。  
以下是一个实际使用的例子
``` 
    (base) C:\>testcli
    TestCli Release 0.0.9
    SQL> _connect /mem
    Database connected.
    SQL> create table aaa (num int);
    0 row affected.
    SQL> insert into aaa values(10);
    1 row affected.
    SQL> select * from aaa;
    +--------+-----+
    |   ##   | NUM |
    +--------+-----+
    |      1 |  10 |
    +--------+-----+
    1 row selected.
    SQL> _assert {% lastCommandResult["rows"][0][0] == 10 %}
    Assert successful.
    SQL> _assert {% lastCommandResult["rows"][0][0] == 11 %}, test1
    Assert [test1] fail.    
```
这里用ASSERT语句来判断上一个结果集返回的第一行、第一列是否为10。
如果是，返回成功，否则返回失败。  
AssertName是Assert具体的名字，可以为任何字符串，用在这里可以方便最后的日志输出和统计。  
注意： 这里的python表达式必须是一个非赋值表达式，即只能做判断语句，无法对内容发生改变。  
以下的python表达式用在Assert语句中是不合法的：
```
    SQL> _assert {% x = 11 %}, test1
```
上述错误的例子中定义了一个新的变量x，这违反了python表达式必须是非赋值表达式的限制。  

####  在脚本中嵌入python语法
为了方便测试脚本的扩展，testcli支持在测试脚本中嵌入python语法的写法。
```
> {% 
<Python单行或者多行语句> 
%}

如果内容少，也可以将python语句写在一行，类似> {% <Python单行或者多行语句> %}
```
以下是使用的例子：
```
> {% 
import time
start = time.time() 
%}

do some script....

> {% 
end = time.time() 
%}

_assert {% end - start > 300 %}
```
上述的语句中两次用python内嵌脚本获取了系统当前的时间，并最后用时间差判断这一段脚本执行是否超过了300秒。  
理论上，我们用这种内嵌脚本的方式支持所有可能的python语法。  
但是在实际的应用中，如果业务的逻辑比较复杂，建议将业务逻辑代码写成独立的Python文件，并通过脚本（_LOAD SCRIPT)或插件(_LOAD PLUGIN)的方式来导入。  
通过插件导入的方式，将使得程序变得更容易复用，而且可读性有所提高。  

需要注意的是： 在一个测试脚本运行的过程中，所有的python内嵌语法都拥有共同的变量空间。   
即如何保证变量空间的不冲突是写业务逻辑代码的时候需要保证的。    

为了更方便来满足业务的判断，我们内置了一些系统变量，这些系统变量在使用的过程中不需要业务层面重新定义，可以直接拿来使用。  

##### lastCommandResult
用来标记上一次语句执行的结果。  
如果需要保留上一次的语句执行结果，则在执行下一个语句前必须对该变量进行深度复制。（直接赋值会导致Python中的引用问题，结果将偏离预期）
复制的方法是：
```
  > {%
  import copy
  x = copy.copy(lastCommandResult) 
  %}
```
执行完上述语句后，就可以在随后的脚本中使用x来做进一步的判断的处理。  
对于正常的SQL语法，lastCommandResult的结果是一个数据字典，其内容为：  
```
   {
       "rows": [(Cell1-1,Cell1-2,),(Cell2-1,Cell2-2),],
       "headers": [列名1，列名2,],
       "elapsed": <命令执行的时间，如1.35，单位为秒>,
       "status": <语句的最后命令行状态输出>,
       "errorCode": 0
   }
```
对于一个错误的SQL写法，lastCommandResult的结果是一个数据字典，其内容为：
```
   {
       "errorCode": 1,
       "rows": [],
       "headers": [],
       "elapsed": <命令执行的时间，如1.35，单位为秒>,
       "status": <语句的最后命令行状态输出, 这里指错误消息>,
   }
```
对于一个正确的API调用，lastCommandResult的结果是一个数据字典，其内容为：
``` 
   {
       "content": <HTTP响应正文>,
       "elapsed": <命令执行的时间，如1.35，单位为秒>,
       "status": <HTTP的响应状态，即HTTP.RESP.STATUS>,
       "errorCode": 0
   }
```
对于一个错误的API调用，lastCommandResult的结果是一个数据字典，其内容为：
``` 
   {
       "message": <请求错误消息>,
       "errorCode": 1
   }
```

##### sessionContext
定义当前会话的上下文信息。  
sessionContext是一个字典结果。  
1： 可以通过sessionContext获得当前会话的数据库连接信息；  
2： 可以通过sessionContext向当前会话传递结果，并作为当前Python内嵌语句的返回结果；

```
    -- 获得当前数据库的数据库连接
    > {%
        dbConn = sessionContext["dbConn"]
        ...
    %}
```
```
    -- 从内嵌语法中返回
    > {%
        # type可以为result或者error
        #     如果为result，则应填写相应的title, rows, headers, columnTypes
        #     如果为result，则应填写相应的message
        sessionContext["type"] = "result"
        sessionContext["status"] = "这是从Python的内置语法中返回，可以为None，即不填写"
        sessionContext["title"] = "以下是返回标题，可以为None，即不填写"
        sessionContext["rows"] = [(10,15), (20,25)]
        sessionContext["headers"] = ['COL1','COL2',]
    %}
    -- 返回的样子:
    以下是返回标题，可以为None，即不填写
    +--------+------+------+
    |   ##   | COL1 | COL2 |
    +--------+------+------+
    |      1 | 10   | 15   |
    |      2 | 20   | 25   |
    +--------+------+------+
    这是从Python的内置语法中返回，可以为None，即不填写
```

##### argv
通过argv，我们可以在调用start命令的时候传递命令运行的参数。
```
    -- 这里testsqlstartchild.sql是一个脚本，里头将打印传递参数到控制台 
    testsqlstartchild.sql：
      {%
      sessionContext["status"] = "argv=" + str(argv)
      %}
    
    -- 在主程序中调用testsqlstartchild.sql，并传递参数3和5，就可以得到如下的结果
    SQL> _start testsqlstartchild.sql 3 5
    SQL> > {%
       > sessionContext["status"] = "argv=" + str(argv)
       > %}
    argv=['3', '5']    
```
***
#### 用TestCli来产生测试数据文件
为了方便测试，有时候我们要生成大量的测试数据，生成这些测试数据的要求是：  
1. 能够按照规则进行随机生成  
2. 能够快速的生成数据
```
  _DATA SET SEEDFILE DIR <种子文件的路径>;
  
  _DATA SET HDFSUSER <HDFS连接用户>;
  
  _DATA CREATE MEM|FS|HDFS FILE <目标文件路径> 
  (
     <列表达式..>
     <列表达式..>
  )
  [ROWS <计划生成的记录行数>]
  
  HDFS路径描述方法:
    hdfs://<hdfs服务器IP>:<hdfs服务器端口>/<hdfs文件路径>

  _DATA CONVERT MEM|FS|HDFS FILE <源文件路径> TO MEM|FS|HDFS FILE <目标文件路径>  
```

```
    如果参数中提供了ROWS：
        这里将把列表达式中内容理解为一行内容，其中的换行符在处理过程中被去掉
    如果参数没有提供了ROWS：
        这里将把列表达式内中的内容理解为多行内容

   列表达式的表达可以为：
     {identity(start_number)}                  表示一个自增字段，起始数字为start_number
                                               如果一行内有多个identity，他们将分别自增
     {identity_timestamp(start_time,fmt,step)} 表示一个自增的时间戳
                                               起始数字为start_time，格式位fmt（可以省略，默认是%Y-%m-%d %H:%M:%S)，
                                               每次自增长度为Step， Step的单位可以是s,ms,us (默认为ms)
                                               s: 秒 ;  ms: 毫秒； us: 微妙
                                               如果一行内有多个identity，他们将分别自增
     {random_ascii_letters(length)}            表示一个随机的ascii字符串，可能大写，可能小写，最大长度为length
     {random_ascii_lowercase(length)}          表示一个随机的ascii字符串，只能是大写字母，最大长度为length
     {random_ascii_uppercase(length)}          表示一个随机的ascii字符串，只能是小写字母，最大长度为length
     {random_digits(length)}                   表示一个随机的数字，可能数字，最大长度为length
     {random_ascii_letters_and_digits(length)} 表示一个随机的ascii字符串，可能大写，可能小写，可能数字，最大长度为length
     {random_date(start, end, frmt)}           表示一个随机的日期， 日期区间为 start到end，日期格式为frmt
                                               frmt可以不提供，默认为%Y-%m-%d
     {random_time(start, end, frmt)}           表示一个随机的时间， 时间区间为 start到end，时间格式为frmt
                                               frmt可以不提供，默认为%H:%M:%S
     {random_timestamp(start, end, frmt)}      表示一个随机的时间戳， 时间区间为 start到end，日期格式为frmt
                                               frmt可以不提供，默认为%Y-%m-%d %H:%M:%S
     {random_boolean())                        表示一个随机的Boolean，可能为0，也可能为1
     {current_unixtimestamp()}                 unix时间戳格式表示的系统当前时间
     {column_name: macro()}                    一个带有列名的宏定义，其中macro()的写法参考前面的写法
     {value(:column_name)}                     根据列名，引用之前的一个定义
     {column_name: value(expr)}                带有列名的一个定义                             
     {random_from_seed(seedname,length)}                  表示从seed文件中随机选取一个内容，并且最大长度限制在length, 此时seedname不要引号
     {random_from_seed(seedname,start_pos, length)}       表示从seed文件中随机选取一个内容，内容从start_pos开始(第一个位置为0)， 并且最大长度限制在length, 此时seedname不要引号
     使用random_from_seed需要用到seed文件，必须提前准备到$TestCli_HOME/data下，用来后续的随机函数  

   例子：
   SQL> _DATA CREATE FS FILE abc.txt
      > (
      > {identity(10)},'{random_ascii_letters(5)}','{random_ascii_lowercase(3)}'
      > ) ROWS 3;
    会在当前的文件目录下创建一个名字为abc.txt的文本文件，其中的内容为：
    10,'UmMwr','bam'
    11,'HWgiR','dmh'
    12,'Skxag','mlj'
```
***
#### 加载附加的命令行映射文件
这里的使用方法和在testcli命令中使用--commandmapping的参数效果是一样的。  
这里将对mapping文件的规则进行详细的解释和说明。  
正如前面介绍的， 映射文件的设计目的是为了解决一个典型的测试场景。即：有的测试脚本需要反复多次的运行，其区别仅仅是部分参数信息的不同。
```
   _LOAD MAP <file location of command mapping file>   
```
以下是一个实际使用的例子：
```
# aa.map以下是一个典型的映射文件, 这里我们将TAB映射为了TAB1
(base) C:\> type testsqlmapping.map
#..*:
TABA=>TAB1
#.
```
```
(base) C:\> testcli
TestCli Release 0.0.8
SQL> --在脚本中直接加载映射文件
SQL> _load map testsqlmapping.map
Mapping file loaded.
SQL> _connect /mem
Database connected.
SQL> create table {{TABA}}
   > (
   >     id  int
   > );
REWROTED SQL> Your SQL has been changed to:
REWROTED    > create table TAB1
REWROTED    > (
REWROTED    >     id  int
REWROTED    > )
0 row affected.
SQL>
SQL> insert into {{TABA}} values(3);
REWROTED SQL> Your SQL has been changed to:
REWROTED    > insert into TAB1 values(3)
1 row affected.
Disconnected.
```
以下对testsqlmapping.map的格式进行详细的说明：  
映射文件的查找顺序：  
1. 首先会判断映射文件是否是一个基于绝对路径定义的文件，如果是，则以绝对路径定义的文件为准；    
2. 如果绝对路径下文件无法找到，则以当前执行脚本（对于控制台输入，以程序当前所在工作目录）的上下文目录去相对查找；  

映射文件的格式要求：  
```
1  #..*:
2  TABA=>TAB1
3  TABB=>TAB2
4  M(.*)=>N\1
5  #.
```
上述内容的前面数字1，2，3，4不是文件真实内容，只是为了后面便于表达添加的。  
1. 行1：  
    这里定义的是参与匹配的脚本文件名，以#.开头，以:结束，这里可以根据需要写出绝对文件名称，也可以按照正则表达式的写法写出正则匹配表达。  
    当写出的一个正则匹配表达式的时候： 如果当前执行的脚本文件名和这里定义的内容符合正则匹配条件，则当前配置段生效  
2. 行2,行3,行4：  
   这里定义的是正则替换规则, 用Pattern=>Target的方式来描述。
   即用=>分割，脚本中出现的符合Pattern定义的内容，将会替换为Target表达的内容  
   在上述定义的例子中，我们会把脚本中的TABA替换成TAB1，会把脚本中的TABB替换成TAB2
   还会根据正式表达式规则完成从M123到N123的替换，类似M456到N456.
3. 行5  
   当前配置段落终止

每一个映射文件中，可以循环反复多个这样的类似配置，每一个配置段都会生效。  
如果一个文件规则或者替换规则多次出现定义，则会发生多次匹配的现象。  

***
#### 加载附加的外挂脚本
为了让测试框架能够支持更多的扩展，testcli支持你将自己写好的Python程序作为一个脚本的方式放入到系统中。脚本中可以包含自己的函数和模块。  
虽然这是一个可能解决问题的近乎外能良药，但是这么做会导致一定的测试脚本可读性下降。需要你在使用的时候小心谨慎。  
```
   _LOAD SCRIPT <脚本文件的位置>   
```
这里的脚本文件是一个有效的Python文件，python文件可能包含有类的定义，全局函数的定义等等。  
以下是一个简单脚本文件的例子：  
```
(base) C:\>type testscript.py
class cc:
    def welcome(self, message: str):
        if self:
            pass
        return 'thx ' + message


def fun(b):
    return "b" + str(b)
```
通过在testcli中执行LOAD SCRIPT命令可以完成对插件文件的加载
```
(base) C:\>testcli
TestCli Release 0.0.8
SQL> _load script testscript.py
Script module [cc] loaded successful.
Script function [fun] loaded successful.
Script file loaded successful.
```
加载成功后，我们就可以直接在测试脚本中使用插件文件中定义的内容，以下是一个例子：
```
(base) C:\>testcli
-- 接上面的测试命令
SQL> _connect /mem
Database connected.
SQL> create table aaa (id int);
0 row affected.
SQL> insert into aaa values(10);
1 row affected.
SQL> select * from aaa;
+--------+----+
|   ##   | ID |
+--------+----+
|      1 | 10 |
+--------+----+
1 row selected.
SQL>
SQL> > {%
   > import copy
   > x=copy.copy(lastCommandResult)
   > %}
SQL>
SQL> _assert {% x["rows"][0][0]==10 %};
Assert successful.
SQL>
SQL> > {%
   > sessionContext["status"] = fun(x["rows"][0][0])
   > %}
b10
SQL>
SQL> > {%
   > xx = cc()
   > sessionContext["status"] = xx.welcome("Boy.")
   > %}
thx Boy.
SQL> _exit
```
具体对于SessionConext的用法解释请参考文档的其他章节。  
上面的例子中，我们在内置脚本中执行了插件中定义的类和方法，并完成了数据的处理和返回。  

***
#### 加载附加的外挂命令实现
为了让测试框架能够支持更多的扩展，testcli支持你将自己来实现相关的命令。前提是你遵循相关的写法规则。  
```
   _LOAD PLUGIN <插件文件的位置>   
```

这里的插件文件是一个有效的Python文件，包含特定的变量和函数入口。  
以下是一个简单插件文件的例子（石头，剪刀，布。 我和电脑玩了几次，发现我总是输掉。）：  
```
(base) C:\>type testplugin.py
# -*- coding: utf-8 -*-
import random

COMMAND = "GAME"

def cmdEntry(cmdArgs: list):
    if len(cmdArgs) != 1:
        # 至少有一个选择，剪刀，石头，布
        yield {
            "type": "error",
            "message": "Please enter your choise [rock|paper|scissor].",
        }
        return

    computer = random.choice(["rock", "paper", "scissor"])
    user = str(cmdArgs[0])

    # 必须是剪刀，石头，布的一个
    if user.lower() not in ["rock", "paper", "scissor"]:
        yield {
            "type": "error",
            "message": "Please enter correct choise [rock|paper|scissor].",
        }
        return

    message = "opponent choice : {}".format(computer) + "\n"
    if computer == user:
        message = message + "Tie!"
    elif computer == "paper" and user == "scissor":
        message = message + "{0} cuts {1}. Congrats You win!".format(user, computer)
    elif computer == "paper" and user == "rock":
        message = message + "{1} covers {0}. Oops You lost!".format(user, computer)
    elif computer == "scissor" and user == "paper":
        message = message + "{1} cuts {0}. Oops You lost!".format(user, computer)
    elif computer == "scissor" and user == "rock":
        message = message + "{0} smashes {1}. Congrats You win!".format(user, computer)
    elif computer == "rock" and user == "scissor":
        message = message + "{1} smashes {0}. Oops You lost!".format(user, computer)
    elif computer == "rock" and user == "paper":
        message = message + "{0} covers {1}. Congrats You win!".format(user, computer)
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": message
    }

```
通过在testcli中执行LOAD PLUGIN命令可以完成对插件文件的加载和运行。
```
(base) C:\>testcli
TestCli Release 0.0.8
Plugin [GAME] loaded successful.
SQL> _GAME rock;
opponent choice : scissor
rock smashes scissor. Congrats You win!
```

扩展文件书写要求：
* 插件的名称： 必须在插件文件中出现COMMAND的字符串变量定义，且字符串内容和内置关键字不能冲突。
* 插件的命令执行入口： 必须在插件文件中定义cmdEntry函数，其接受List类型的参数列表，且输出结果
* 对于正确的结果，输出格式要求为：
```
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
```
* 对于错误的结果，输出格式要求为：
```
    {
        "type":     "error"
        "message":  错误消息
    }
```

***
#### 加载数据库驱动
TestCli会默认加载所有配置在conf/testcli.ini中的JDBC驱动  
你也可以在启动后手工加载额外的驱动，或者更改已经加载的配置。
```
    _LOAD JDBCDRIVER
        {
            NAME = <给每一个驱动起一个唯一的名字> |
            CLASS = <数据驱动类的名称> |
            FILE = <数据驱动文件的位置> |
            URL = <数据库驱动连接字符串> |
            PROPS = <数据库连接中的额外属性信息>
        }
```
1. 驱动类的名称  
   是指Java的类名称，如com.mysql.jdbc等
2. 驱动文件的位置  
   你可以提供绝对路径，也可以提供基于脚本路径的相对路径  
   如果某一个数据连接需要多个Jar包，则可以提供多个文件名称，文件中中间用逗号分割  
   如 _LOAD JDBCDRIVER NAME=ORACLE FILE='ojdbc8.jar,xmldb.jar'  
3. URL数据库驱动连接字符串  
   对于一些动态变化的连接字符串，可以用变量的方式来表示  
   目前支持的变量有：  
    ```
       ${driverType}         表示驱动的类型，如thin,oci  
       ${host}               表示连接主机，如192.168.2.1  
       ${port}               表示连接端口，如1521  
       ${service}            表示数据服务名，如orcl  
       例子：_LOAD JDBCDRIVER NAME=ORACLE URL="jdbc:oracle:thin:@${host}:${port}/${service}"
    ```
4. PROPS为额外的数据参数,描述格式为：
    ```
   <optionName1>:<optionValue1>[,<optionName2>:<optionValue2>]+
   ```
   例子：_LOAD JDBCDRIVER NAME=ORACLE PROPS="socket_timeout:360000000"
5. 如果不提供额外的参数，则会显示当前的数据库驱动信息
   如: 
    ```
    (base) C:\>testcli
    SQL> _LOAD JDBCDRIVER
     Current Drivers:
    +--------+------------+----------------------------------------------+------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-------------+
    |   ##   |  Database  |                  ClassName                   |                                                  FileName                                                  |                                                              JDBCURL                                                               |   JDBCProp  |
    +--------+------------+----------------------------------------------+------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-------------+
    ...
    |     13 | h2mem      | org.h2.Driver                                | ['C:\\Anaconda3\\lib\\site-packages\\robotslacker_testcli-0.0.8-py3.9.egg\\testcli\\jlib\\h2-1.4.200.jar'] | jdbc:h2:mem:                                                                                                                       | <null>      |
    ...
    ```

***
#### 程序的并发和后台执行
TestCli被设计为支持并发执行脚本，支持后台执行脚本。    
为了支持后台操作，我们这里有一系列的语句，他们是：    
1：  Create         创建后台任务      
2：  set            设置JOB相关参数    
3：  show           显示当前已经提交的后台任务，以及他们的运行状态    
4：  start          开始运行后台作业    
5：  abort          放弃正在执行的JOB，当前正在运行的SQL将被强制中断    
6：  shutdown       停止当前正在执行的JOB，但等待当前SQL正常结束    
7：  waitJob        等待作业队列完成相关工作    
8：  timer          相关Worker进程等待聚合点
```
   _JOB MANAGER [ON | OOF]
   _JOB WAIT <JOB的名字 | ALL> { <JOB选项名称>=<JOB选项值>}
   _JOB SHOW <JOB的名字 | ALL> 
   _JOB START <JOB的名字 | ALL>   
   _JOB ABORT <JOB的名字 | ALL> 
   _JOB SHUTDOWN <JOB的名字 | ALL>   
   _JOB CREATE <JOB的名字> { <JOB选项名称>=<JOB选项值>}
   _JOB SET <JOB的名字> { <JOB选项名称>=<JOB选项值>}
   _JOB REGISTER WORKER TO <JOB名称>
   _JOB DEREGISTER WORKER
```
##### 创建后台任务脚本
在很多时候，我们需要TestCli来帮我们来运行数据库脚本，但是又不想等待脚本的运行结束。    
create可以有多个参数：      
参数1：     JOB的名称  
参数2-..:   JOB的各种参数，要求成对出现 ParameterName  ParameterValue
```
SQL> _JOB create jobtest;
JOB [jobtest] create successful.
SQL> _JOB create jobtest2 loop=4;
JOB [jobtest2] create successful.
SQL> _JOB create jobtest3 loop=4 parallel=2;
JOB [jobtest3] create successful.

```
2:  设置JOB的相关参数    
通过set，我们可以JOB的具体参数。 支持的参数有：
```  
script                   ：  必选参数。后台作业的脚本名称。可以用绝对路径写或者当前目录的相对路径    
parallel                 ：  可选参数。后台作业并发度，即同时可以有几个作业在运行该脚本。默认为1  
loop                     ：  可选参数。一共要循环完成的次数，默认为1    
timeout                  ：  可选参数。后台作业的超时限制，单位为秒，默认为0，即不限制
                             若设置为非零数，则在达到指定的时间后，作业会被强行终止，不再继续下去
starter_maxprocess       ：  为减少首次启动的负载压力。每次启动作业时，单个批次最大启动多少个并行作业
                             只在作业首次启动的时候，这个参数有意义。
                             默认是9999，即完全不做限制
                             例如： parallel 设置为10，starter_maxprocess为2，
                               则：以starter_interval为间隔，每次2个启动作业，一直到满足parallel要求 
starter_interval         ：  为减少首次启动的负载压力。每次启动作业时，单个批次的间隔时间，默认是0，即不等待
think_time               ：  每一次作业完成后，启动下一个作业中间需要的时间间隔，默认是0，即不等待
blowout_threshold_count  ：  完全失败阈值，若失败次数已经达到该次数，认为后续作业已经没必要运行。默认是0，即不限制   
tag                      ：  程序组标识，所有具有相同tag的Worker进程在判断聚合点的时候将保持同步
例子： 
SQL> _JOB set jobtest script=bb.sql parallel=2;
JOB [jobtest] set successful.
SQL> _JOB set jobtest script=bb.sql loop 4;
JOB [jobtest] set successful.
SQL> _JOB set jobtest script=bb.sql;
JOB [jobtest] set successful.
SQL>
```

##### 查看后台任务脚本的运行情况
通过show可以查看我们之前提交情况，脚本的运行情况，运行的开始时间，运行的结束时间，当前正在运行的SQL等。
```
SQL> -- 查看JOB整体情况
SQL> _JOB show all;
+----------+-----------+-------------+-------------+---------------+---------------------+------------+----------+
| job_name | status    | active_jobs | failed_jobs | finished_jobs | submit_time         | start_time | end_time |
+----------+-----------+-------------+-------------+---------------+---------------------+------------+----------+
| jobtest  | Submitted | 0           | 0           | 0             | 2020-12-02 11:00:41 | None       | None     |
+----------+-----------+-------------+-------------+---------------+---------------------+------------+----------+
Total 1 Jobs.
这里可以看到目前1个脚本已经提交.

SQL> -- 查看JOB具体情况 
SQL> _JOB show jobtest;
JOB_Name = [jobtest     ]; ID = [   3]; Status = [Submitted          ]
ActiveJobs/FailedJobs/FinishedJobs: [         0/         0/         0]
Submit Time: [2020-12-02 11:00:41                                    ]
Start Time : [None                ] ; End Time: [None                ]
Script              : [bb.sql                                        ]
Script Full FileName: [None                                          ]
Parallel: [         2]; Loop: [         4]; Starter: [    9999/    0s]
Think time: [         0]; Timeout: [         0]; Elapsed: [      0.00]
Blowout Threshold Count: [                                       9999]
Error Message : [None                                                ]
Detail Tasks:
+----------+----------+--------------------+--------------------+
|Task-ID   |PID       |Start_Time          |End_Time            |
+----------+----------+--------------------+--------------------+
这里可以看到具体对于JOB名称为jobtst的任务的详细情况
```
##### 如何启动后台任务脚本
通过start的方式，我可以启动全部的后台任务或者只启动部分后台任务
```
SQL> _JOB jobmanager on
SQL> _JOB start all;
1 Job Started.
这里会将你之前提交的所有后台脚本都一次性的启动起来
SQL> _JOB start jobtest;
1 Job Started.
这里只会启动JOB名称为jobtest的后台任务
随后，再次通过show来查看信息，可以注意到相关已经启动
```

##### 如何停止后台任务脚本
在脚本运行过程中，你可以用shutdown来停止某个某个任务或者全部任务，
```
SQL> _JOB shutdown all;
Total [1] job shutdowned.
这里会将当前运行的所有后台脚本都停止下来
SQL> _JOB shutdown jobtst;
Total [1] job shutdowned.
注意： shutdown并不会真的终止你当前正在运行的作业，但是在这个作业之后的所有作业不再执行，要求循环执行的脚本也不再循环。
      只有在子任务完成当前作业后，shutdownjob才能完成。
      这个意思是说，如果你有一个比较大的长SQL作业，shutdownjob并不能很快的终止任务运行。
```
##### 如何强行停止后台任务脚本
在脚本运行过程中，你可以用abort来强行停止某个某个任务或者全部任务，
```
SQL> _JOB abort all;
Total [1] job aborted.
这里会将当前运行的所有后台脚本都停止下来
SQL> _JOB abort jobtst;
Total [1] job aborted.
```
##### 等待后台任务脚本运行结束
在脚本运行过程中，你可以用wait来等待后台脚本的运行结束
```
SQL> _JOB wait all;
All jobs [all] finished.
SQL> _JOB wait jobtest;
All jobs [jobtest] finished.
waitjob不会退出，而是会一直等待相关脚本结束后再退出
```
wait 可以指定timeout参数，如果指定，则wait最多等待timeout的时候，随后退出。
```
SQL> _job wait all TIMEOUT=3;
Unexpected internal error: Job wait terminated. Timeout [3]
```

##### 如何让若干的Worker应用程序保持聚合点
主调度程序脚本：
```
SQL> _JOB jobmanager on
SQL> _JOB create mytest loop=2 parallel=2 script=slave1.sql tag=group1;
SQL> _JOB create mytest2 loop=2 parallel=2 script=slave2.sql tag=group1;
SQL> _JOB start mytest;
SQL> _JOB start mytest2;
SQL> _JOB wait all;
```

Worker应用程序脚本(slave1.sql, slave2.sql)：
```
-- 两个Worker程序(slave1.sql,slave2.sql)将会同时结束all_slave_started的聚合点
SQL> _JOB timer all_slave_started;
SQL> do some sql
SQL> _JOB timer slave_point1;
SQL> do some sql
SQL> _JOB timer slave_finished;
```

#### 脚本中使用COMPARE命令来比较文件差异性
通常我们用比较的方式来比对一个执行结果和预期执行结果的差异性。来判断当前测试是否正确执行。
```
   _COMPARE <需要比对的文件名> <比对参考文件> {MASK | NOMASK | CASE | NOCASE | IGBLANK | NOIGBLANK | TRIM | NOTRIM}
   _COMPARE SKIPLINE <比对过程中需要忽略的行信息，可以用正则表达式来描述>
   _COMPARE NOSKIPLINE <和上述语句相对应，来取消需要忽略的行信息>
   _COMPARE MASKLINE <比对过程中需要进行掩码的行信息，可以用正则表达式来描述>=><符合条件的内容进行掩码后的内容>
   _COMPARE NOMASKLINE <和上述语句相对应，来取消需要掩码的行信息>
   _COMPARE RESET
   _COMPARE SET {MASK | NOMASK | CASE | NOCASE | IGBLANK | NOIGBLANK | TRIM | NOTRIM}
   _COMPARE SET OUTPUT { CONSOLE | DIFFFILE }
   _COMPARE SET ALGORITHM [LCS | MYERS]
   _COMPARE SET WORK ENCODING <需要比对文件的字符集信息，默认为UTF-8>
   _COMPARE SET REFERENCE ENCODING <需要比对文件的字符集信息，默认为UTF-8>

   TODO:
      1. 支持 _COMPARE SET OUTPUT HTMLFILE
      2. COMPARE OUTPUT中的DIFFFILE，包含文件头信息，以更好的辅助判断
```
1. 文件比对选项
   1. MASK 比对过程中启用正则表达式进行比对。默认是： 不启动
   2. NOMASK 比对过程中不启用正则表达式进行比对
   3. CASE 比对过程中忽略文本大小写差异。默认是：不忽略
   4. CASE 比对过程中不忽略文本大小写差异。
   5. IGBLANK 比对过程中忽略空行信息，即如果两个文件只有空行差异，则认为内容是完全相同的。默认是不忽略
   6. IGBLANK 比对过程中不忽略空行信息
   7. TRIM 比对过程中对文件每一行的前后进行截断操作，即去掉行前和行尾的空格后再进行比对。默认是不截断
   8. TRIM 比对过程中对文件每一行的前后不进行截断操作
   9. 如果COMPARE语句中指定了选项，则以指定选项为准，否则以系统SET设置的内容为准
   10. 一个语句中可以使用多个比对选项。如: _COMPARE aa.txt bb.txt MASK CASE
   11. 通过_COMPARE RESET可以重置所有的比较选项配置
2. 文件比对算法
   1. LCS 是Longest Common Subsequence的缩写,即最长公共子序列。 在文件比较大的时候，运行效率指数下降。
   2. MYERS 是Myers Diff Algorithm，即差分算法。算法复杂度为O(NlgN)，线性增长，运行效率很高，尤其在文件大时候优势明显。
   3. 目前程序是默认是MYERS
3. MASKLINE 在比对过程中对特定的信息进行掩码
   1. MASKLINE会显著减低程序运行效率
   2. 如果有多个需要进行掩码的内容，可以用多个_COMPARE MASKLINE来表述。如：
      ```
      _COMPARE MASKLINE  aa=>bb;
      _COMPARE MASKLINE  cc=>dd;
      ```
      上述设置将在比对过程中前置的把所有aa替换成bb，把cc替换成dd
   3. 通过NOMASKLINE可以取消之前的MASKLINE设置
   4. 这里的匹配内容为部分匹配，即只要行中包含符合条件的信息，则COMPARE规则符合
   5. 如果期望完全匹配，则需要配置类似如下 _COMPARE MASKLINE ^aa$^=>***
4. SKIPLINE 在比对过程中忽略特定的行信息
   1. 如果有多个需要进行忽略的内容，可以用多个_COMPARE SKIPLINE来表述
   2. SKIPLINE默认是完全匹配规则，即_COMPARE SKIPLINE aa表示忽略掉行信息为aa的内容，类似aab的内容则不会忽略
   3. 如果希望模拟忽略，则可以用正则表达来描述，如_COMPARE SKIPLINE aa.*
5. OUTPUT 将比对的结果输出到控制台、一个DIFF文件(文本文件）、一个DIFF文件(HTML文件)中
   1. 也可以即输出到控制台，也输出到DIFF文本文件中。设置方法： _COMPARE SET OUTPUT CONSOLE DIFFFILE;

#### 脚本中使用SSH命令来远程执行命令以及上传、下载文件
1. SSH命令主要用来远程执行命令，以及上传、下载文件
```
    _SSH CONNECT <远程主机名称/IP地址> WITH USER <远程主机用户名> KEYFILE <用户密钥文件位置>
    _SSH CONNECT <远程主机名称/IP地址> WITH USER <远程主机用户名> [PASSWORD <用户密码>]
    _SSH EXECUTE <远程主机命令>
    _SSH DISCONNECT
    _SSH SAVE <需要保存的会话名称>
    _SSH RESTORE <需要恢复的会话名称>
    _SSH SFTP CHMOD <远程文件名> <计划变更的文件权限属性(8进制数位表示)>
    _SSH SFTP GETCWD
    _SSH SFTP CHDIR <计划变更的新目录>
    _SSH SFTP CHOWN <需要修改属主的文件名称> <新的用户ID> <新的组ID>
    _SSH SFTP MKDIR <需要建立的新目录名称> <新目录的文件权限属性(8进制数位表示)>
    _SSH SFTP GET <远程文件名> <本地文件名>
    _SSH SFTP PUT <本地文件名> <远程文件名>
    _SSH SFTP REMOVE <需要删除的远程文件名>
    _SSH SFTP RENAME <需要更名的远程文件名> <更名后的远程文件名>
    _SSH SFTP LISTDIR <需要列出详细信息的远程目录名>
    _SSH SFTP TRUNCATE <需要改变大小的远程文件名> <改变后的文件大小>

    TODO:
      LISTDIR 需要提供详细信息
      GET 可以默认本地文件名, 可以GET到本地的一个目录中
      PUT 可以PUT到一个目录下，也可以默认PUT到远程的当前目录下
      CHOWN 支持用户名和组名的写法
      CHMOD 支持+x, +w等的写法
      GET 可以用正则表达式下载一系列文件
      PUT 可以用正则表达式上传一系列文件
```

#### 使用spool命令来将当前执行结果输出到文件中
1. SPOOL主要用来把随后语句的执行结果记录到特定的文件中
    ```
        _SPOOL  <输出的文件名>
        # Do command 1
        # Do command 2
        # ...
        _SPOOL  OFF 
    ```
2. 以下是一个例子：
    ```
        SQL> _spool test.log
        SQL> select 1+2 from dual;
        +--------+---+
        |   ##   | 3 |
        +--------+---+
        |      1 | 3 |
        +--------+---+
        1 row selected.
        SQL> _spool off
    
        $> type test.log
        SQL> select 1+2 from dual;
        +--------+---+
        |   ##   | 3 |
        +--------+---+
        |      1 | 3 |
        +--------+---+
        1 row selected.
    
        -- spool [file name] 表示将从此刻开始，随后的SQL语句输出到新的文件中
        -- spool off         表示从此刻开始，关于之前的SQL文件输出
    
    ```
3. 在已经进行spool的过程中，spool新的文件名将导致当前文件被关闭，随后的输出切换到新文件中
4. SPOOL的文件默认目录：
   1. 如果程序运行过程中提供了logfile信息，则spool结果的目录和logfile的目录相同
   2. 如果程序运行过程中没有提供logfile信息，且程序在脚本中运行，则spool结果文件目录就是脚本所在的目录
   3. 如果程序运行过程中没有提供logfile信息，且程序在命令行中运行，则spool结果文件目录就是用户所在的当前目录

***
#### 脚本中使用ECHO来生成简易的文件
1. ECHO主要用来快速的生成一些小的脚本和文件。例如：
    ```
    _ECHO <输出的文件名>
        <文件内容>
    _ECHO OFF 
    ```
2. 这里文件内容的所有东西都将被直接输出到指定的文件中，包括换行符等信息
***
#### 系统运行监控
使用内置的监控程序，系统将在后台采集需要的性能数据，如果有必要，这些信息可以记录在程序的扩展日志中。  
```
    _MONITOR MONITORMANAGER ON [WOKERS <int>]
    _MONITOR MONITORMANAGER OFF
    _MONITOR CREATE TASK <taskName> TAG=<taskTag> taskPara1=taskValue1 taskPara2=taskValue2 ...
    _MONITOR START TASK [ <taskName> | ALL ]
    _MONITOR STOP TASK [ <taskName> | ALL ]
    _MONITOR REPORT TASK [ <taskName> | ALL ]
    _MONITOR LIST TASK
```
1. 启动/停止监控调度管理
   运行监控必须首先启动后台的调度管理作业。 启动的方式是_MONITOR MANAGER ON    
   通过指定WORKER的数量来确定监控采集程序占用的线程数目，默认情况下，这个数字为3  

2. 创建监控任务
   1. TAG选项：
   所有的监控任务都必须有TAG选项，用来指定需要采集的指标项目。    
   目前，支持的TAG包括：   
   ```
        cpu_count             # 逻辑CPU数量，该指标只统计一次，不会重复执行                
        cpu_count_physical    # 物理CPU数量，该指标只统计一次，不会重复执行
        cpu_percent           # 统计CPU的占用率
        cpu_times             # CPU运行统计，统计的内容依赖不同的操作系统也会不同
        memory                # 内存使用情况统计
        network               # 网络使用情况统计
        disk                  # 磁盘使用情况统计
        process               # 进程使用情况统计
   ```
   2. FREQ选项：
   FREQ不是必须的，但是在循环检测中设置必要的FREQ是必要的。  
   如果不设置，FREQ的默认值为30，即30秒采集一次数值  
   3. 针对NETWORK的选项  
   ``` 
   NAME  网卡的名称； 可以不填写，不填写意味着查看所有网卡。也可以用通配符表示，如 NAME='eth.*'
   ```
   以下是一个采集网络数据并且指定了选项的例子：  
   ```
        _MONITOR CREATE TASK task1 TAG=network NAME='eth0' FREQ=10; 
   ```
   采集的结果信息包括：
   ```
       nicName:       网卡名称
       bytes_sent:    累计发送字节，单位为byte
       bytes_recv:    累计接收字节，单位为byte
       errin:         收到数据中发生的错误字节数量，单位为byte
       errout:        发送数据中发生的错误字节数量，单位为byte
       dropin:        收到数据中发生的丢弃字节数量，单位为byte
       dropout:       发送数据中发生的丢弃字节数量，单位为byte
       netin:         瞬时网络下行流量，单位为byte/秒
       netout:        瞬时网络上行流量，单位为byte/秒
   ```
   4. 针对DISK的选项
   ``` 
   NAME  磁盘的名称； 可以不填写，不填写意味着查看所有磁盘。也可以用通配符表示，如 NAME='PhysicalDrive[12]'  
   ```
   以下是一个采集网络数据并且指定了选项的例子：
   ```
        _MONITOR CREATE TASK task1 TAG=disk NAME='PhysicalDrive[12]' FREQ=10; 
   ```
   采集的结果信息包括：
   ```
       diskName:     磁盘名称
       read_count:   磁盘读取次数
       write_count:  磁盘写入次数
       read_bytes:   磁盘读取字节
       write_bytes:  磁盘写入字节
       read_time:    磁盘读取响应时间，单位是毫秒
       write_time:   磁盘写入响应时间，单位是毫秒
       read_speed:   磁盘读取速率，单位为byte/秒
       write_speed:  磁盘写入速率，单位为byte/秒
   ```
   5. 针对MEMORY的选项
   采集的结果信息包括：
   ```
       available:   系统当前可用内存，包括未使用的物理内存、可用缓存
       free:        未使用的物理内存
       total:       总使用内存
       percent:     内存使用率（总内存-可用内存/总内存*100)
   ```
   以下是一个采集内存数据的例子：
   ```
        _MONITOR CREATE TASK task1 TAG=memory FREQ=10; 
   ```
   6. 针对进程的选项  
   ``` 
   NAME             进程的名称。可以省略，或者通配符方式表示。需要注意的是，Linux的机制下，对于名称较长的进程，系统会自动截断。  
   EXE              进程的执行文件。可以省略，或者通配符方式表示。需要注意的是，EXE可能为全路径，即包含路径信息。  
   USERNAME         进程的执行用户名。可以省略，或者通配符方式表示  
   ```
   采集的结果包括：
   ``` 
        pid:             进程PID
        username:        进程用户名
        name:            进程名称
        cmdline:         进程命令行，列表形式
        status:          进程状态
        threads:         进程线程数量
        files:           进程文件数量
        exec:            进程执行文件名称
        create_time:     进程创建时间
        cpu_percent:     进程占用CPU百分比
        cpu_times_user:  进程消耗用户态CPU时间
        cpu_times_sys:   进程消耗系统态CPU时间
        mem_rss:         进程常驻内存大小，即使用的实际物理内存大小
        mem_vms:         进程占用内存大小，即包括实际使用的物理内存大小、交换内存、共享内存等
        mem_percent:     进程消耗内存占实际内存的比例      
   ```
   以下是一个进程数据的例子：
   ```
        _MONITOR CREATE TASK task1 TAG=process NAME=SunloginRemote.exe FREQ=3; 
   ```
   7. 针对CPU数量统计    
   cpu_count             统计核心CPU的数量（按照内核数量统计）  
   cpu_count_physical    统计物理CPU的数量  
   以下是一个采集CPU数据的例子：
   ```
        _MONITOR CREATE TASK task1 TAG=cpu_count;
        _MONITOR CREATE TASK task2 TAG=cpu_count_physical; 
   ```
   注意： 针对CPU数量采集设置FREQ是毫无意义的，系统也不会重复采集该数据。  
   8. CPU使用率统计    
   以下是一个采集CPU使用率的例子：
   ```
        _MONITOR CREATE TASK task1 TAG=cpu_percent FREQ=10; 
   ```
   采集的结果包括：
   ``` 
        ratio:           CPU使用率比例（百分比）
   ```
   9. CPU时间统计  
          以下是一个采集CPU时间的例子：
          ```
              _MONITOR CREATE TASK task1 TAG=cpu_times FREQ=10;
          ```
       依赖不同的操作系统，统计指标会所有不同。后期处理需要格外小心。  
       Linux下：
       ```
         user:          用户态进程占据时间
         system:        核心态进程占据时间
         idle:          系统空闲时间
         iowait:        系统IO等待时间
         irq:           系统硬中断时间
         softirq:       系统软中断时间
         steal:         CPU排队时间（只发生在虚拟机中，物理CPU资源不足，导致虚拟CPU必须等待的情况）
       ```
       Windows下：
       ```
         user:          用户态进程占据时间
         system:        核心态进程占据时间
         idle:          系统空闲时间
         interrupt:     系统中断时间
         dpc:           延迟系统调用时间（系统核心中断无法提供服务，排队中)
       ```
       MACOS下：
       ```
         user:          用户态进程占据时间
         system:        核心态进程占据时间
         idle:          系统空闲时间
         count:         cpu_times.count,
         index:         cpu_times.index,
         nice:          cpu_times.nice       
         interrupt:     系统中断时间
         dpc:           延迟系统调用时间（系统核心中断无法提供服务，排队中)
       ```
   
   
***
#### 程序退出
如果你执行一个脚本，则在以下三种情况下会退出
1. 脚本执行失败。并且设置_WHENEVER ERROR EXIT <INT>的时候。退出的值将是这里的<INT>值
2. 脚本执行结束。退出值为0
3. 脚本中包含了_EXIT <INT>或者_QUIT <INT>语句。退出的值将是这里的<INT>值, 如果不填写，将为0

使用exit或者quit来退出命令行程序，或者在脚本中使用该语句
```
    (_EXIT | _QUIT) [返回值]
    # 退出的值将是这里的<INT>值, 如果不填写，将为0
```
***
#### 程序中用到的环境变量
程序中我们定义了一些环境变量，用来支撑客户部署和调试的需要。  

##### TESTCLI_DEBUG
布尔类型，用来标记程序是否在DEBUG模式。  
如果为0（默认）： 表示程序处于非调试模式。  
如果为1（即打开DEBUG模式）：  表示程序处于调试模式。  
调试模式仅仅用于，在你认为程序发生了问题，希望打印更多的信息来发现问题所在的时候。    
在环境变量里头设置TESTCLI_DEBUG和在命令行或者脚本中执行 _set debug on的效果完全一致。  
```
   export TESTCLI_DEBUG=1
   # Windows下用：  set TESTCLI_DEBUG 1
   
   随后执行的语句将打印更多的内部日志  
```

##### TESTCLI_CONF
用来定义程序配置文件的目录。  
默认的配置文件是程序安装目录的conf/testcli.ini。 即PYTHON_HOME/lib/python36/site-packages/testcli/conf/testcli.ini.  
```
   export TESTCLI_CONF=/tmp/mycli.conf
   # Windows下用：  set TESTCLI_CONF \Temp\mycli.conf  
```

##### TESTCLI_JLIBDIR
用来定义程序需要加载的数据源JAR包的位置（文件夹名称）    
默认的配置文件是程序安装目录的jlib。 即PYTHON_HOME/lib/python36/site-packages/testcli/jlib.  
```
   export TESTCLI_JLIBDIR=/tmp/myjlib
   # Windows下用：  set TESTCLI_JLIBDIR \Temp\myjlib  
```
如果实际部署中用到了客户化的JAR包，可以通过定义TESTCLI_CONF和TESTCLI_JLIBDIR来指定客户化文件的位置，而不用修改PYTHON系统目录。  


##### TESTCLI_CONNECTION_URL
格式和CONNECT语法中的URL相同， 如：  
```
   export TESTCLI_CONNECTION_URL=jdbc:linkoopdb:tcp://localhost:9105/ldb
   # Windows下用：  set TESTCLI_CONNECTION_URL jdbc:linkoopdb:tcp://localhost:9105/ldb
```
在设置了TESTCLI_CONNECTION_URL，在连接数据库的时候，可以不再指定连接字符串的后半部分。  
如：
```
   set TESTCLI_CONNECTION_URL jdbc:linkoopdb:tcp://localhost:9105/ldb
   (base) C:\>testcli
   TestCli Release 0.0.8
   SQL> _connect admin/123456
   Connected.
   
   这和不设置TESTCLI_CONNECTION_URL，执行如下语句的效果是完全一致的。  
   (base) C:\>testcli
   TestCli Release 0.0.8
   SQL> _connect admin/123456@jdbc:linkoopdb:tcp://localhost:9105/ldb
   Connected.
```


### TestCliRobot

#### 程序命令行参数
```
Usage: testclirobot [OPTIONS]

Options:
  --job TEXT               Specify robot job file or directory.  [required]
  --jobgroup TEXT          Specify robot job list file. Each line represents
                           one job.
  --work TEXT              Specify the work directory(ALL FILES IN THIS
                           DIRECTORY WILL BE CLEANED).  [required]
  --parallel INTEGER       Specify the parallelism of the job, default is 1,
                           means no parallel.
  --jobtimeout INTEGER     Specify the timeout limit(seconds) of the job,
                           Default is -1, means no limit.
  --workertimeout INTEGER  Specify the timeout limit(seconds) of one suite,
                           Default is -1, means no limit.
  --force                  Clean all files under working directory if not
                           empty.
  --runid TEXT             Test run unique id. Default is 0. will save in
                           extend log for later analyze.
  --help                   Show this message and exit.
```
##### --job
指定需要运行的测试脚本位置，参数可以为特定的某个robot文件，也可以是特定的某个目录。  
如果给定参数是目录，则目录下所有的robot文件都会被运行。    
如果需要运行多个目录或者多个文件，则可以在命令行里头一同指定，多个目录或者文件参数中间用逗号分隔即可。

##### --jobgroup
指定一个测试脚本的描述文件  
用于当测试任务比较多的时候，将具体的JOB记录在一个文本文件中。  

##### --work
指定测试的工作目录位置，所有的结果信息（包括程序运行日志），报告信息都将存放在该目录下。  
开始运行后，该目录下的内容将会被清空。需要确保这个目录下不存放之前的重要信息。

##### --parallel 
控制测试运行的并行度。 默认为1， 可以为任何不为1的正整数。  
在程序并行期间，运行级别是判断程序运行先后的依据。同一个级别内部，运行的顺序不固定。

#####  --jobtimeout
控制任务的整体超时时间。参数为时间信息，秒作为单位。默认为-1，即完全不考虑超时。  
在达到到这个时间后，正在运行的任务会被终止，没有运行的任务不会再被执行。  
这里的时间统计并不是精准统计，只是一个相对大概。即使超时时间到达，后续也还有报告整理等工作要做，停止也需要一段时间。

#####  --worktimeout
控制单个测试套件的超时时间。参数为时间信息，秒作为单位。默认为-1，即完全不考虑超时。  
在达到到这个时间后，正在运行的任务会被终止，后续运行队列上的任务将会被继续运行。  
这里的时间统计并不是精准统计，只是一个相对大概。即使超时时间到达，后续也还有报告整理等  工作要做，停止也需要一段时间。

#####  --runid
在扩展日志中会记录这个ID信息，用于需要保存多次测试记录，并区分每个测试记录的时候使用

#####  --force
控制是否强制清空工作目录。 如果制定了force，则运行前会强行清空工作目录下的所有文件（包括子目录）

#### ROBOTOPTIONS环境变量
用来在运行Robot的时候设置某些排除选项
如：  
```
export ROBOTOPTIONS="--exclude DEMO --execlude TEST"
testclirobot ....
```
该命令将排除所有TAG为DEMO以及TEST的测试

#### Robot文件编写规则
CliRobot中的文件使用RobotFrameWork的代码编写，具体RF的代码写作方法可以参考：https://robotframework.org/
原则上，CliRobot中可以用不使用TestCli提供的Robot扩展，而作为Robot程序的调度使用，但是这样做将失去了CliRobot本身的作用。完全可以通过Robot自身命令行或者一些第三方插件来直接运行Robot程序，而不是必须依赖TestCli的Robot扩展。    
以下是一个Robot文件的书写例子和解释：
```
*** Settings ***
## Resource来定义引用，引用TestCli的扩展函数库
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
## Test Setup中需要定义TestCli扩展的函数-初始化函数
Test Setup       TestCli Test Setup
## Test TearDown中需要定义TestCli扩展的函数-清理函数
Test Teardown    TestCli Test Clnup

*** Test Cases ***
Demo1
    [Documentation]            TestCli基于Robot测试样例
    ## Execute TestCli Script等都是TestCli实现的Robot扩展函数，随后将专门介绍
    Execute TestCli Script     demo1.sql    demo1.log
    Compare Files              demo1.log    demo1.ref
```

##### TestCli提供的内置Robot扩展函数-TestCli
需要主意的是： 以下说的默认值未必是Robot测试执行的默认行为，只是这个扩展函数的默认值。程序执行的默认行为除了受到下面默认值的影响外，还受到套件初始化函数Setup_Robot中的行为行为。具体实际的默认值情况见另外的描述。
######	Execute TestCli Script
	说明：
		执行TEST脚本
	参数：
		p_szScript_FileName            计划执行的脚本名称
		p_szLogOutPutFileName = None   计划输出的执行日志名称（默认为和脚本文件桶命的log文件）
######	Logon And Execute TestCli Script
	说明：
		登录数据库并执行TEST脚本
	参数：
		logonString                     登录数据库的用户名/口令
		p_szScript_FileName             计划执行的脚本名称
		p_szLogOutPutFileName = None    计划输出的执行日志名称（默认为和脚本文件桶命的log文件）
######	TestCli Break When Error
	说明：
		设置是否在遇到错误的时候中断该Case的后续运行，默认为不退出  
		如果设置为True，则TestCli运行会中断，Case会被判断执行失败  
		如果设置为False，则TestCli运行不会中断，运行结果文件中有错误信息，供参考
	参数：
		p_BreakWithError                是否退出。 TRUE/FALSE
######	TestCli Enable ConsoleOutput
	说明：
		设置在执行中将控制台输出信息显示到Robot的Log中，默认为不显示
	参数：
		p_ConsoleOutput                 是否显示。 TRUE/FALSE
######	TestCli Enable ExtendLog
	说明：
		设置在执行中记录扩展日志（包括语句级别的执行时间，场景信息等）。默认是不记录
	参数：
		p_enableExtendLog                是否记录。 TRUE/FALSE
######	TestCli Set CommandMapping
	说明：
		设置程序中用到的映射文件，如果包括多个文件，用逗号分割
	参数：
		p_szCommandMapping               映射文件
######	TestCli Set ResultSet
	说明：
		设置脚本执行时候的客户端输出字符集。默认为UTF-8
	参数：
		p_ResultCharset                  有效的字符集，如UTF-8,GBK
######	TestCli Set ClientSet
	说明：
		设置脚本执行时候的客户端输入字符集。默认为UTF-8
	参数：
		p_ClientCharset                  有效的字符集，如UTF-8,GBK

##### TestCli提供的内置Robot扩展函数-Compare
需要主意的是： 以下说的默认值未必是Robot测试执行的默认行为，只是这个扩展函数的默认值。程序执行的默认行为除了受到下面默认值的影响外，还受到套件初始化函数Setup_Robot中的行为行为。具体实际的默认值情况见另外的描述。
######	Compare Algorithm
	说明：
		设置文本比对的算法。 分为LCS和Myers. 默认为Myers
		LCS在小数据量下有优势。Myers在大数据量下有优势。
	参数：
		algorithm                        算法， LCS或者Myers
######	Compare Break When Difference
	说明：
		设置是否在遇到错误的时候中断该Case的后续运行。默认不中断
	参数：
		p_BreakWithDifference            是否中断。 TRUE/FALSE		
######	Compare Clean Mask
	说明：
		清空之前设置的所有掩码信息
	参数：
		无
######	Compare Clean Skip
	说明：
		清空之前设置的所有行忽略信息
	参数：
		无
######	Compare Enable ConsoleOutput
	说明：
		设置是否在在屏幕上显示Dif文件的内容。默认是不显示
	参数：
		p_ConsoleOutput                 是否显示。  TRUE/FALSE
######	Compare Enable Mask
	说明：
		设置是否在比对的时候考虑正则表达式。 默认为不考虑
	参数：
		p_CompareWithMask               是否考虑。  TRUE/FALSE
######	Compare Files
	说明：
		比较两个文件是否一致
	参数：
		p_szWorkFile:        需要比对的当前结果文件
		p_szReferenceFile：  需要比对的结果参考文件
######	Compare Ignore EmptyLine
	说明：
		设置是否在比对的时候忽略空行（包含仅有空格的空白行）。默认为不忽略
	参数：
		p_IgnoreEmptyLine               是否考虑。  TRUE/FALSE
######	Compare IgnoreCase
	说明：
		设置是否在比对的时候忽略大小写。默认为不忽略
	参数：
		p_IgnoreCase                     是否考虑。  TRUE/FALSE
######	Compare IgnoreTailOrHeadBlank
	说明：
		设置是否在比对的时候忽略行首和行末的空格。默认为不忽略
	参数：
		p_IgnoreTailOrHeadBlank          是否考虑。  TRUE/FALSE
######	Compare Mask
	说明：
		设置是否在比对的时候掩码某些特殊行。可以用正则表达式来描述指定的行内容
		如果有多个内容需要在比对的时候进行掩码，则可以重复执行该语句
	参数：
		p_szMaskLine                    特定行的正则表达式。
######	Compare Not Mask
	说明：
		设置是否在比对的时候取消之前定义的掩码行。
		该语句和之前的Compare Mask是一个反操作，用来取消已经不再需要的掩码信息
		如果有多个内容需要取消，则可以重复执行该语句
	参数：
		p_szMaskLine                    特定行的正则表达式。
######	Compare Not Skip
	说明：
		设置是否在比对的时候取消忽略某些特殊行。
		该语句和Compare Skip是一个反操作，用来取消已经不再需要的掩码信息
		如果有多个内容需要取消忽略，则可以重复执行该语句
	参数：
		p_szSkipLine                    特定行的正则表达式。
######	Compare SetDiffEncoding
	说明：
		设置在生成dif文件时候用到的Encoding。默认是UTF-8
	参数：
		p_szDifEncoding                 有效的字符编码集。如UTF-8，GBK等
######	Compare SetRefEncoding
	说明：
		设置在读取REF参考文件时候用到的Encoding。默认是UTF-8
	参数：
		p_szDifEncoding                 有效的字符编码集。如UTF-8，GBK等
######	Compare SetWorkEncoding
	说明：
		设置在读取当前结果参考文件时候用到的Encoding。默认是UTF-8
	参数：
		p_szDifEncoding                 有效的字符编码集。如UTF-8，GBK等
######	Compare Show Config
	说明：
		辅助函数。在控制台中打印当前的所有Compare设置
	参数：
		无
######	Compare Skip
	说明：
		设置是否在比对的时候忽略某些特殊行。可以用正则表达式来描述指定的行内容
		如果有多个内容需要忽略，则可以重复执行该语句
	参数：
		p_szSkipLine                    特定行的正则表达式。
##### SetupTestCli.robot中定义的测试预配置
SetupTestCli.robot定义了一些预先设置的扩展参数设定。这些设定可以被覆盖，如果有相关测试需要。这些预设置只是我们根据经验进行的总结。
```
    # 控制TestCli控制台是否显示输出，如果在Jenkins中运行，则打开后同样会在Jenkins的控制台上显示出来
    # 小心： 如果测试中包含返回内容较多的查询，这样打开将导致测试报告文件很大，可能会变得无法阅读
    # 默认是关闭状态，即不显示TestCli的输出
    TestCli Enable ConsoleOutput        False

    # 控制SQLCli在执行SQL语句中是否遇到错误，就立即终止后续的SQL执行
    # 默认是不终止，即使SQL有错误，整个SQL也会被执行完毕
    TestCli Break When Error            False

    # 控制TestCli是否记录扩展的日志，打开后，会在LOG目录下生成一个xlog文件
    # 这里设置为打开状态，即记录扩展信息
    TestCli Enable ExtendLog            True

    # 控制Compare过程中如果发生比对不一致现象，是否将不一致的结果输出在控制台上。
    # 如果在Jenkins中运行，则打开后同样会在Jenkins的控制台上显示出来
    # 小心： 如果比对文件很大，这样打开将导致测试报告文件很大，可能会变得无法阅读
    # 默认是关闭状态，即不显示Compare的结果
    Compare Enable ConsoleOutput       True

    # 控制日志比对是否在遇到不一致现象的时候，是否在Robot中抛出比对错误
    # 默认是抛出
    Compare Break When Difference      True

    # 设置比较时使用的比较算法，有LCS和MYERS，MYERS在大数据量文件下具有明显优势
    Compare Algorithm                  MKERS

    # 比对参考文件的时候忽略空白行
    Compare Ignore EmptyLine           True

    # 比对参考文件的时候使用正则表达式
    Compare Enable Mask                True

    # 比对文件的时候忽略大小写差异
    Compare IgnoreCase                 False

    # 比对文件的时候忽略内容的首末空格
    Compare IgnoreTailOrHeadBlank      True

    # 比对参考文件的时候跳过所有符合以下标记的行
    #     Running time elapsed 是程序的运行时长，由于每次运行都可能不一致，所以比对没有意义
    Compare Skip                       Running time elapsed.*
    #     Current clock time   是脚本的当前结束时间，由于每次运行都可能不一致，所以比对没有意义
    Compare Skip                       Current clock time.*
    #     REWROTED             被SQLMAPPING文件改写了的SQL信息，在不同的SQLMAP下，可能会不一样，所以比对没有意义
    Compare Skip                       REWROTED.*
    #     PROFILE              SQL文件的环境预处理文件，不作为日志的比较内容
    Compare Skip                       PROFILE.*
    #     SKIP                 过滤掉那些在SQL中强制描述不需要比对的内容
    Compare Skip                       SKIP.*
    #     TestCli版本号，        由于版本的更新，版本号比对没有意义
    Compare Skip                       TestCli Release .*
    #     start                start开始的是在具体执行某一个脚本，在执行中由于路径名不同，具体start后面的信息也会不同，所以不再比对
    Compare Skip                       SQL\> start .*
    #     Scneario                 过滤掉Scneario注释信息带来的差异
    Compare Skip                       .*\> --.*

    # Case运行在脚本所在的目录下，切换当前工作目录
    SetupRoot CD CurrentDirectory        ${SUITE SOURCE}

    # 记录所有环境变量信息到日志文件中，便于日后检查
    log environment variables
```
###### 如何用自定义的测试配置来覆盖系统默认配置
```
*** Settings ***
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
# 重新定义测试套件运行的初始化函数，指向自定义的新关键字
Test Setup       My Custom Setup
Test Teardown    TestCli Test Clnup
MetaData         runLevel   10

*** Test Cases ***
Demo1
    [Documentation]            TestCli基于Robot测试样例
    Execute TestCli Script     demo1.sql    demo1.log
    Compare Files              demo1.log    demo1.ref

*** Keywords ***
My Custom Setup
    # 这里继承了默认的Setup，并随后覆盖了其中的部分设置
    TestCli Test Setup
    Compare Enable ConsoleOutput        True
    SQLCli Enable ConsoleOutput         True

```

##### runLevel，     程序运行级别控制
在程序需要运行多个robot文件的时候，runlevel会按照优先级来运行不同的文件。即总是先运行runlevel数字小的脚本，随后运行runlevel数字高的。默认的优先级数字为100。  
Robot中定义runLevel的例子：
```
*** Settings ***
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
Test Setup       TestCli Test Setup
Test Teardown    TestCli Test Clnup
MetaData         runLevel   10

*** Test Cases ***
Demo1
    [Documentation]            TestCli基于Robot测试样例
    Execute TestCli Script     demo1.sql    demo1.log
    Compare Files              demo1.log    demo1.ref
```

##### StandAlone，独立运行标志
如果某个robot文件不能作为测试独立运行，则可以通过设置StandAlone来将其排除。  
被设置了StandAlone的程序在Robot测试中会被自动过滤（不影响其被其他Robot调用）。  
当StandAlone被定义为N或者No或者Not的时候，表示非独立运行的测试用例。  
Robot中定义StandAlone的例子：

```
*** Settings ***
Resource         %{TEST_ROOT}/common/SetupTestCli.robot
Test Setup       TestCli Test Setup
Test Teardown    TestCli Test Clnup
MetaData         StandAlone   N
      
*** Test Cases ***
Demo1
    [Documentation]            TestCli基于Robot测试样例
    Execute TestCli Script     demo1.sql    demo1.log
    Compare Files              demo1.log    demo1.ref
```

## TestCli 开发者说明

### 程序代码结构
```
TestCli
│  LICENSE.txt                                        # 许可信息描述，没啥不许可的，Github非要提供一个不可
│  README.md                                          # 说明文档
│  setup.py                                           # 打包配置
│  build.bat                                          # 编译构建当前运行包
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

#### 从源代码中启动TestCli控制台
```
    # 进入到工程目录
    cd testcli
    > python -m testcli.cliconsole
```

#### 从源代码中启动TestCli的文件比对功能
```
    # 进入到工程目录
    cd testcli
    > python -m testcli.clicomp
```

#### 从源代码中启动TestCli的Robot测试功能
```
    # 进入到工程目录
    cd testcli
    > python -m testcli.clirobot
```

#### 程序调试
从外部启用DEBUG
```
   export TESTCLI_DEBUG=1
   testcli --....

```

从脚本内部启用DEBUG
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
   Prompt_ToolKit需要控制台的一些设置以保证正确运行（模拟控制台输出的终端必须选中）
   
```

#### 调试Antlr语法定义
```
   程序中对语法的解析采用Antlr的访问器来解析表达

   如果要修改Antlr语法，请：
   1. 按照要求安装Antlr IDEA插件
   2. 修改g4文件
   3. 右键单击修改后的g4文件，执行Generate Antlr Recognizer, 生成Python运行文件
      第一次Generate前需要配置默认Generate选项(Configure ANTLR...)，选项为：
          Grammer file enconding:        填入utf-8
          Language:                      填入Python3
          Location of imported grammers: 填入<项目所在路径/testcli/antlr>
          Generate parse tree listener:  取消选择，即不需要监听器
          Generate parse tree visitor:   选择，即需要访问器      
   3. 修改后可以利用IDEA插件提供的预览器（ANTLR Preview)来检查修改是否正确
   4. 确认修改无误后用generate.bat中的语句来重新生成Antlr的Python运行文件(放置在antlrgen目录下)
      ！！！请不要直接修改antlrgen目录下的文件，此处的修改将不会被保留!!!   
   5. 修改对应的sqlvisitor.py和apivisitor.py文件, 如果修改基础命令，则两个文件都需要同步修改
      确认能修解析到新的语法内容
   6. 修改对应command的处理文件，实现新语法的功能实现
```

#### 单元测试
```
   程序修改后请运行test\testcliunittest.py，确保测试运行无误，改动没有引起非预期的变化
   
   运行时间大概几分钟，也可以通过命令行中的selftest参数来运行，比如：
   testcli --selftest
```

#### 从应用程序的角度直接调用TestCli类
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

#### 从应用程序的角度直接调用Regress类（运行Robot脚本文件）
```
	from testcli.robot.common.runregress import Regress as runRobot
    from testcli.robot.common.runregress import RegressException as runRobotException
    
    logger = logging.getLogger("robotTest")
    runRoboter = runRobot(
        maxProcess=3,
        workDirectory="C:/Temp/",
        testRoot="C:/work/testcli/robot",
        logger=logger,
        workerTimeout=3600,
        scriptTimeout=18000,
        jobList=["a.robot", "b.robot", ],
        reportType="JUNIT,HTML",
        reportLevel="CASE",
        executorMonitor=None,
        extraParameters=None
    )
    # 运行Robot测试
    runRoboter.run()
    
    # 整理测试报告
    runRoboter.generateTestReport()

```

## 已知问题
### Windows下程序安装路径中包含中文的问题
由于JPype在处理ClassPath时候的问题，当程序安装目录包含中文，或者用户自定义Jar包路径中包含中文的时候，将导致Jar包无法加载。  
从直观的表现来看，就是配置好的Jar包找不到。    
这个问题暂时没有好的解决办法。
