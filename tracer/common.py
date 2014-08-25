import os
import sqlite3

############################################
## MANAGES THE CONNECTION TO THE DATABASE ##
############################################

class DBManager(object):
    def __init__(self, file):
        newDB = not os.path.isfile(file)
        self.conn = sqlite3.connect(file)
        self.cursor = self.conn.cursor()
        if newDB:
            self._initDB()

    def _query(self, query, *params):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def _initDB(self):
        self._query('''
create table errors (
    id integer primary key autoincrement,
    date datetime default current_timestamp,
    short_error text,
    full_error text
);
            ''')

    def addError(self, shortError, fullError):
        self._query("insert into errors (short_error, full_error) values (?, ?)", shortError, fullError)

    def fetchErrors(self):
        queryResults = self._query("select id,datetime(date,'localtime'),short_error,full_error from errors order by date desc limit 750;")
        errorList = []
        for queryResult in reversed(queryResults):
            errorList.append(Error(*queryResult))
        return errorList


######################
## DEFINES AN ERROR ##
######################

class Error(object):
    def __init__(self, id, errorDatetime, shortError, fullError):
        self.id = id
        self.errorDatetime = errorDatetime
        self.shortError = shortError
        self.fullError = fullError

    def getListText(self):
        return self.errorDatetime + ": " + self.shortError