*** Settings ***
Library           SetupTestCli.py
Library           RunTestCli.py
Library           RunPython.py
Library           RunCompare.py
Library           OperatingSystem
Library           String
Library           Process

*** Keywords ***
TestCli Test Setup
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
    Compare Algorithm                  MYERS

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
    #     过滤掉完全是表头的内容
    Compare Skip                       ^[-|+]+$

    # Case运行在脚本所在的目录下，切换当前工作目录
    SetupRoot CD CurrentDirectory        ${SUITE SOURCE}

    # 记录所有环境变量信息到日志文件中，便于日后检查
    log environment variables

TestCli Test Clnup
    # 暂时空置
    Log to Console      "Test Completed."
