# -*- coding: utf-8 -*-

helpMessage = [
    {
        "topic": 'exit',
        "summary": "exit current script with exitValue (Default is 0) ",
        "synatx": "_EXIT [<exitValue>]",
    },
    {
        "topic": 'quit',
        "summary": "force exit current script with exitValue (Default is 0) ",
        "synatx": "_QUIT [<exitValue>]",
    },
    {
        "topic": 'load',
        "summary": "load external map/driver/plugin files.",
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

            _LOAD MAP <command mapping file location>
        ''',
    },
    {
        "topic": 'ssh',
        "summary": "Remote SSH operation.",
        "synatx":
            '''
            _SSH CONNECT <remote hostname or ip address> WITH USER <username> KEYFILE <ssh key file location>
            _SSH CONNECT <remote hostname or ip address> WITH USER <username> [PASSWORD <user password>]
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
        ''',
    },
    {
        "topic": 'compare',
        "summary": "Diff test result and reference log.",
        "synatx":
        '''
           _COMPARE <work file name> <reference file name> {MASK | NOMASK | CASE | NOCASE | IGBLANK | NOIGBLANK | TRIM | NOTRIM}
           _COMPARE SKIPLINE <the line expression to skip>
           _COMPARE NOSKIPLINE <the skip line to undefine>
           _COMPARE MASKLINE <<src pattern to mask> >= <target string after mask>>
           _COMPARE NOMASKLINE <the mask line to undefine>
           _COMPARE RESET
           _COMPARE SET {MASK | NOMASK | CASE | NOCASE | IGBLANK | NOIGBLANK | TRIM | NOTRIM}
           _COMPARE SET OUTPUT { CONSOLE | DIFFFILE }
           _COMPARE SET ALGORITHM [LCS | MYERS]
           _COMPARE SET WORK ENCODING <work file codec, default is UTF-8>
           _COMPARE SET REFERENCE ENCODING <reference file codec. default is UTF-8>
        ''',
    },
    {
        "topic": 'echo',
        "summary": "echo some message to file.",
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
        "synatx":
            '''
               _JOB MANAGER [ON | OOF]
               _JOB WAIT [<job name> | ALL] 
               _JOB SHOW [<job name> | ALL] 
               _JOB START [<job name> | ALL]  
               _JOB ABORT [<job name> | ALL]
               _JOB SHUTDOWN [<job name> | ALL]   
               _JOB CREATE <job name> { <option Name> = <optionValue>}
               _JOB SET <job name> { <option Name> = <optionValue>}
               _JOB REGISTER WORKER TO <job name>
               _JOB DEREGISTER WORKER
               
               Job Option:
               script                   ：  Required. The script name of the background job.    
               tag                      ：  Required. All worker processes with the same tag will be synchronized when 
                                            judging the aggregation point.
               parallel                 ：  Optional. Number of background jobs at same time, default is 1. 
               loop                     ：  Optional. Number of cycles, default is 1.
               timeout                  ：  Optional. The timeout limit (second) of background jobs, 
                                            default value is 0, which means no limit.
               starter_maxprocess       ：  Optional. To reduce the load pressure of the first start, we don't start all 
                                            jobs in a single batch. This parameter is meaningful only when the job first 
                                            started. The default is 9999, which means no limit.
                                            For example: parallel is 10, and starter_maxprocess is 2.
                                                         two jobs are started each "starter_interval" time until the 
                                                         parallel requirements(10) are met.
               starter_interval         ：  Optional. Referring to the previous description, starter_interval define the 
                                            interval time when job first start. default is 0, it means no wait.
               think_time               ：  Optional. After each job completed, the time interval required to start the 
                                            next job. Default is 0, which means no think, start next job immediate.
               blowout_threshold_count  ：  Optional. The failure threshold value. If threshold has reached, we think 
                                            following jobs are unnecessary to run.  The default is 0, that is, no limit.  
            ''',
    },
    {
        "topic": 'data',
        "summary": "Generate test random data.",
        "synatx":
            '''
                _DATA SET SEEDFILE DIR <seed file location>;
                  
                _DATA CREATE MEM|FS FILE <target file location> 
                (
                   <column expression..>,
                   <column expression..>
                )
                [ROWS <rows will generated>];
                  
                _DATA CONVERT MEM|FS FILE <source file location> TO MEM|FS FILE <target file location>;  
            ''',
    },
    {
        "topic": 'SLEEP',
        "summary": "sleep app some time",
        "synatx":
            '''
                _SLEEP <sleep time (seconds)>
            ''',
    },
    {
        "topic": 'ASSERT',
        "summary": "Execute the assertion. Determine whether the specified conditions are met.",
        "synatx":
            '''
                _ASSERT {% <assert python expression> %}, [<name of assertion, optional>]
            ''',
    },
    {
        "topic": 'USE',
        "summary": "Switch the namespace of the current script.",
        "synatx":
            '''
                _USE SQL|API
            ''',
    },
    {
        "topic": 'HOST',
        "summary": "Execute local system commands.",
        "synatx":
            '''
                _HOST <os file command>
            ''',
    },
    {
        "topic": 'SET',
        "summary": "Set/View app runtime options.",
        "synatx":
            '''
                _SET [<OPTION_NAME> <OPTION_VALUE>]
                
                If you run this command without any parameter, it will show current runtime options.
            ''',
    },
    {
        "topic": 'START',
        "summary": "Run sub command script.",
        "synatx":
            '''
                _STARRT <command script file location> [<argv1> <argv2> ....]
            ''',
    },
    {
        "topic": 'SCRIPT',
        "summary": "Run embedded python script.",
        "synatx":
            '''
                > {%
                <python script>
                %}
            ''',
    },
    {
        "topic": 'SPOOL',
        "summary": "Print subsequent run commands and results to the specified file.",
        "synatx":
            '''
                _SPOOL <spool file location>
                <command1 ...>
                <command2 ...>
                _SPOOL OFF
            ''',
    },
]
