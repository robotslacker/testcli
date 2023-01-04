# TestCli 快速说明

TestCli 是一个主要用Python完成的，基于命令行下运行的，精致的测试工具。    

## 不需要怀疑，目前TestCli还在努力开发中，Bug会比你想象的多得多，没事，吐呀吐呀，你就习惯了。
## 如果你希望一个稳定功能的工具，请移步到我之前的软件SQLCli，那个作为一个稳定版本，经历了时间的漫长考验，相对稳定的多。  
## 我没有计划更新SQLCli的功能，即使我发现了其中的一些问题，我都会体现在目前这个TestCli中，换句话说，那个是旧爱，这个是新欢。我是喜新厌旧的。  

### 概要
#### 设计目的：  
* 满足数据库方面的相关功能测试、压力测试需要。   
* 满足API方面的相关功能测试、压力测试需要。
* 能够作为一个日常小工具，进行数据库的日常操作，进行数据查询、更新等。      
* 更多的为测试工作带来的便利功能，包括：
  * 方便的用来生成随机数据文件的工具。 
  * 使用提示（Hint）信息来过滤或者掩码输出结果。
  * 使用TermOut，FeedBack，ECHO来控制显示输出的内容。
  * 使用ECHO来生成一些临时性的测试文件
  * 使用COMPARE来进行文件级别的内容比对，比对过程中支持了正则表达过滤，正则表达掩码
  * 使用SSH来完成远程主机命令的操作，文件的上传和下载
  * 使用ASSERT来判断运行的结果
  * 使用JOBMANAGER来并行执行多个脚本，并提供了聚合点的完整支持
  * 使用PLUGIN来加载完成的Python文件作为测试功能的扩展
  * 支持在测试脚本中嵌入Python语法来完成一些常规难以完整的验证
  * 支持对测试脚本中的变量信息进行宏替换，包括基于映射文件的替换，基于应用变量的替换，基于环境变量的替换
  * 支持在程序中捕捉返回的上下文信息，利用前面执行的结果来影响后续的影响结果
  * 支持在程序中使用LOOP，IF等循环、条件判断表达式，来完成复杂的测试逻辑

***
#### 背景描述
* TestCli的前身是SQLCli，本人的另外一个类似项目。 
* TestCli是基于SQLCli进行改进，并废弃了SQLCli中一些不常用的功能。 如果你很在意那些被废弃的功能，请继续使用SQLCli
* TestCli利用了Prompt_Toolkit，这是一个Python的开源软件，基于Prompt_Toolkit，TestCli实现了命令行的输入、历史语句的记录、语句的翻页等。
* TestCli利用了Antlr，将基本的语法内容用Antlr进行描述，并根据解析的结果进行执行。
* 对于SQL部分，TestCli利用JDBC桥（JPype）作为依托，将所有用户输入的SQL转换为JDBC语句，并进行执行。
* 早期的SQLCli，利用JayDeBeApi作为连接数据库的方法，但是很快废弃了JayDeBeApi，这是因为
  * JayDeBeApi对于JDBC的支持并不完全标准，对于一些LOB类型，支持很差
  * JayDeBeApi返回的数据类型不是原生的Python数据类型（而是Java类型），这给后续的处理带来困难
  * JayDeBeApi并不是一个多线程应用，在多线程下，其加载JAVAVM的方式会带来错误
* 早期的SQLCli，支持了ODBC的连接方式，并实现了一些简单的语句，但是由于并没有多少的实际使用场景，所以这部分功能在迁移到TestCli后被删除了

*** 
#### License许可问题
不要问我什么License的问题。如果问，那答案就是： FREE！  完全的FREE！  
实际上，我很高兴你如果感兴趣这个项目，如果你能参与到完善这个项目中，我将更加不信感激！  
即使你不能亲自参与，如果遇到了什么问题，你都可以发邮件给我，发issue到开源网站，我会处理的。  

***
#### TestCli目前支持的数据库  
   * Oracle,MySQL,PostgreSQL,SQLServer,TeraData, Hive, H2等主流通用数据库  
   * 达梦，神通， 金仓， 南大通用，LinkoopDB, 快立方等众多国产数据库  
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
这个工具的存在目的不是为了替代PostMan，JMeter等测试工具。  
这个工具的存在目的是在尽可能地兼容这些命令行工具的同时提供测试工作需要的相关特性。    
选择了Python作为开发工具，工具本身部署的复杂性和对环境的依赖性决定了这个工具无法作为产品的功能之一交付给客户。  

***
### 安装
安装的前提有：
   * 有一个Python 3.6以上的环境
   * 能够连接到互联网上， 便于下载必要的包
   * 安装JDK8或者JDK11  （目前我的调试环境和测试环境均为JDK11，未对其他JDK环境进行验证） 
   * 对于Windows平台，需要提前安装微软的C++编译器（jpype1使用了JNI技术，需要动态编译）  
   * 对于Linux平台，  需要提前安装gcc编译器，以及Python3的开发包（原因同上）  
     yum install -y gcc-c++ gcc  
     yum install python3<?>-devel(在Anaconda环境下，这一步不是必须的. ?是具体的Python版本，根据自己的环境决定)
   * 对于MAC平台，  需要提前安装gcc编译器    
     brew install gcc  

依赖的第三方安装包：  
   * 这些安装包会在robotslacker-testcli安装的时候自动随带安装
   * click                    : Python的命令行参数处理
   * hdfs                     : HDFS类库，支持对HDFS文件操作
   * fs                       : 构建虚拟文件系统，用来支撑随机数据文件的生成
   * JPype1                   : Python的Java请求封装，用于完成运行时JDBC请求调用  
   * paramiko                 : Python的SSH协议支持，用于完成远程主机操作  
   * prompt_toolkit           : 用于提供交互式命令行和终端应用程序
   * setproctitle             : Python通过setproctitle来设置进程名称，从而在多进程并发时候给调试人员以帮助
   * urllib3                  : HTTP客户端请求操作
   * antlr4-python3-runtime   : Antlr4运行时引用

利用pip来安装：
```
   pip install -U robotslacker-testcli
```

安装后步骤-更新驱动程序配置：  
   * 根据你的需要， 放置自己的jar包到 <PYTHON_HONE>/../site-packages/testcli/jlib下
   * github上提供的仅仅是一些测试用的Jar包，请根据需要，自行添加实际需要的Jar包
   * 如果自行了添加了jar包，修改testcli/conf/testcli.ini文件：  
   
***

### 第一次使用
安装后直接在命令下执行testcli命令即可。  
如果你的<PYTHON_HOME>/scripts没有被添加到当前环境的$PATH中，你可能需要输入全路径名  
```
(base) C:\>testcli
TestCli Release 0.0.7
SQL>
```
如果你这里看到了版本信息，那祝贺你，你的程序安装成功了

```
(base) C:\>testcli
TestCli Release 0.0.7
SQL> _connect /mem
Database connected.
SQL>
```
如果你看到了Connected信息，那再一次祝贺你，你的程序基本工作正常。 

***

### 程序的自检
运行selftest可以在当前运行环境上快速检查程序是否存在问题  
尽管这不是程序运行所必须的，但是仍然建议在部署应用之前运行该命令以帮助发现潜在的问题。  
命令大概需要几分钟的时间，为了测试API业务，程序还会占用8000端口作为测试的需要。  
```
(base) C:\>testcli --selftest
=========================== test session starts =======================
platform win32 -- Python 3.9.7, pytest-7.2.0, pluggy-0.13.1 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
....
================================== 52 passed in 37.25s ================
```
如果你看到了Passed信息，那再一次祝贺你，你的程序自检完全正常。你可以在当前环境下开展你的工作了。 

### 驱动程序的下载和配置
TestCli是一个基于JDBC的数据库工具，基于JDBC操作数据库的前提当前环境下有对应的数据库连接jar包。 

#### 驱动程序的配置
配置文件位于TestCli的安装目录下的conf目录中，配置文件名为:testcli.ini  
配置例子:
```
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

### 程序的命令行参数
```
(base) C:\>testcli --help
Usage: testcli [OPTIONS]

Options:
  --version                Show TestCli version.
  --logon TEXT             SQL logon user name and password. user/pass
  --logfile TEXT           Log every command and its results to file.
  --execute TEXT           Execute command script.
  --commandmap TEXT        Command mapping file.
  --nologo                 Execute with no-logo mode.
  --xlog TEXT              Save command extended log.
  --xlogoverwrite          Overwrite extended log if old file exists. Default is false
  --clientcharset TEXT     Set client charset. Default is UTF-8.
  --resultcharset TEXT     Set result charset. Default is same to clientCharset.
  --profile TEXT           Startup profile.
  --scripttimeout INTEGER  Script timeout(seconds).
  --namespace TEXT         Command default name space(SQL|API). Default is depend on file suffix.
  --selftest               Run self test and exit.
  --readme                 Show README doc and exit.
  --suitename TEXT         Test suite name.
  --casename TEXT          Test case name.
  --help                   Show this message and exit.  
```

#### --version 
用来显示当前工具的版本号
```
(base) C:\>testcli --version
Version: 0.0.7
```

#### --logon  
用来输入连接数据的的用户名和口令
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

#### --logfile   
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

#### --execute 
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

#### --commandmap   
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

#### --nologo    
这是一个选项，用来控制TestCli是否会在连接的时候显示当前的程序版本
```
(base) testCli 
TestCli Release 0.0.7
SQL>   
区别：
(base) testCli --nologo
SQL>
```

#### --xlog  
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
#### --xlogoverwrite      
控制如果扩展日志文件已经存在的方式下，是否会覆盖掉原有的扩展日志文件。默认是不覆盖，即追加模式

#### --clientcharset      
定义客户端的字符集，默认为UTF-8  
客户端的字符集影响了脚本的字符集，命令行中输入信息的字符集  

#### --resultcharset      
定义了结果输出文件的字符集，包括日志文件，也包括SPOOL导出的文件，也包括ECHO生成的回显文件

#### --profile            
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
#### --scripttimeout   
控制脚本的最大超时时间，这里的计数单位是秒。默认为-1，即完全不控制。    
以下是一个设置了scriptTimeout为3时候的执行例子，当达到3秒的限制后，脚本会立刻结束运行，不再继续下去。 
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
3. 除了在命令行上指定脚本的全局超时时间限制外，还可以在脚本中指定具体语句的执行时间显示。 具体的介绍将在后面部分描述。  

#### --namespace    
指定程序的默认命名空间，如果不指定，命名空间的默认依赖于文件后缀，具体的规则是：  
1. 文件后缀为.sql， 则默认的命名空间为SQL
2. 文件后缀为.api， 则默认的命名空间为API
3. 其他文件后缀，默认的命名空间为SQL  
命名空间的不同将影响语句的解析执行， 你也可以在脚本中进行命名空间的切换  

#### --selftest      
运行自测脚本并退出  
这个选项仅仅用于测试当前环境下是否已经正确安装了本工具。  

#### --readme        
在控制台上显示本帮助文档并退出.  
需要注意的是：不同的终端对于富文本字体的处置规则并不相同，所以不能苛求显示的完全正确性和美观性。  

#### --suitename     
指定测试套件的名称，这个通常用于记录在扩展日志，或者完成测试报告的时候协助统计分析测试结果使用

#### --casename      
指定测试用例的名称，这个通常用于记录在扩展日志，或者完成测试报告的时候协助统计分析测试结果使用  

#### --help          
显示本帮助信息并退出  

***

# 以下内容尚未来得及更新，请等等哈


### 在TestCli里面查看当前支持的命令
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> help
+--------------+-----------------------------------------------------+
| Command      | Description                                         |
+--------------+-----------------------------------------------------+
| __internal__ | 执行内部操作命令：                                  |
| __internal__ |     __internal__ hdfs          HDFS文件操作         |
| __internal__ |     __internal__ kafka         kafka队列操作        |
| __internal__ |     __internal__ data          随机测试数据管理     |
| __internal__ |     __internal__ test          测试管理             |
| __internal__ |     __internal__ job           后台并发测试任务管理 |
| __internal__ |     __internal__ transaction   后台并发测试事务管理 |
| connect      | 连接到指定的数据库                                  |
| disconnect   | 断开数据库连接                                      |
| echo         | 回显输入到指定的文件                                |
| exit         | 正常退出当前应用程序                                |
| help         | Show this help.                                     |
| host         | 执行操作系统命令                                    |
| loaddriver   | 加载数据库驱动文件                                  |
| loadcommandMap   | 加载SQL映射文件                                     |
| quit         | Quit.                                               |
| session      | 数据库连接会话管理                                  |
| set          | 设置运行时选项                                      |
| sleep        | 程序休眠(单位是秒)                                  |
| spool        | 将输出打印到指定文件                                |
| start        | 执行指定的测试脚本                                  |
+--------------+-----------------------------------------------------+
这里显示的是所有除了标准SQL语句外，可以被执行的各种命令开头。
标准的SQL语句并没有在这里显示出来，你可以直接在控制行内或者脚本里头执行SQL脚本。



```

















***
### 连接数据库
在TestCli命令行里头，可以通过connect命令来连接到具体的数据库
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> connect user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> 
能够成功执行connect的前提是： 数据库驱动已经放置到jlib下，并且在conf中正确配置

如果已经在环境变量中指定了TestCli_CONNECTION_URL，连接可以简化为
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> connect user/pass
Database connected.
SQL> 

在数据库第一次连接后，第二次以及以后的连接可以不再输入连接字符串，程序会默认使用上一次已经使用过的连接字符串信息，比如：
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> connect user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> connect user2/pass2
Database connected.
SQL> 

常见数据库的连接方式示例：
H2:
    connnet mem
ORACLE:
    connect username/password@jdbc:oracle:tcp://IP:Port/Service_Name
MYSQL:
    connect username/password@jdbc:mysql:tcp://IP:Port/Service_Name
PostgreSQL：
    connect username/password@jdbc:postgresql:tcp://IP:Port/Service_Name
SQLServer：
    connect username/password@jdbc:sqlserver:tcp://IP:Port/DatabaseName
TeraData：
    connect username/password@jdbc:teradata:tcp://IP/DatabaseName
Hive:
    connect hive/hive@jdbc:hive2://IP:Port/DatabaseName
ClickHouse:
	connect default/""@jdbc:clickhouse:tcp://IP:Port/DatabaseName
LinkoopDB:
    connect username/password@jdbc:linkoopdb:tcp://IP:Port/Service_Name
```

### 断开数据库连接
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> connect user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> disconnect
Database disconnected.
```
***

### 会话的切换和保存
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> connect user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名] 
Database connected.
SQL> session save sesssion1
Session saved.
# 这里会把当前会话信息保存到名字为session1的上下文中，session1为用户自定义的名字
# 注意：这里并不会断开程序的Session1连接，当Restore的时候也不会重新连接
SQL> connect user/pass@jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名]
Database connected.
# 连接到第一个会话
SQL> session save sesssion2
Session saved.
# 这里会把当前会话信息保存到名字为session2的上下文中，session2为用户自定义的名字
# 注意：这里并不会断开程序的Session2连接，当Restore的时候也不会重新连接
SQL> session show
+---------------+-----------+-----------------------------------------------+
| Sesssion Name | User Name | URL                                           |
+---------------+-----------+-----------------------------------------------+
| session1      | xxxxx     | jdbc:xxxxx:xxx://xxx.xxx.xxx.xxx/xxxx         |
| session2      | yyyyy     | jdbc:yyyy:xxx://xxx.xxx.xxx.xxx/yyyyy         |         
+---------------+-----------+-----------------------------------------------+
# 显示当前保存的所有会话信息

SQL> session restore sesssion1
Session stored.
# 这里将恢复当前数据库连接为之前的会话1

SQL> session restore sesssion2
Session stored.
# 这里将恢复当前数据库连接为之前的会话2

SQL> session saveurl sesssion3
Session saved.
# 这里会把当前会话信息的URL保存到名字为session3的上下文中，session3为用户自定义的名字
# 注意：这里并不会保持程序的Session3连接，仅仅记录了URL信息，当Restore的时候程序会自动重新连接

SQL> session release sesssion3
Session released.
# 这里将释放之前保存的数据库连接，和针对具体一个连接的DisConnect类似
```
***

### 从脚本中执行SQL语句
我们可以把语句保存在一个SQL文件中，并通过执行SQL文件的方式来执行具体的SQL  
语法格式为：
```
    start [script1.sql] [script2.sql] .... [loop $nlooptime]
```
例如：
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> start aa.api
SQL> ....
SQL> disconnect
这里将执行aa.sql
如果有多个文件，可以依次填写，如SQL> start aa.api bb.sql ....

(base) TestCli 
SQL*Cli Release 0.0.32
SQL> start aa.api loop 10
SQL> ....
SQL> disconnect
这里将执行aa.sql共计10次
如果有多个文件，可以依次填写，如SQL> start aa.api bb.sql .... loop 10

```
### 让程序休息一会
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> sleep 10
SQL> disconnect
Database disconnected.
这里的10指的是10秒，通过这个命令可以让程序暂停10秒钟。
Sleep的做法主要用在一些定期循环反复脚本的执行上
```
### 执行主机的操作命令
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> host date
2020年 10月 29日 星期四 11:24:34 CST
SQL> disconnect
Database disconnected.
这里的date是主机的命令，需要注意的是：在Windows和Linux上命令的不同，脚本可能因此无法跨平台执行
```
### 回显指定的文件
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> echo subtest.sql
-- 这里是subtest.sql
connect admin/123456
select * from cat
SQL> echo off
这里从echo开始，到echo off结束的中间内容并不会被数据库执行，而且会记录在subtest.sql中
同样的操作，这里也可以用来生成一些简单的配置文件，简单的报告信息等
```

### 加载SQL重写配置文件
在TestCli命令行里头，可以通过loadcommandMap命令来加载SQL重写配置文件
```
(base) TestCli 
SQL*Cli Release 0.0.31
SQL> loadcommandMap map1
Mapping file loaded.
这里的map1表示一个重写配置文件，这里可以写多个配置文件的名字，比如loadcommandMap map1,map2,map3，多个文件名之间用逗号分隔
```

### 执行数据库SQL语句
在数据库连接成功后，我们就可以执行我们需要的SQL语句了，对于不同的SQL语句我们有不同的语法格式要求。  
* 对于SQL语句块的格式要求：  
  SQL语句块是指用来创建存储过程、SQL函数等较长的SQL语句  
  SQL语句块的判断依据是：
```
     CREATE | REPLACE ******   FUNCTION|PROCEDURE **** | DECLARE ****
     这里并没有完整描述，具体的信息可以从代码文件中查阅
```
#### 执行SQL语句块
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

* 对于多行SQL语句的格式要求：  
   多行SQL语句是指不能在一行内写完，需要分成多行来写的SQL语句。  
   多行SQL语句的判断依据是： 语句用如下内容作为关键字开头
```
    CREATE | SELECT | UPDATE | DELETE | INSERT | __INTERNAL__ | DROP | REPLACE | ALTER

```
#### 执行多行SQL语句
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

#### 其他SQL语句
* 其他SQL语句  
  不符合上述条件的，即不是语句块也不是多行语句的，则在输入或者脚本回车换行后结束当前语句。  
  结束后的语句会被立刻送到SQL引擎中执行。

#### SQL语句中的注释
* 语句中的注释  
  注释信息分为行注释和段落注释，这些注释信息不会被送入到SQL引擎中，而是会被TestCli直接忽略。  
  
  行注释的写法是： 【 ...SQL...   -- Comment 】  
  即单行中任何【--】标识符后的内容都被理解为行注释信息。  
  
  段落注释的写法是： 【 ...SQL...  /* Comment .... */ 】  
  即单行中任何【/*】标识符和【*/】标识符中的内容都被理解为行注释信息。  
  比如：
```
    SQL> CREATE TABLE TEST_TAB
       > (
       >    ID   CHAR(20),          -- ID信息，这是是一个行注释
       >    COL1 CHAR(20)           -- 第一个CHAR字段，这也是一个行注释
       >  /*  这个表是做测试用的，有两个字段：
       >      ID和COL
       >      这上下的4行内容都是段落注释
       >   */
       > );
    SQL> 

```  
***
### 设置程序的运行选项
通过SET命令，我们可以改变TestCli的一些行为或者显示选项。
```
    SQL> set
    Current set options: 
    +--------------------+----------------------+----------------------+
    | Name               | Value                | Comments             |
    +--------------------+----------------------+----------------------+
    | WHENEVER_ERROR  | CONTINUE             |                      |
    | PAGE               | OFF                  |                      |
    | ECHO               | ON                   |                      |
    | TIMING             | OFF                  |                      |
    | TIME               | OFF                  |                      |
    | OUTPUT_FORMAT      | LEGACY               | TAB|CSV|LEGACY       |
    | CSV_HEADER         | OFF                  | ON|OFF               |
    | CSV_DELIMITER      | ,                    |                      |
    | CSV_QUOTECHAR      |                      |                      |
    | FEEDBACK           | ON                   | ON|OFF               |
    | TERMOUT            | ON                   | ON|OFF               |
    | ARRAYSIZE          | 10000                |                      |
    | SQLREWRITE         | OFF                  | ON|OFF               |
    | LOB_LENGTH         | 20                   |                      |
    | FLOAT_FORMAT       | %.7g                 |                      |
    | DECIMAL_FORMAT     |                      |                      |
    | DATE_FORMAT        | %Y-%m-%d             |                      |
    | DATETIME_FORMAT    | %Y-%m-%d %H:%M:%S %f |                      |
    | TIME_FORMAT        | %H:%M:%S %f          |                      |
    | CONN_RETRY_TIMES   | 1                    | Connect retry times. |
    | OUTPUT_PREFIX      |                      | Output Prefix        |
    | SQL_EXECUTE        | PREPARE              | DIRECT|PREPARE       |
    | JOBMANAGER         | OFF                  | ON|OFF               |
    | JOBMANAGER_METAURL |                      |                      |
    | SCRIPT_TIMEOUT     | -1                   |                      |
    | SQL_TIMEOUT        | -1                   |                      |
    +--------------------+----------------------+----------------------+
    没有任何参数的set将会列出程序所有的配置情况。

```
#### 控制参数解释-ECHO
&emsp; &emsp; 主要的控制参数解释：  
&emsp; &emsp; 1.ECHO    SQL回显标志， 默认为ON，即SQL内容在LOG中回显
```
        SQL> set ECHO ON      # 在LOG中将会回显SQL语句
        SQL> set ECHO OFF     # 在LOG中不会回显SQL语句

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

#### 控制参数解释-WHENEVER_ERROR
&emsp; &emsp; 2. WHENEVER_ERROR  SQL错误终端表示， 用来控制在执行SQL过程中遇到SQL错误，是否继续。 默认是CONTINUE，即继续。   
&emsp; 目前支持的选项有：    
```
       CONTINUE |     遇到SQL语句错误继续执行 
       EXIT     |     遇到SQL语句错误直接退出TestCli程序
```
#### 控制参数解释-PAGE
&emsp; &emsp; 3. PAGE        是否分页显示，当执行的SQL语句结果超过了屏幕显示的内容，是否会暂停显示，等待用户输入任意键后继续显示下一页，默认是OFF，即不中断。

#### 控制参数解释-OUTPUT_FORMAT
&emsp; &emsp; 4. OUTPUT_FORMAT   显示格式， 默认是ASCII(会择机变化成TAB)
&emsp; 目前支持的选项有：
```
      LEGACY    |     显示格式为表格的格式(第三方工具提供，暂时保留，来作为兼容性) 
      CSV      |     显示格式为CSV文件的格式
      TAB      |     显示格式为表格的格式
```
&emsp; 以下是一个例子：
```
       SQL> set output_format legacy
       SQL> select * from test_tab;
       +----+----------+
       | ID | COL2     |
       +----+----------+
       | 1  | XYXYXYXY |
       | 1  | XYXYXYXY |
       +----+----------+
       2 rows selected.
      
       SQL> set output_format csv
       SQL> select * from test_tab;
       "ID","COL2"
       "1","XYXYXYXY"
       "1","XYXYXYXY"
       2 rows selected.
       SQL>           
```
#### 控制参数解释-LOB_LENGTH
&emsp; &emsp; 5. LOB_LENGTH      控制LOB字段的输出长度，默认是20  
&emsp; &emsp; 由于LOB字段中的文本长度可能会比较长，所以默认不会显示出所有的LOB内容到当前输出中，而是最大长度显示LOB_LENGTH值所代表的长度对于超过默认显示长度的，将在输出内容后面添加...省略号来表示   
&emsp; &emsp; 对于BLOB类型，输出默认为16进制格式。对于超过默认显示长度的，将在输出内容后面添加...省略号来表示 
```       
        SQL> set LOB_LENGTH 300     # CLOB将会显示前300个字符
        例子，执行一个CLOB字段查询,CLOB中的信息为ABCDEFGHIJKLMNOPQRSTUVWXYZ
        SQL> set LOB_LENGTH 5
        SQL> SELECT CLOB1 FROM TEST_TAB;
        SQL> ===========
        SQL> =  CLOB1 ==
        SQL> ===========
        SQL>       ABCDE
        SQL> 1 rows selected.
        SQL> set LOB_LENGTH 15
        SQL> =====================
        SQL> =        CLOB1      =
        SQL> =====================
        SQL>    ABCDEFGHIJKLMNO...
        SQL> 1 rows selected.
```
#### 控制参数解释-FEEDBACK
&emsp; &emsp; 6. FEEDBACK      控制是否回显执行影响的行数，默认是ON，显示  
```
       SQL> set feedback on
       SQL> select * from test_tab;
       +----+----------+
       | ID | COL2     |
       +----+----------+
       | 1  | XYXYXYXY |
       | 1  | XYXYXYXY |
       +----+----------+
       2 rows selected.
       SQL> set feedback off
       SQL> select * from test_tab;
       +----+----------+
       | ID | COL2     |
       +----+----------+
       | 1  | XYXYXYXY |
       | 1  | XYXYXYXY |
       +----+----------+
```
#### 控制参数解释-TERMOUT
&emsp; &emsp; 7. TERMOUT       控制是否显示SQL查询的返回，默认是ON，显示  

```
       SQL> set termout on
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
#### 控制参数解释-FLOAT_FORMAT/DECIMAL_FORMAT/DATE_FORMAT/DATETIME_FORMAT/TIME_FORMAT
&emsp; &emsp; 8. FLOAT_FORMAT    控制浮点数字的显示格式，默认是%.7g
```
    SQL>  select abs(1.234567891234) from dual;
    +----------+
    | C1       |
    +----------+
    | 1.234568 |
    +----------+
    1 row selected.
    SQL> set FLOAT_FORMAT %0.10g
    SQL> select abs(1.234567891234) from dual;
    +-------------+
    | C1          |
    +-------------+
    | 1.234567891 |
    +-------------+
    1 row selected.
    类似的参数还有DECIMAL_FORMAT
    
    SQL> set DATE_FORMAT %Y%m%d
    SQL> select CAST('2000-02-02' AS DATE) from dual;
    +-------------+
    | C1          |
    +-------------+
    | 20000111    |
    +-------------+
    1 row selected.
    类似的参数还有DATETIME_FORMAT, TIME_FORMAT
```
#### 控制参数解释-CSV_HEADER/CSV_DELIMITER/CSV_QUOTECHAR
&emsp; &emsp; 9. CSV格式控制  
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
#### 控制参数解释-TIMING/TIME
&emsp; &emsp; 10. 运行时间显示  
```
    TIMING    ON|OFF  控制在SQL运行结束后是否显示执行消耗时间， 默认是OFF
    TIME      ON|OFF  控制在SQL运行结束后是否显示系统当前时间， 默认是OFF
```
#### 控制参数解释-CONN_RETRY_TIMES
&emsp; &emsp; 11. 连接尝试次数  
```
    默认是1，即数据库只尝试一次数据库连接，失败后即退回。
    可以调整到其他数值，来应用不稳定的数据库连接环境
```
#### 控制参数解释-ARRAYSIZE
&emsp; &emsp; 12. 数据读取预Fetch的缓冲区大小  
```
    默认是10000，即数据库每次读取数据的时候，预缓存10000条记录到本地
    如果没有十分必要的需求，不建议修改这个参数。过低的参数将导致程序运行性能下降
```
#### 控制参数解释-SQLREWRITE
&emsp; &emsp; 13. SQLREWRITE  
```
    控制是否启用SQL重写，默认是ON。
    当设置为OFF的时候，无论运行是否指定了COMMANDMAP，映射都不会工作
```
#### 控制参数解释-SQL_EXECUTE
&emsp; &emsp; 14. SQL_EXECUTE  
```
    控制Jpype调用JDBC测试的时候，使用的具体行为方式。有两个可能的选项，分别是DIRECT和PREPARE
    对于DIRECT的行为类似：
        conn.createStatement().execute("sql ...")
    对于PREPARE的行为类似：
        PrepareStatement m_pstmt == conn.PrepareStatement(sql)
        m_pstmt.execute()
    在某些特定的情况下，这个参数将影响显示输出效果。目前正在测试中。
```

#### 控制参数解释-JOBManager, JOBManager_MetaURL
&emsp; &emsp; 15. SQL脚本并发控制  
```
   程序实现了并发的脚本运行，以及对脚本运行中的聚合点支持
   并发运行的时候， 应用程序的角色分为主调度程序和Worker工作程序
   
   通过 SET JOBManager ON的方式可以启用本机的主调度程序。
   在SET JOBManager ON后，通过SET命令查看当前设置，可以看到如下信息：
   | JOBMANAGER         | on                        | ON|OFF               |
   | JOBMANAGER_METAURL | tcp://192.168.3.155:50869 |                      |
   此时的JOBMANAGER_METAURL就是主调度程序所工作的地址
   
   Worker工作程序可以通过手工的方式注册到主调度程序上，也可以通过主调度程序利用JOB的相关命令来启动
   具体的使用方法随后的章节将详细介绍   
```

#### 控制参数-SQL_TIMEOUT，SCRIPT_TIMEOUT
&emsp; &emsp; 15. SQL脚本超时控制
```
   程序实现了超时管理，默认的超时时间为无限制，即不做任何控制
   SCRIPT_TIMEOUT    脚本的最大运行时间，单位为秒，当脚本运行超过这个时间后，脚本将失败，程序将退出
   SQL_TIMEOUT       单个语句的最大运行时间，单位为秒，当单个语句运行超过这个时间后，当前语句将失败，程序将继续
   两个参数可以同时设置，同时生效，也可以根据需要设置其中一个
   
   注意： 
   1： 当发生SQL超时中断后，程序将会启动调用数据库的cancel机制来回退当前运行状态，但不是每个数据库都能支持cancel机制
      所以，不要对超时退出后，数据库的连接状态有所预期，可能（非常可能）会导致后续的所有SQL执行失败
   2： 目前TimeOut仅用于如下函数， Connect,  Execute
   
```

### 在SQL中使用Hint信息
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

    SQL> -- [Hint] LogFilter  ^((?!Error).)*$
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
    SQL> SET SQL_EXECUTE PREPARE|DIRECT

    SQL> -- [Hint] LOOP [LoopTimes] UNTIL [EXPRESSION] INTERVAL [INTERVAL]
    循环执行当前SQL语句一直到表达式EXPRESSION被满足，或者循环次数满足设置要求
    循环执行的次数是LoopTimes，每次循环的间隔是INTERVAL(秒作为单位)
    
```

### 在SQL中使用变量信息
&emsp; &emsp; 在一些场景中，我们需要通过变量来变化SQL的运行  
&emsp; &emsp; 这里提供的解决办法是：   
&emsp; &emsp; * 用set的语句来定义一个变量
```
    SQL> set @var1 value1

    如果value1中包含空格等特殊字符，需要考虑用^将其前后包括，例如：
    SQL> set @var1 ^value1 fafsadfd^
    此时，尖括号内部的字符串将作为参数的值，但尖括号并不包括在内

    注意： value1 是一个eval表达式，可以被写作 3+5, ${a}+1, 等
    如果你要在value1中传入一个字符串，请务必将字符串用‘包括，即'value1'

```
&emsp; &emsp; * 用${}的方式来引用已经定义的变量
```
    SQL> select ${var1} from dual;
    REWROTED SQL> Your SQL has been changed to:
    REWROTED    > select value1 from dual
    -- 这里真实的表达意思是： select value1 from dual, 其中${var1}已经被其对应的变量替换
```


### 在SQL中用内置变量来查看上一个SQL的执行结果
&emsp; &emsp; 有一些场景通常要求我们来下一个SQL指定的时候，将上一个SQL的结果做出参数来执行  
&emsp; &emsp; 这里提供的解决办法是： 在SQL中引入用JQ表达式定义的表达式  
&emsp; &emsp; 例子：  
&emsp; &emsp; &emsp; &emsp; {$LastSQLResult(JQPattern)}
```
    LastSQLResult 是一个包含了上次结果集的JSON表达式，其包含的内容为：
    {
        "desc": [column name1, column name2, ....],
        "rows": rowcount,
        "elapsed": sql elapsed time,
        "result": [[row1-column1 , row1-column2,...] [row2-column1 , row2-column2,...] ...]
    }
    SQL>  -- 返回上一个SQL执行影响的记录数量
    SQL>  select '${LastSQLResult(.rows)}' from dual;
    REWROTED SQL> Your SQL has been changed to:
    REWROTED    > select '1' from dual
    +-----+
    | '1' |
    +-----+
    | 1   |
    +-----+
    1 row selected.
    
    SQL>  -- 返回上一个SQL结果记录集的零行零列内容    
    SQL> select '${LastSQLResult(.result.0.0)}' from dual;
    REWROTED SQL> Your SQL has been changed to:
    REWROTED    > select '1' from dual
    +-----+
    | '1' |
    +-----+
    | 1   |
    +-----+
    1 row selected.

    支持的JQ过滤表达式：
        dict key过滤           .key
        dict key列表           .keys()
        dict value列表         .values()
        dict key,value对       .iterms()
        list过滤                .3 或 .[3]
        list负索引              .-2 或 .[-2]
        list切片1               .2:6 或 .[2:6]
        list切片2               .2: 或 .[2:]
        list切片3               .:6 或 .[:6]
        list step1             .1:6:2 或 .[1:6:2]
        list step2             .1::2 或 .[1::2]
        list step3             .::2 或 .[::2]
        string过滤              ..与list相同
        string切片              ..与list相同
        string切片step          ..与list相同

   
```
### 在TestCli中完成简单的循环语句
```
    通过使用SQLHint，我们可以实现简单的语句循环。
    例子：
    SQL> -- [Hint] LOOP 100 UNTIL False INTERVAL 2
    Select * From Cat;
    -- 以上的语句将以间隔2秒执行一次的节奏执行100次的“Select * From Cat”

    SQL> -- [Hint] LOOP 100 UNTIL ${LastSQLResult(.result.0.0)}>10 INTERVAL 2
    Select * From Cat;
    以上的语句将以间隔2秒执行一次的节奏执行“Select * From Cat”
    一直执行到100次或者该语句返回结果集的第一行第一内内容大于10
    其中： ${LastSQLResult(.result.0.0)}是一个标准的JQ表达式，写法参考__internal__ test assert中写法说明
``` 
### 定义TestCli的初始化文件
```
    TestCli在执行的时候可以指定初始化文件，初始化文件会在真正的脚本执行之前被执行
    可以通过以下三种方式来定义TestCli的初始化文件：
    1： 通过在TestCli的命令行参数中执行，   
    OS>  TestCli --profile xxxx
    2. 通过创建TestCli_HOME/profile/default文件，并在其中输入相关信息
    3. 通过修改程序的安装目录中对应文件来指定，即<PYTHON_PACKAGE>/TestCli/profile/default
    同时存在上述3类文件的时候，3类文件都会被执行。叠加执行的顺序是：3，2，1

    除非打开调试模式，否则初始化脚本的执行不会有任何输出日志，不会影响到日志校验等

```

### 用TestCli来产生测试数据文件
```
   SQL> __internal__ DATA SET HDFSUSER [USERNAME]
   这里将指定随后操作HDFS操作时使用的用户名（程序使用InSecureClient来上传文件，所以无需口令)
     
   SQL> __internal__ DATA SET SEEDFILE DIR [DIRECTORY]
   这里将指定随后程序加载种子Seed文件时所使用的目录，如果不指定，默认目录是TestCli_HOME\data
   
   SQL> __internal__ DATA CREATE [string|integer] SEEDDATAFILE [SeedName] LENGTH [row length] ROWS [row number]  
      > WITH NULL ROWS [null rows number];
   如果指定了SEEDFILE的目录，则会在目录下创建seed文件。否则，会在$TestCli_HOME/data下创建seed文件，用来后续的随机函数

    [string|integer]          是字符型随机数据文件还是数字型随机数据文件
    [SeedName]                数据种子的名称，根据需要编写，应简单好记
    [row length]              数据种子中每行数据的最大长度
    [row number]              数据种子的行数
    [null rows number]        在该数据文件row number的行数中有多少行为空行

   __internal__ DATA CREATE [MEM|FS|HDFS] FILE [FileName]
   (
     此处为宏代码

     如果参数中提供了ROWS：
         这里将把括号内内容理解为一行内容，其中的换行符在处理过程中被去掉
         相关信息将被完成宏替换后，重复ROWS行数后构成一个文件
     如果参数没有提供了ROWS：
         这里将把括号内内容理解为多行内容
         相关信息将被完成宏替换后构成一个文件
   ) ROWS [number of rows];
   
   MEM:  表示文件将被创建在内存中，程序退出后，文件将不复存在
   FS:   表示文件将被创建在文件中，需要注意的是，这里的目录不是真实的OS目录，而是一个相对于工作目录的相对目录
   HDFS: 表示文件将被创建在HDFS上，这里需要远程的HDFS服务器开启WebFS的功能
         文件格式例子：  http://nodexx:port/dirx/diry/xx.dat
         其中port是webfs的port，不是rpc的port， TestCli并不支持rpc协议
   这里语句的开头：  __internal__ 是必须的内容，固定写法
   宏代码的格式包括：
     {identity(start_number)}                  表示一个自增字段，起始数字为start_number
                                               如果一行内有多个identity，他们将分别自增
     {identity_timestamp(start_time,fmt,step)} 表示一个自增的时间戳
                                               起始数字为start_time，格式位fmt（可以省略，默认是%Y-%m-%d %H:%M:%S)，
                                               每次自增长度为Step， Step的单位可以是s,ms,ns (默认为ms)
                                               s: 秒 ;  ms: 毫秒； ns: 纳秒
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
     {random_from_seed(seedname,length)}                  表示从seed文件中随机选取一个内容，并且最大长度限制在length, 此时seedname不要引号
     {random_from_seed(seedname,start_pos, length)}       表示从seed文件中随机选取一个内容，内容从start_pos开始(第一个位置为0)， 并且最大长度限制在length, 此时seedname不要引号
     使用random_from_seed需要用到seed文件，必须提前准备到$TestCli_HOME/data下，用来后续的随机函数  

   SQL> __internal__ DATA CREATE [MEM|FS|HDFS] FILE [LocalFileName] FROM [MEM|FS|HDFS] FILE [RemoteFileName]
   如果是HDFS文件，则文件名格式为： http://HDFSHOST:HDFSRPCPORT/RemoteFileName
   会下载相应文件, 并保存到指定目录，即完成文件复制

   例子：
   SQL> __internal__ DATA CREATE FS FILE abc.txt
      > (
      > {identity(10)},'{random_ascii_letters(5)}','{random_ascii_lowercase(3)}'
      > ) ROWS 3;
    会在当前的文件目录下创建一个名字为abc.txt的文本文件，其中的内容为：
    10,'vxbMd','jsr'
    11,'SSiAa','vtg'
    12,'SSdaa','cfg'

   SQL> __internal__ DATA CREATE FS FILE abc.txt
      > (
      > {identity(10)},'{random_ascii_letters(5)}','{random_ascii_lowercase(3)}'
      > {identity(10)},'{random_ascii_letters(5)}','{random_ascii_lowercase(3)}'
      > );
    会在当前的文件目录下创建一个名字为abc.txt的文本文件，其中的内容为：
    10,'vxbMd','jsr'
    11,'SSiAa','vtg'

```
### 用TestCli工具操作Kafka
```
   TestCli工具可以操作Kafka，建立、删除Topic，查看Topic的状态，给Topic发送信息

   提前准备：
   SQL> __internal__ kafka connect server [bootstrap_server];
   连接一个Kafka服务器，格式位nodex:port1,nodey:port2....
   注意，这里并没有校验服务器的实际信息是否正确。

   SQL> __internal__ kafka create topic [topic name] 
        [ Partitions [number of partitions] 
          replication_factor [number of replication factor] 
          timeout [timeout of creation]
          .... kafka valid configuration ...
        ];
   创建一个kafka的Topic.
   其中： timeout of creation 可以省略， 默认是60
         number of partitions 可以省略， 默认是16
         number of replication factor 可以省略， 默认是1
         kafka valid configuration    可以为1个或者多个有效的配置参数，比如retention.ms
   例子： __internal__ kafka create topic mytopic;
   
   SQL> __internal__ kafka get info topic [topic name] group [gruop id];
   其中： group id 可以省略
   获得消息队列的高水位线和低水位线
    +-----------+-----------+-----------+
    | Partition | minOffset | maxOffset |
    +-----------+-----------+-----------+
    | 0         | 0         | 1         |
    | 1         | 0         | 1         |
    +-----------+-----------+-----------+
   例子： __internal__ kafka get info topic mytopic Partition 0 group abcd;

   SQL> __internal__ kafka produce message from file [text file name] to topic [topic name];
   将指定文本文件中所有内容按行发送到Kafka指定的Topic中
   例子： __internal__ kafka produce message from file Doc.md to topic Hello;

   SQL> __internal__ kafka consume message from topic [topic name] to file [text file name];
   将Kafka指定的Topic中所有消息消费到指定文本文件中
   例子： __internal__ kafka consume message from topic Hello to file xxx.md;

   SQL> __internal__ kafka produce message topic [topic name]
       > (
       >    [message item1]
       >    [message item2] 
       >    [message item3]
       > );
   将SQL中包含的Message item发送到kafka指定的topic中
   上述的例子，将发送3条消息到服务器。

   SQL> __internal__ kafka produce message topic [topic name]
       > (
       >    [message part1]
       >    [message part2] 
       >    [message part3]
       > ) rows [num of rowcount]
       > frequency [num of frequency];   
   将SQL中包含的Message part重复num of rowcount发送到kafka指定的topic中
   上述的例子，将发送num of rowcount条消息到服务器。
   其中: num of frequency 表示每秒最多发送的消息数量。 可以省略，省略表示不对发送频率进行限制
        具体message part的写法参考前面描述的创建数据文件的例子
   注意：frequency的计数器并不是精准计数器，不排除1~2秒的误差

   SQL> __internal__ kafka drop topic [topic name] timeout [timeout of deletion];
   其中： timeout of deletion 可以省略， 默认是1800
   删除指定的topic
```

### 用TestCli工具操作HDFS
```
    SQL> __internal__ hdfs connect [hdfs webui url] with user [hdfs user name]
    用HDFSweb连接到指定的HDFS上
    例子：
    SQL> __internal__  hdfs connect http://localhost:9870/user/testuser/abcd with user testuser;
    Hdfs Server set successful.
    这里的/user/testuser/abcd将作为后续HDFS操作的根目录

    SQL> __internal__ hdfs cd [hdfs new dir]
    切换当前HDFS的主目录到新的目录上
    例子：
    SQL> __internal__  hdfs cd testuser/abcd;
    Hdfs root dir change successful.
    这里的testuser/abcd将作为后续HDFS操作的根目录

    SQL> __internal__ hdfs status [hdfs path]
    获取指定的HDFS文件信息
    例子：
    SQL> __internal__  hdfs status aa.log;
    HDFS file status:
    +--------+------------+-------+--------+------+---------------------+
    | Path   | Permission | owner | group  | Size | Modified            |
    +--------+------------+-------+--------+------+---------------------+
    | aa.log | -rw-r--r-- | ldb   | ldbp67 | 1148 | 2021-03-05 11:11:41 |
    +--------+------------+-------+--------+------+---------------------+
    Total 1 files listed.

    SQL> __internal__ hdfs list [hdfs path] 
    显示远程的HDFS文件目录信息。 hdfs_path可以省略，省略情况下显示当然目录信息。
    例子：
    SQL> __internal__  hdfs list;
    HDFS file List:
    +-------+------------+--------+--------+------+---------------------+
    | Path  | Permission | owner  | group  | Size | Modified            |
    +-------+------------+--------+--------+------+---------------------+
    | 111   | drwxr-xr-x | ldbp67 | ldbp67 | 0    | 2021-03-05 09:26:56 |
    | aa.sh | -rw-r--r-- | ldbp67 | ldbp67 | 363  | 2021-03-05 09:07:35 |
    +-------+------------+--------+--------+------+---------------------+
    Total 2 files listed.

    SQL> __internal__ hdfs rm [hdfs path]
    删除指定的HDFS文件信息，如果需要删除多个文件，可以提供文件通配符
    例子：
    SQL> __internal__  hdfs rm aa.log;
    Hdfs file deleted successful.

    SQL> __internal__ hdfs makedirs [hdfs path]
    建立需要的HDFS路径

    SQL> __internal__ hdfs upload [local file] [remote file]
    上传本地文件到远程的HDFS文件目录中

    SQL> __internal__ hdfs download [remote file] [local file] 
    下载远程的HDFS文件到本地文件目录中

```

# 以上文件还没有更新，请等等哈
***    
### 在脚本中使用ASSERT语句来判断运行结果
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

###  在脚本中嵌入python语法
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
但是在实际的应用中，如果业务的逻辑比较复杂，建议将业务逻辑代码写成独立的Python文件，并通过插件（_LOAD PLUGIN)的方式来导入。  
通过插件导入的方式，将使得程序变得更容易复用，而且可读性有所提高。  

需要注意的是： 在一个测试脚本运行的过程中，所有的python内嵌语法都拥有共同的变量空间。   
即如何保证变量空间的不冲突是写业务逻辑代码的时候需要保证的。    

#### 内置Python语法中的系统预制变量
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

***    
### 加载附加的命令行映射文件
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
### 加载附加的外挂插件
为了让测试框架能够支持更多的扩展，testcli支持你将自己写好的Python程序作为一个插件的方式放入到系统中。  
虽然这是一个可能解决问题的近乎外能良药，但是这么做会导致一定的测试脚本可读性下降。需要你在使用的时候小心谨慎。  
```
   _LOAD PLUGIN <插件文件的位置>   
```
这里的插件文件是一个有效的Python文件，python文件可能包含有类的定义，全局函数的定义等等。  
以下是一个简单插件文件的例子：  
```
(base) C:\>type testplugin.py
class cc:
    def welcome(self, message: str):
        if self:
            pass
        return 'thx ' + message


def fun(b):
    return "b" + str(b)
```
通过在testcli中执行LOAD PLUGIN命令可以完成对插件文件的加载
```
(base) C:\>testcli
TestCli Release 0.0.8
SQL> _load plugin testplugin.py
Plugin module [cc] loaded successful.
Plugin function [fun] loaded successful.
Plugin file loaded successful.
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
### 加载数据库驱动
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
### 程序的并发和后台执行
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
   _JOB WAIT <JOB的名字 | ALL> 
   _JOB SHOW <JOB的名字 | ALL> 
   _JOB START <JOB的名字 | ALL>   
   _JOB ABORT <JOB的名字 | ALL> 
   _JOB SHUTDOWN <JOB的名字 | ALL>   
   _JOB CREATE <JOB的名字> { <JOB选项名称>=><JOB选项值>}
   _JOB SET <JOB的名字> { <JOB选项名称>=><JOB选项值>}
   _JOB REGISTER WORKER TO <JOB名称>
   _JOB DEREGISTER WORKER
```
#### 创建后台任务脚本
在很多时候，我们需要TestCli来帮我们来运行数据库脚本，但是又不想等待脚本的运行结束。    
create可以有多个参数：      
参数1：     JOB的名称  
参数2-..:   JOB的各种参数，要求成对出现 ParameterName  ParameterValue
```
SQL> _JOB job create jobtest;
JOB [jobtest] create successful.
SQL> _JOB job create jobtest2 loop 4;
JOB [jobtest2] create successful.
SQL> _JOB job create jobtest3 loop 4 parallel 2;
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
SQL> _JOB job set jobtest parallel 2;
JOB [jobtest] set successful.
SQL> _JOB job set jobtest loop 4;
JOB [jobtest] set successful.
SQL> _JOB job set jobtest script bb.sql;
JOB [jobtest] set successful.
SQL>
```

#### 查看后台任务脚本的运行情况
通过show可以查看我们之前提交情况，脚本的运行情况，运行的开始时间，运行的结束时间，当前正在运行的SQL等。
```
SQL> -- 查看JOB整体情况
SQL> _JOB job show all;
+----------+-----------+-------------+-------------+---------------+---------------------+------------+----------+
| job_name | status    | active_jobs | failed_jobs | finished_jobs | submit_time         | start_time | end_time |
+----------+-----------+-------------+-------------+---------------+---------------------+------------+----------+
| jobtest  | Submitted | 0           | 0           | 0             | 2020-12-02 11:00:41 | None       | None     |
+----------+-----------+-------------+-------------+---------------+---------------------+------------+----------+
Total 1 Jobs.
这里可以看到目前1个脚本已经提交.

SQL> -- 查看JOB具体情况 
SQL> _JOB job show jobtest;
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
#### 如何启动后台任务脚本
通过start的方式，我可以启动全部的后台任务或者只启动部分后台任务
```
SQL> _JOB jobmanager on
SQL> _JOB job start all;
1 Job Started.
这里会将你之前提交的所有后台脚本都一次性的启动起来
SQL> _JOB job start jobtest;
1 Job Started.
这里只会启动JOB名称为jobtest的后台任务
随后，再次通过show来查看信息，可以注意到相关已经启动
```

#### 如何停止后台任务脚本
在脚本运行过程中，你可以用shutdown来停止某个某个任务或者全部任务，
```
SQL> _JOB job shutdown all;
Total [1] job shutdowned.
这里会将当前运行的所有后台脚本都停止下来
SQL> _JOB job shutdown jobtst;
Total [1] job shutdowned.
注意： shutdown并不会真的终止你当前正在运行的作业，但是在这个作业之后的所有作业不再执行，要求循环执行的脚本也不再循环。
      只有在子任务完成当前作业后，shutdownjob才能完成。
      这个意思是说，如果你有一个比较大的长SQL作业，shutdownjob并不能很快的终止任务运行。
```
#### 如何强行停止后台任务脚本
在脚本运行过程中，你可以用abort来强行停止某个某个任务或者全部任务，
```
SQL> _JOB job abort all;
Total [1] job aborted.
这里会将当前运行的所有后台脚本都停止下来
SQL> _JOB job abort jobtst;
Total [1] job aborted.
```
#### 等待后台任务脚本运行结束
在脚本运行过程中，你可以用wait来等待后台脚本的运行结束
```
SQL> _JOB job wait all;
All jobs [all] finished.
SQL> _JOB job wait jobtest;
All jobs [jobtest] finished.
waitjob不会退出，而是会一直等待相关脚本结束后再退出
```
#### 如何让若干的Worker应用程序保持聚合点
主调度程序脚本：
```
SQL> _JOB jobmanager on
SQL> _JOB job create mytest loop 2 parallel 2 script slave1.sql tag group1;
SQL> _JOB job create mytest2 loop 2 parallel 2 script slave2.sql tag group1;
SQL> _JOB job start mytest;
SQL> _JOB job start mytest2;
SQL> _JOB job wait all;
```

Worker应用程序脚本(slave1.sql, slave2.sql)：
```
-- 两个Worker程序(slave1.sql,slave2.sql)将会同时结束all_slave_started的聚合点
SQL> _JOB job timer all_slave_started;
SQL> do some sql
SQL> _JOB job timer slave_point1;
SQL> do some sql
SQL> _JOB job timer slave_finished;
```

### 脚本中使用COMPARE命令来比较文件差异性
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
   _COMPARE SET ALGORITHM [LCS | COMPARE_MYERS]
   _COMPARE SET WORK <需要比对文件的字符集信息，默认为UTF-8>
   _COMPARE SET REFERENCE <比对参考文件的字符集信息，默认为UTF-8>

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
5. OUTPUT 将比对的结果输出到控制台或者一个DIFF文件中
   1. 也可以即输出到控制台，也输出到DIFF文件中。设置方法： _COMPARE SET OUTPUT CONSOLE DIFFFILE;

### 脚本中使用SSH命令来远程执行命令以及上传、下载文件
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
    _SSH SFTP GET <本地文件名> <远程文件名>
    _SSH SFTP REMOVE <需要删除的远程文件名>
    _SSH SFTP RENAME <需要更名的远程文件名> <更名后的远程文件名>
    _SSH SFTP LISTDIR <需要列出详细信息的远程目录名>
    _SSH SFTP TRUNCATE <需要改变大小的远程文件名> <改变后的文件名>

    TODO:
      LISTDIR 需要提供详细信息
      GET 可以默认本地文件名, 可以GET到本地的一个目录中
      PUT 可以PUT到一个目录下，也可以默认PUT到远程的当前目录下
      CHOWN 支持用户名和组名的写法
      CHMOD 支持+x, +w等的写法
      GET 可以用正则表达式下载一系列文件
      PUT 可以用正则表达式上传一系列文件
```

### 使用spool命令来将当前执行结果输出到文件中
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
### 脚本中使用ECHO来生成简易的文件
1. ECHO主要用来快速的生成一些小的脚本和文件。例如：
    ```
    _ECHO <输出的文件名>
        <文件内容>
    _ECHO OFF 
   
   TODO： ECHO中能够处理{{}}的替代信息，能够支持APPEND操作
    ```
2. 这里文件内容的所有东西都将被直接输出到指定的文件中，包括换行符等信息
*** 
### 程序退出
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
### 程序中用到的环境变量
程序中我们定义了一些环境变量，用来支撑客户部署和调试的需要。  

#### TESTCLI_DEBUG
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

#### TESTCLI_CONF
用来定义程序配置文件的目录。  
默认的配置文件是程序安装目录的conf/testcli.ini。 即PYTHON_HOME/lib/python36/site-packages/testcli/conf/testcli.ini.  
```
   export TESTCLI_CONF=/tmp/mycli.conf
   # Windows下用：  set TESTCLI_CONF \Temp\mycli.conf  
```

#### TESTCLI_JLIBDIR
用来定义程序需要加载的数据源JAR包的位置（文件夹名称）    
默认的配置文件是程序安装目录的jlib。 即PYTHON_HOME/lib/python36/site-packages/testcli/jlib.  
```
   export TESTCLI_JLIBDIR=/tmp/myjlib
   # Windows下用：  set TESTCLI_JLIBDIR \Temp\myjlib  
```
如果实际部署中用到了客户化的JAR包，可以通过定义TESTCLI_CONF和TESTCLI_JLIBDIR来指定客户化文件的位置，而不用修改PYTHON系统目录。  


#### TESTCLI_CONNECTION_URL
用来定义程序的默认数据库连接地址  
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
