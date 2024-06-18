# -*- coding: utf-8 -*-

helpMessage = [
    {
        "topic": 'exit',
        "summary": "exit current script with exitValue (Default is 0) ",
        "nameSpace": "ALL",
        "synatx": "_EXIT [<exitValue>]",
    },
    {
        "topic": 'quit',
        "summary": "force exit current script with exitValue (Default is 0) ",
        "nameSpace": "ALL",
        "synatx": "_QUIT [<exitValue>]",
    },
    {
        "topic": 'load',
        "summary": "load external map/driver/plugin files.",
        "nameSpace": "ALL",
        "synatx":
            '''
            _LOAD JDBCDRIVER 
            {
                NAME = <the unique name of each jdbc driver> |
                CLASS = <name of driver class> |
                FILE = <the drive file location> |
                URL = <jdbc connect url> |
                PROPS = <extra properties for jdbc connect url>
            }
            
            _LOAD PLUGIN <plugin file location> 

            _LOAD SCRIPT <script file location> 

            _LOAD MAP <command mapping file location>
        ''',
    },
    {
        "topic": 'ssh',
        "summary": "Remote SSH operation.",
        "nameSpace": "ALL",
        "synatx":
            '''
            _SSH CONNECT <remote hostname or ip address> WITH USER <username> KEYFILE <ssh key file location>
            _SSH CONNECT <remote hostname or ip address> WITH USER <username> [PASSWORD <user password>]
            _SSH SET <option name>=<option value>
            _SSH EXECUTE <remote command>
            _SSH DISCONNECT
            _SSH SAVE <user defined session name>
            _SSH RESTORE <user defined session name>
            _SSH SFTP CHMOD <remote file name> <new file permission, 8-base number>
            _SSH SFTP GETCWD
            _SSH SFTP CHDIR <new directory>
            _SSH SFTP CHOWN <target file name> <new user id> <new group id>
            _SSH SFTP MKDIR <target directory name> [<new file permission, 8-base number>]
            _SSH SFTP GET <remote file name> <local file name>
            _SSH SFTP PUT <local file name> <remote file name>
            _SSH SFTP REMOVE <file name to delete>
            _SSH SFTP RENAME <file name to rename> <new remote file name>
            _SSH SFTP LISTDIR <file name to list>
            _SSH SFTP TRUNCATE <file name to trancate> <new file size after truncate>
            
            Current SSH support option:
               encoding:               Control the ssh channel.
        ''',
    },
    {
        "topic": 'compare',
        "summary": "Diff test result and reference log.",
        "nameSpace": "ALL",
        "synatx":
        '''
           _COMPARE <work file name> <reference file name> {MASK|NOMASK|CASE|NOCASE|IGBLANK|NOIGBLANK|TRIM|NOTRIM}
           _COMPARE SKIPLINE <the line expression to skip>
           _COMPARE NOSKIPLINE <the skip line to undefine>
           _COMPARE MASKLINE <<src pattern to mask> >= <target string after mask>>
           _COMPARE NOMASKLINE <the mask line to undefine>
           _COMPARE RESET
           _COMPARE SET {MASK|NOMASK|CASE|NOCASE|IGBLANK|NOIGBLANK|TRIM|NOTRIM}
           _COMPARE SET OUTPUT { CONSOLE | DIFFFILE | HTMLFILE}
           _COMPARE SET ALGORITHM [LCS | MYERS]
           _COMPARE SET WORK ENCODING <work file codec, default is UTF-8>
           _COMPARE SET REFERENCE ENCODING <reference file codec. default is UTF-8>
        ''',
    },
    {
        "topic": 'echo',
        "summary": "echo some message to file.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _ECHO <target file name>
                    <echo body. you can input anything>
                _ECHO OFF 
            ''',
    },
    {
        "topic": 'spool',
        "summary": "spool following command and command output to file.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _SPOOL  <target file name>
                    <command1>
                    <command2>
                    .....
                _SPOOL  OFF 
            ''',
    },
    {
        "topic": 'job',
        "summary": "Run slave script in parallel.",
        "nameSpace": "ALL",
        "synatx":
            '''
               _JOB MANAGER [ON | OOF]
               _JOB WAIT [<job name> | ALL] { <option Name> = <optionValue>} 
               _JOB SHOW [<job name> | ALL] 
               _JOB START [<job name> | ALL]  
               _JOB ABORT [<job name> | ALL]
               _JOB SHUTDOWN [<job name> | ALL]   
               _JOB CREATE <job name> { <option Name> = <optionValue>}
               _JOB SET <job name> { <option Name> = <optionValue>}
               _JOB REGISTER WORKER TO <job name>
               _JOB DEREGISTER WORKER

               Job Option [Wait]:
                   timeout                  ：  Optional. The timeout limit (second) of wait jobs, 
                                                default value is 0, which means no limit.
               
               Job Option [Set]:
                   script                   ：  Required. The script name of the background job.    
                   tag                      ：  Required. All worker processes with the same tag will be synchronized 
                                                when judging the aggregation point.
                   parallel                 ：  Optional. Number of background jobs at same time, default is 1. 
                   loop                     ：  Optional. Number of cycles, default is 1.
                   timeout                  ：  Optional. The timeout limit (second) of background jobs, 
                                                default value is 0, which means no limit.
                   starter_maxprocess       ：  Optional. To reduce the load pressure of the first start, we don't start 
                                                all jobs in a single batch. This parameter is meaningful only when the  
                                                job first started. The default is 9999, which means no limit.
                                                For example: parallel is 10, and starter_maxprocess is 2.
                                                             two jobs are started each "starter_interval" time until the 
                                                             parallel requirements(10) are met.
                   starter_interval         ：  Optional. Referring to the previous description, starter_interval define 
                                                the interval time when job first start. default is 0, it means no wait.
                   think_time               ：  Optional. After each job completed, the time interval required to start 
                                                the next job. Default is 0, which means no think, start next immediate.
                   blowout_threshold_count  ：  Optional. The failure threshold value. If threshold has reached, we  
                                                think following jobs are unnecessary to run.  
                                                The default is 0, that is, no limit.  
            ''',
    },
    {
        "topic": 'data',
        "summary": "Generate test random data.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _DATA SET SEEDFILE DIR <seed file location>;
                  
                _DATA SET HDFSUSER <hdfs connected user>;
                
                _DATA CREATE MEM|FS|HDFS FILE <target file location> 
                (
                   <column expression..>,
                   <column expression..>
                )
                [ROWS <rows will generated>];
                  
                _DATA CONVERT MEM|FS|HDFS FILE <source file location> TO MEM|FS|HDFS FILE <target file location>;  
                
                hdfs file location:
                    hdfs://<hdfs server ip>:<hdfs server port>/<hdfs file path>
            ''',
    },
    {
        "topic": 'SLEEP',
        "summary": "sleep app some time",
        "nameSpace": "ALL",
        "synatx":
            '''
                _SLEEP <sleep time (seconds)>
            ''',
    },
    {
        "topic": 'ASSERT',
        "summary": "Execute the assertion. Determine whether the specified conditions are met.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _ASSERT {% <assert python expression> %}, [<name of assertion, optional>]
            ''',
    },
    {
        "topic": 'USE',
        "summary": "Switch the namespace of the current script.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _USE SQL|API
            ''',
    },
    {
        "topic": 'HOST',
        "summary": "Execute local system commands.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _HOST <os file command>
            ''',
    },
    {
        "topic": 'SET',
        "summary": "Set/View app runtime options.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _SET [<OPTION_NAME> <OPTION_VALUE>]
                
                If you run this command without any parameter, it will show current runtime options.
            ''',
    },
    {
        "topic": 'START',
        "summary": "Run sub command script.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _STARRT <command script file location> [<argv1> <argv2> ....]
            ''',
    },
    {
        "topic": 'SCRIPT',
        "summary": "Run embedded python script.",
        "nameSpace": "ALL",
        "synatx":
            '''
                > {%
                <python script>
                %}
            ''',
    },
    {
        "topic": 'MONITOR',
        "summary": "Monitor system perference.",
        "nameSpace": "ALL",
        "synatx":
            '''
        _MONITOR MANAGER ON [WOKERS <int>]
        _MONITOR MANAGER OFF
        _MONITOR CREATE TASK <taskName> TAG=<taskTag> <taskPara1>=<taskValue1> <taskPara2>=<taskValue2> ...
        _MONITOR START TASK [ <taskName> | ALL ]
        _MONITOR STOP TASK [ <taskName> | ALL ]
        _MONITOR REPORT TASK [ <taskName> | ALL ]
        _MONITOR LIST TASK

        Example:
            _MONITOR MONITORMANAGER ON WORKERS 3;

            _MONITOR CREATE TASK task1 TAG=cpu_count;
            _MONITOR CREATE TASK task2 TAG=memory FREQ=10;
            _MONITOR CREATE TASK task3 TAG=network NAME='eth0' FREQ=10;
            _MONITOR CREATE TASK task4 TAG=disk NAME='.*' FREQ=10;
            _MONITOR CREATE TASK task5 TAG=process USERNAME='ldb' EXE='.*grassland-launcher';
            _MONITOR START TASK ALL;
            _SLEEP 10;
            _MONITOR LIST TASK;
            _MONITOR REPORT TASK ALL;

        Supported tags:
            cpu_count                
            cpu_count_physical
            cpu_times
            cpu_percent
            memory
            network
            disk
            process
            ''',
    },
    {
        "topic": 'SPOOL',
        "summary": "Print subsequent run commands and results to the specified file.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _SPOOL <spool file location>
                <command1 ...>
                <command2 ...>
                _SPOOL OFF
            ''',
    },
    {
        "topic": 'IF',
        "summary": "Conditional statement.",
        "nameSpace": "ALL",
        "synatx":
            '''
                _IF {% <expression> %}                
                _ENDIF
            ''',
    },
    {
        "topic": 'LOOP',
        "summary": "LOOP statement.",
        "nameSpace": "ALL",
        "synatx":
            '''
               _LOOP BEGIN UNTIL {% <expression> %}
               _LOOP BREAK
               _LOOP CONTINUE
               _LOOP END
               
               _LOOP [<maxRetriedTime>] UNTIL {% <expression> %} INTERVAL <loop interval time>
            ''',
    },
    {
        "topic": 'CONNECT',
        "summary": "Connect to JDBC database.",
        "nameSpace": "SQL",
        "synatx":
            '''
        _CONNECT /[MEM|META]
        _CONNECT {<user>/<pass>@}jdbc:<driver>{:<driverType>}/{<host>{:<port>}}/{<service>}                
        
        Example:
            _connect user/pass@jdbc:mysql:tcp://[2001:251:e000:1::c0a8:230]:3306/mydb
            _connect user/pass@jdbc:mysql:tcp://10.10.10.10:3306/mydb
            _connect user/pass
            ''',
    },
    {
        "topic": 'SQL',
        "summary": "Execute sql statement.",
        "nameSpace": "SQL",
        "synatx":
            '''
        Write any valid sql statement.
        
        For single line sql statement, end with semicolon;
        For multiline statements, end with a slash;
        
        Example:
            Drop Table If Exists Col1;

            Create Table TestTab(Col1 Int);

            Declare
            Begin
                Insert Into TestTab Values(1);
            End;
            /
            ''',
    },
    {
        "topic": 'SQLSESSION',
        "summary": "SQL session management.",
        "nameSpace": "SQL",
        "synatx":
            '''
        _SESSION SAVE <sessonName>
        _SESSION RELEASE
        _SESSION RESTORE <sessonName>
        _SESSION SAVEURL [<sessonName>]
        _SESSION SHOW [<sessonName>]

        Example:
            N/A
            ''',
    },
    {
        "topic": 'HTTPSET',
        "summary": "Set http request behavior.",
        "nameSpace": "API",
        "synatx":
            '''
        SET HTTPS_VERIFY <ON|OFF>;
        SET HTTP_RPXOY <proxy_address, like http://127.0.0.1:8080>
        
    
        Example:
            N/A
            ''',
    },
    {
        "topic": 'HTTP',
        "summary": "Execute http statement.",
        "nameSpace": "API",
        "synatx":
            '''
        Execute http request.

        To compose an HTTP request in TestCli, use the following general syntax:            
            ### RequestName
            Method Request-URI HTTP-Version
            Header-field: Header-value

            Request-Body
            ###
            
        Use comments in HTTP requests:
            -- Comment Here.
            GET http://example.com/a/

        Use multipart/form-data content type:
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
            
        Example:
            ### basic request 1
            -- A basic request
            GET http://example.com/a/  HTTP/1.1

            ###

            ### basic request 2
            -- A basic request
            GET http://example.com:8080  HTTP/1.1
                /api
                /html
                /get
                ?id=123
                &value=content
    
            ###

            ### basic request 3
            POST http://example.com:8080/api/html/post HTTP/1.1
            Content-Type: application/json
            Cookie: key=first-value
            
            { "key" : "value", "list": [1, 2, 3] }
            ###

            ''',
    },
    {
        "topic": 'HTTPSESSION',
        "summary": "Http session management.",
        "nameSpace": "API",
        "synatx":
            '''
           _SESSION SAVE <sessonName>
           _SESSION RELEASE
           _SESSION RESTORE <sessonName>
           _SESSION SHOW [<sessonName>]
        
        Example:
            N/A
            ''',
    }
]
