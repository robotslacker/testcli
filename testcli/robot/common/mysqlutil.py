# -*- coding: utf-8 -*-
import mysql.connector


class MYSQLUtil(object):
    def __init__(self):
        self.user = None
        self.password = None
        self.database = None
        self.host = None
        self.port = 3306
        self.dbHandler = None

    def setUser(self, user: str):
        self.user = user

    def setPassword(self, password: str):
        self.password = password

    def setDatabase(self, database: str):
        self.database = database

    def setHost(self, host: str):
        self.host = host

    def setPort(self, port: int):
        self.port = port

    def connect(
            self,
            host=None,
            port=None,
            user=None,
            passwd=None,
            database=None
    ):
        if host is not None:
            self.setHost(host=host)
        if port is not None:
            self.setPort(port=port)
        if database is not None:
            self.setDatabase(database=database)
        if user is not None:
            self.setUser(user=user)
        if passwd is not None:
            self.setPassword(password=passwd)
        self.dbHandler = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.password,
            database=self.database,
            auth_plugin='mysql_native_password'
        )

    def disConnect(self):
        if self.dbHandler:
            self.dbHandler.close()
        self.dbHandler = None

    def executeQuery(self, sql: str):
        cursor = self.dbHandler.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        field_names = [i[0] for i in cursor.description]
        cursor.close()
        ret = []
        for row in rs:
            rowMap = {}
            for i in range(0, len(row)):
                rowMap[field_names[i]] = row[i]
            ret.append(rowMap)
        return ret

    def execute(self, sql: str, data=None):
        cursor = self.dbHandler.cursor()
        if data is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, data)
        cursor.close()

    def executemany(self, sql: str, data):
        cursor = self.dbHandler.cursor()
        cursor.executemany(sql, data)
        cursor.close()

    def commit(self):
        self.dbHandler.commit()

    def rollback(self):
        self.dbHandler.rollback()
