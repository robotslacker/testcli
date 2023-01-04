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
    }
]
