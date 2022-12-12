# TestCli 快速说明

TestCli 是一个主要用Python完成的，命令快速的测试工具。  
设计目的：  
    1： 满足数据库方面的相关功能测试、压力测试需要。  
    2： 满足API方面的相关功能测试、压力测试需要。  
    3： 能够作为一个日常小工具，进行数据库的日常操作。    
    4： 能够根据需要快速、灵活的生成测试需要的随机数据。   
    5： 能够操作Kafka消息队列。   
    6： 能够操作HDFS上的文件。  
    7： 完成基于执行结果比对的回归测试校验。

程序可以通过JPype连接数据库的JDBC驱动。      

TestCli 目前可以支持的数据库有：  
   * Oracle,MySQL,PostgreSQL,SQLServer,TeraData, Hive, H2等主流通用数据库  
   * 达梦，神通， 金仓， 南大通用，LinkoopDB, 快立方等众多国产数据库  
   * ClickHouse数据库      
   * 其他符合标准JDBC规范的数据库  
   
TestCli 目前支持的数据类型有：
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

### 谁需要使用这个工具

需要通过SQL语句来查看、维护数据库的。  
需要通过API语句来完成业务的。  
需要进行各种数据库功能测试、压力测试的。  
需要进行各种API功能测试、压力测试的。  
需要用统一的方式来连接各种不同数据库的。  
需要在一个测试程序内部组合使用数据库请求、API请求的。  


### 为什么要设计这个工具
这个工具的存在目的不是为了替代各种数据库的命令行工具，如Oracle的SQLPlus，MYSQL的mysql等  
这个工具的存在目的不是为了替代PostMan，JMeter等测试工具。  
这个工具的存在目的是在尽可能地兼容这些命令行工具的同时提供测试工作需要的相关特性。    
这些特性包括：  
1：并发脚本的支持，通过在脚本中使用JOBManager，可以同时执行多个脚本，同时利用时间戳还可以同步脚本之前的行为。    
2：一些internal的命令，可以完成数据库之外的相关操作。  


***
### 安装
安装的前提有：
   * 有一个Python 3.6以上的环境
   * 能够连接到互联网上， 便于下载必要的包
   * 安装JDK8或者JDK11  
   * 对于Windows平台，需要提前安装微软的C++编译器（jpype1使用了JNI技术，需要动态编译）  
   * 对于Linux平台，  需要提前安装gcc编译器，以及Python3的开发包（原因同上）  
     yum install -y gcc-c++ gcc  
     yum install python3<?>-devel(在Anaconda环境下，这一步不是必须的. ?是具体的Python版本，根据自己的环境决定)
   * 对于MAC平台，  需要提前安装gcc编译器    
     brew install gcc  

依赖的第三方安装包：  
   * 这些安装包会在robotslacker-TestCli安装的时候自动随带安装
   * click                    : Python的命令行参数处理
   * hdfs                     : HDFS类库，支持对HDFS文件操作
   * JPype1                   : Python的Java请求封装，用于完成JDBC请求调用  
   * paramiko                 : Python的SSH协议支持，用于完成远程主机操作  
   * prompt_toolkit           : 用于提供包括提示符功能的控制台终端的显示样式
   * setproctitle             : Python通过setproctitle来设置进程名称，从而在多进程并发时候给调试人员以帮助
   * urllib3                  : HTTP客户端请求操作   

   * antlr4-python3-runtime   : 编译需要，用来编译生成Antlr4的Python文件

利用PIP来安装：
```
   pip install -U robotslacker-testcli
```

安装后步骤-更新驱动程序配置：  
   * 根据你的需要， 放置自己的jar包到 <PYTHON_HONE>/../site-packages/testcli/jlib下
   * github上提供的仅仅是一些测试用的Jar包，如果你有自己的需要，可以用自己的文件覆盖上述下载的文件
   * 根据需要修改testCli/conf/testCli.ini文件：  
   * 默认情况下，这个文件不需要修改
   * 如果你需要定义自己内网的驱动程序下载服务器，你需要修改这个文件
   * 如果你需要定义自己的数据库驱动，你需要修改这个文件
   
***

### 第一次使用
安装后直接在命令下执行TestCli命令即可。  
如果你的<PYTHON_HOME>/Scripts没有被添加到当前环境的$PATH中，你可能需要输入全路径名  
```
(base) >TestCli
SQL*Cli Release 0.0.32
SQL> 
```
如果你这里看到了版本信息，那祝贺你，你的程序安装成功了

```
(base) >TestCli
SQL*Cli Release 0.0.32
SQL> connect mem;
SQL> Connected.
```
如果你下载了至少H2的驱动程序，执行这个命令将连接到内置的H2数据库中，如果你看到了Connected信息，那再一次祝贺你，你的程序基本工作正常。 

***

### 驱动程序的下载和配置
TestCli是一个基于JDBC/ODBC的数据库工具，基于JDBC操作数据库的前提当前环境下有对应的数据库连接jar包，基于ODBC前提是安装了相关的ODBC驱动。  
#### 驱动程序的配置
配置文件位于TestCli的安装目录下的conf目录中，配置文件名为:TestCli.conf  
配置例子:
```
[driver]
oracle=oracle_driver
mysql=mysql_driver
.... 

[oracle_driver]
filename=ojdbc8.jar
downloadurl=http://xxxxxx/driver/ojdbc8.jar
md5=1aa96cecf04433bc929fca57e417fd06
driver=oracle.jdbc.driver.OracleDriver
jdbcurl=jdbc:oracle:thin:@${host}:${port}/${service}

[mysql_driver]
filename=mysql-connector-java-8.0.20.jar
downloadurl=http://xxxxx/driver/mysql-connector-java-8.0.20.jar
md5=48d69b9a82cbe275af9e45cb80f6b15f
driver=com.mysql.cj.jdbc.Driver
jdbcurl=jdbc:mysql://${host}:${port}/${service}
jdbcprop=socket_timeout:360000000
odbcurl=DRIVER={driver_name};SERVER=${host};PORT=${port};DATABASE=${service};UID=${username};PWD=${password};
```

如果数据库要新增其他数据库的连接，则应仿效上述配置例子。  
其中：  
* 所有的数据库名称及配置项名称均应该出现在[driver]的配置项中  
  如果某一种数据库连接需要不止一个jar包，则这里应该配置多个配置项  
  例如：   mydb=mydb1_driver1, mydb1_driver2
* 数据库的具体配置应该在具体的配置项中  
  filename：      可选配置项，jar包具体的名字  
  driver:         可选配置项，数据库连接的主类  
  jdbcurl:        可选配置项，jdbc连接字符串，其中${host}${port}${service}分别表示数据库连接主机，端口，数据库名称  
  downloadurl：   可选配置项，若本地不存在该文件，则文件下载需要的路径  
  md5:            可选配置项，文件下载校验MD5    
  jdbcprop:       可选配置项，若该数据库连接需要相应的额外参数，则在此处配置
  odbcurl:        可选配置项，若该数据库连需要通过ODBC连接数据库，则在此处配置      
  jdbcurl和odbcurl两个参数，至少要配置一个。若配置jdbcurl，则jdbc对应的filename,driver也需要配置  
* 基于这个原则，最简化的运行配置应该为：  
```
[driver]
oracle=oracle_driver
mysql=mysql_driver

[oracle_driver]
filename=ojdbc8.jar
driver=oracle.jdbc.driver.OracleDriver
jdbcurl=jdbc:oracle:thin:@${host}:${port}/${service}

[mysql_driver]
filename=mysql-connector-java-8.0.20.jar
driver=com.mysql.cj.jdbc.Driver
jdbcurl=jdbc:mysql://${host}:${port}/${service}
```
#### 驱动程序的下载
基于上述参数文件的正确配置，可以使用--syncdriver的方式从服务器上来更新数据库连接需要的jar包  
例子：    
```
(base) C:\Work\linkoop\TestCli>TestCli --syncdriver
Checking driver [oracle] ...
File=[ojdbc8.jar], MD5=[1aa96cecf04433bc929fca57e417fd06]
Driver [oracle_driver] is up-to-date.
Checking driver [mysql] ...
File=[mysql-connector-java-8.0.20.jar], MD5=[48d69b9a82cbe275af9e45cb80f6b15f]
Driver [mysql_driver] is up-to-date.
```
### 程序的命令行参数
```
(base) TestCli --help
Usage: TestCli [OPTIONS]

Options:
  --version       Output TestCli's version.
  --logon TEXT    logon user name and password. user/pass
  --logfile TEXT  Log every query and its results to a file.
  --execute TEXT  Execute SQL script.
  --nologo        Execute with silent mode.
  --xlog TEXT     SQL performance Log.
  --syncdriver    Download jdbc jar from file server.
  --clientcharset TEXT  Set client charset. Default is UTF-8.
  --resultcharset TEXT  Set result charset. Default is same to clientcharset.
  --help          Show this message and exit.
```  
--version 用来显示当前工具的版本号
```
(base) TestCli --version
Version: 0.0.32
```
--logon  用来输入连接数据的的用户名和口令
```
(base) TestCli --logon user/pass
Version: 0.0.32
Driver loaded.
Database connected.
SQL>
如果用户、口令正确，且相关环境配置正常，你应该看到如上信息。

user/pass : 数据库连接的用户名和口令  

成功执行这个命令的前提是你已经在环境变量中设置了数据库连接的必要信息。  
这里的必要信息包括：
环境变量：  TestCli_CONNECTION_URL  
参数格式：  jdbc:[数据库类型]:[数据库通讯协议]://[数据库主机地址]:[数据库端口号]/[数据库服务名]  
```
--logfile   用来记录本次命令行操作的所有过程信息  
这里的操作过程信息包含你随后在命令行里头的所有输出信息。  
如果你在随后的命令行里头设置了SET ECHO ON，那么记录里头还包括了你所有执行的SQL语句原信息  
文件输出的字符集将根据参数resultcharset中的设置来确定    
```
(base) TestCli --logon user/pass --logfile test.log
Version: 0.0.32
Driver loaded.
Database connected.
set echo on
select * from test_tab;
+----+----------+
| ID | COL2     |
+----+----------+
| 1  | XYXYXYXY |
| 1  | XYXYXYXY |
+----+----------+
SQL> exit
Disconnected.

(base) type test.log
Driver loaded.
Database connected.
SQL> select * from test_tab;

+----+----------+
| ID | COL2     |
+----+----------+
| 1  | XYXYXYXY |
| 1  | XYXYXYXY |
+----+----------+
2 rows selected.
SQL> exit
Disconnected.
```
--execute 在TestCli启动后执行特定的SQL脚本  
为了能够批处理一些SQL语句，我们通常将这批SQL语句保存在一个特定的文件中，这个文件的习惯后缀是.sql  
通过execute参数，可以让TestCli来执行这个脚本，而不再需要我们一行一行的在控制台输入  
脚本字符集将根据参数clientcharset中的设置来确定
```
(base) type test.sql
select * from test_tab;

(base) TestCli --logon user/pass --execute test.sql
Version: 0.0.32
Driver loaded.
Database connected.
set echo on
select * from test_tab;
+----+----------+
| ID | COL2     |
+----+----------+
| 1  | XYXYXYXY |
| 1  | XYXYXYXY |
+----+----------+
SQL> exit
Disconnected.
注意： 即使你的SQL脚本中不包含Exit语句，在TestCli执行完当前脚本后，他也会自动执行exit语句
如果SQL脚本中不包含数据库驱动加载或者数据库连接语句，请在执行这个命令前设置好相应的环境变量信息
```
--nologo    这是一个选项，用来控制TestCli是否会在连接的时候显示当前的程序版本
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL>   
区别：
(base) TestCli --nologo
SQL>
```
--xlog  输出SQL运行日志  
这里的运行日志不是指程序的logfile，而是用CSV文件记录的SQL日志，  
这些日志将作为后续对SQL运行行为的一种分析  
运行日志共包括如下信息：  
1、Script       运行的脚本名称  
2、StartedTime  SQL运行开始时间，格式是：%Y-%m-%d %H:%M:%S    
3、elapsed      SQL运行的消耗时间，这里的单位是秒，精确两位小数        
4、RAWCommand   原始的Command信息   
4、Command      运行的命令，注意：这里可能和RAWCommand不同，不同的原因是命令可能会被重写规则改写    
5、SQLStatus    SQL运行结果，0表示运行正常结束，1表示运行错误    
6、ErrorMessage 错误日志，在SQLStatus为1的时候才有意义    
7、Scenario     程序场景名称，这里的内容是通过在SQL文件中指定-- [Hint] Scenario:name的方式来标记的Scenario信息  
说明：上述信息都有TAB分隔，其中字符信息用单引号包括，如下是一个例子：  
```
Script  Started elapsed SQLPrefix       SQLStatus       ErrorMessage    Scenario
sub_1.sql 2020-05-25 17:46:23       0.00        loaddriver localtest\linkoopdb-jdbc-2.3.      0             Scenario1
sub_1.sql 2020-05-25 17:46:23       0.28        connect admin/123456  0             Scenario1
sub_1.sql 2020-05-25 17:46:24       0.00        SET ECHO ON   0             Scenario1
sub_1.sql 2020-05-25 17:46:24       0.00        SET TIMING ON 0             Scenario2
sub_1.sql 2020-05-25 17:46:24       0.01        LOADCOMMANDMAP stresstest 0             Scenario2
sub_1.sql 2020-05-25 17:46:24       0.92        ANALYZE TRUNCATE STATISTICS   0             Scenario3
sub_1.sql 2020-05-25 17:46:25       0.02        SELECT count(SESSION_ID)  FROM INFORMATI      0             Scenario3
sub_1.sql 2020-05-25 17:46:25       1.37        drop user testuser if exists cascade  0             Scenario3
sub_1.sql 2020-05-25 17:46:26       0.54        CREATE USER testuser PASSWORD 123456        0             Scenario3
```
***
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

重写文件的查找顺序：
   1.  以map1为例子，如果map1是一个全路径或者基于当前目录的相对目录，则以全路径或相对目录为准。这时候参数应该带有后缀
   2：  如果依据全路径没有找到，则会尝试在脚本所在的目录进行相对目录的查找。这时候参数不能够带后缀，查找的后缀文件名是.map
   同时存在多个配置的情况下，配置会被叠加

启用SQL重写的方法：
   1.   在命令行里面，通过TestCli --commandMap map1的方式来执行重写文件的位置
   2.   定义在系统环境变量TestCli_COMMANDMAPPING中指定。 如果定义了命令行参数，则系统环境变量不生效
   3.   通过在SQL输入窗口，输入loadcommandMap的方式来指定

重写文件的写法要求：
   以下是一个重写文件的典型格式， 1，2，3，4，5 是文件的行号，不是真实内容：
    1 #..*:                                      
    2 ((?i)CREATE TABLE .*\))=>\1 engine xxxxx
    3 WEBURL=>{ENV(ROOTURL)}
    4 MYID=>{RANDOM('random_ascii_letters_and_digits',10)}
    5 #.

    行1：
        这里定义的是参与匹配的文件名，以#.开头，以:结束，如果需要匹配全部文件，则可以在中间用.*来表示
    行2：
        这里定义的是一个正则替换规则, 在符合CREATE TABLE的语句后面增加engine xxxxx字样
    行3：
        这里定义的是一个正则替换规则, 用环境变量ROOTURL的值来替换文件中WEBURL字样
    行4：
        这里定义的是一个正则替换规则, 用一个最大长度位10，可能包含字母和数字的内容来替换文件中的MYID字样
    行5：
        文件定义终止符

    每一个MAP文件里，可以循环反复多个这样的类似配置，每一个配置段都会生效

重写SQL的日志显示：
    被重写后的SQL在日志中有明确的标志信息，比如：
        SQL> CREATE TABLE T_TEST(
           > id int,
           > name varchar(30),
           > salary int
           > );
        REWROTED SQL> Your SQL has been changed to:
        REWROTED    > CREATE TABLE T_TEST(
        REWROTED    > id int,
        REWROTED    > name varchar(30),
        REWROTED    > salary int
        REWROTED    > ) engine xxxx;
     这里第一段是SQL文件中的原信息，带有REWROTED的信息是被改写后的信息

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
***    
### 退出
你可以使用exit来退出命令行程序，或者在脚本中使用Exit来退出正在执行的脚本
```
SQL> exit
Disconnected.
```
注意： 如果当前有后台任务正在运行，EXIT并不能立刻完成。  
1： 控制台应用：EXIT将不会退出，而是会提示你需要等待后台进程完成工作  
2： 脚本应用：  EXIT不会直接退出，而是会等待后台进程完成工作后再退出  
***

### 加载数据库驱动
TestCli会默认加载所有配置在conf/TestCli.ini中的JDBC驱动  
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
   如: _LOAD JDBCDRIVER; 
   
```
(base) TestCli 
SQL*Cli Release 0.0.32
SQL> loaddriver;
没有任何参数的loaddriver命令将显示出所有系统已经加载的驱动程序
SQL> loaddriver [database_name]  [jdbc_jarfile]
将用参数中jdbc_jarfile指定的文件替换掉配置文件中的文件信息
```

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
   
   TODO： ECHO中能够处理{{}}的替代信息，能够支持APPEND操作
    ```
2. 这里文件内容的所有东西都将被直接输出到指定的文件中，包括换行符等信息

#### 程序退出
如果你执行一个脚本，则在以下三种情况下会退出
1. 脚本执行失败。并且设置_WHENEVER ERROR EXIT <INT>的时候。退出的值将是这里的<INT>值
2. 脚本执行结束。退出值为0
3. 脚本中包含了_EXIT <INT>或者_QUIT <INT>语句。退出的值将是这里的<INT>值, 如果不填写，将为0

如果你在命令行中执行，则只有下面情况下会退出
1. 输入了_EXIT <INT>或者_QUIT <INT>语句。退出的值将是这里的<INT>值, 如果不填写，将为0

如果当前有后台程序(通过JOBManager启动的)运行：  
1： 控制台应用：_EXIT将不会直接退出，而是会提示你需要等待后台进程完成工作  
2： 脚本中应用：_EXIT将不会直接退出，而是会等待后台进程完成工作后再退出
3： 控制台应用：_QUIT将会直接退出，无论是否有后台进程在工作  
4： 脚本中应用：_QUIT将会直接退出，无论是否有后台进程在工作

***
## 程序员必读部分

#### 程序代码结构
```
TestCli
│  LICENSE.txt                                        # 许可信息描述，没啥不许可的，Github非要提供一个
│  README.md                                          # 本说明文档
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
    │  sshwrapper.py                                  # 业务实现。用来完成远程SSH操作
    │  testcli.py                                     # 主程序。处理命令行输入信息，根据脚本调用不同的业务实现
    │  testcliexception.py                            # 例外程序定义
    │  testclijobmanager.py                           # 并发任务，任务调度管理
    │  testclimeta.py                                 # 并发业务，数据字典信息
    │  testclitransactionmanager.py                   # 并发业务，交易事务管理
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
    │  │  APILexer.interp
    │  │  APILexer.py
    │  │  APILexer.tokens
    │  │  APIParser.interp
    │  │  APIParser.py
    │  │  APIParser.tokens
    │  │  APIParserVisitor.py
    │  │  SQLLexer.interp
    │  │  SQLLexer.py
    │  │  SQLLexer.tokens
    │  │  SQLParser.interp
    │  │  SQLParser.py
    │  │  SQLParser.tokens
    │  │  SQLParserVisitor.py
    │  │  __init__.py
    │  │  
    ├─commands
    │  │  assertExpression.py                         # 命令实现。 ASSERT语句
    │  │  cliSleep.py                                 # 命令实现。 SLEEP语句
    │  │  embeddScript.py                             # 命令实现。 {% %} 内置脚本语句
    │  │  exit.py                                     # 命令实现。 EXIT|QUIT语句
    │  │  host.py                                     # 命令实现。 HOST语句
    │  │  load.py                                     # 命令实现。 LOAD语句
    │  │  session.py                                  # 命令实现。 SESSION语句
    │  │  setOptions.py                               # 命令实现。 SET语句
    │  │  __init__.py
    │  │  
    ├─conf
    │      testcli.ini                                # 配置文件，用来记录SQL驱动程序的驱动信息
    │      
    ├─docs
    │      PyCharm运行配置.png                         # IDE环境配置说明。非运行需要
    │      
    ├─jlib
    │      Dm7JdbcDriver17.jar                        # 达梦数据库驱动程序。非运行必须
    │      gbase-connector-java-8.3-bin.jar           # gbase数据库驱动程序。非运行必须
    │      h2-1.4.200.jar                             # H2数据库驱动程序。非运行必须。但是运行JOB管理必须
    │      hadoop-common-2.7.2.jar                    # HIVE数据库驱动附属程序。非运行必须。
    │      hive-jdbc-1.2.2-standalone.jar             # HIVE数据库驱动程序。非运行必须。
    │      kingbase8.jar                              # 人大金仓kingbase数据库驱动程序。非运行必须。
    │      kingbasejdbc4.jar                          # 人大金仓kingbase 8数据库驱动程序。非运行必须。
    │      linkoopdb-jdbc-4.0.0.jar                   # Zettabase数据库驱动程序。非运行必须。
    │      mssql-jdbc-9.2.0.jre8.jar                  # 微软SQLServer数据库驱动程序。非运行必须。
    │      mysql-connector-java-8.0.20.jar            # MYSQL数据库驱动程序。非运行必须。
    │      ojdbc8.jar                                 # Oracle数据库驱动程序。非运行必须。
    │      oscarJDBC.jar                              # 神州oscar数据库驱动程序。非运行必须。
    │      postgresql-42.2.12.jar                     # Postgresql数据库驱动程序。非运行必须。
    │      protobuf-java-3.15.6.jar                   # HIVE数据库驱动附属程序。非运行必须。
    │      Qcubic.jar                                 # 快立方数据库驱动程序。非运行必须。
    │      README                                     # 驱动简要说明。非运行必须。
    │      snowflake-jdbc-3.9.2.jar                   # SnowFlake数据库驱动程序。非运行必须。
    │      tdgssconfig.jar                            # TD数据库驱动附属程序。非运行必须。
    │      terajdbc4.jar                              # TD数据库驱动程序。非运行必须。
    │      trino-jdbc-366.jar                         # Trino数据库驱动程序。非运行必须。
    │      vertica-jdbc-9.3.1-0.jar                   # vertica数据库驱动程序。非运行必须。
    │      xdb.jar                                    # Oracle数据库驱动附属程序（针对XMLType类型）。非运行必须。
    │      xmlparserv2.jar                            # Oracle数据库驱动附属程序（针对XMLType类型）。非运行必须。
    │      
    ├─profile
    │      default                                    # 程序默认初始化执行脚本
    │      
    ├─test                                            # 测试程序目录，非运行必须。
    │  │  pytest.ini                                  # unittest测试程序配置
    │  │  testapisynatx-get.api                       # 测试用例。 语法解析->API HTTP_GET. API脚本
    │  │  testapisynatx-get.ref                       # 测试用例。 语法解析->API HTTP_GET. 脚本执行结果比对
    │  │  testapisynatx-multipart.api                 # 测试用例。 语法解析->API MultiPart. API脚本
    │  │  testapisynatx-multipart.ref                 # 测试用例。 语法解析->API MultiPart. 脚本执行结果比对
    │  │  testcliunittest.py                          # 单元测试主程序
    │  │  testmockserver.py                           # 本地模拟HTTP Server程序，用来完成API测试
    │  │  testplugin.py
    │  │  testplugin.ref
    │  │  testplugin.sql
    │  │  testsessionmanage.ref
    │  │  testsessionmanage.sql
    │  │  testsqlembeddscript.ref
    │  │  testsqlembeddscript.sql
    │  │  testsqlifandloop.ref
    │  │  testsqlifandloop.sql
    │  │  testsqlsanity.ref
    │  │  testsqlsanity.sql
    │  │  testsqlsleep.ref
    │  │  testsqlsleep.sql
    │  │  testsqlwithurl.ref
    │  │  testsqlwithurl.sql
    │  │  __init__.py
    │  │  
    └───────
```

#### 线程安全性
目前程序在设计上，是充分考虑到了线程安全性的。

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

#### 开发插件要求
```
   以下是IDEA的插件为说明。
   必须安装的插件为：
      ANTLR v4
   请注意插件的版本，其版本应该和testcli\antlr\antlr-4.x.x-complete.jar想对应
```

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

### 打包发布
```
   一段时间后可以将程序打包后上传到pypi.org网站中，上传办法：
   > uploadpypi.bat
   执行完成后可以在testcli\dist目录下找到打包后的whl文件
      
```
