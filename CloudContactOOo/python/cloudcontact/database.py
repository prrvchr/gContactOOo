#!
# -*- coding: utf_8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020 https://prrvchr.github.io                                     ║
║                                                                                    ║
║   Permission is hereby granted, free of charge, to any person obtaining            ║
║   a copy of this software and associated documentation files (the "Software"),     ║
║   to deal in the Software without restriction, including without limitation        ║
║   the rights to use, copy, modify, merge, publish, distribute, sublicense,         ║
║   and/or sell copies of the Software, and to permit persons to whom the Software   ║
║   is furnished to do so, subject to the following conditions:                      ║
║                                                                                    ║
║   The above copyright notice and this permission notice shall be included in       ║
║   all copies or substantial portions of the Software.                              ║
║                                                                                    ║
║   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,                  ║
║   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES                  ║
║   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.        ║
║   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY             ║
║   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,             ║
║   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE       ║
║   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                    ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import uno
import unohelper

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.sdb.CommandType import QUERY

from com.sun.star.sdbc import XRestDataBase

from unolib import KeyMap
from unolib import parseDateTime

from .configuration import g_admin

from .dbqueries import getSqlQuery
from .dbconfig import g_role
from .dbconfig import g_dba

from .dbtools import checkDataBase
from .dbtools import createStaticTable
from .dbtools import executeSqlQueries
from .dbtools import getDataSourceCall
from .dbtools import executeQueries
from .dbtools import getDictFromResult
from .dbtools import getKeyMapFromResult
from .dbtools import getSequenceFromResult
from .dbtools import getKeyMapKeyMapFromResult

from .dbinit import getStaticTables
from .dbinit import getQueries
from .dbinit import getTablesAndStatements
from .dbinit import getViewsAndTriggers

from .logger import logMessage
from .logger import getMessage

from collections import OrderedDict
import traceback


class DataBase(unohelper.Base,
               XRestDataBase):
    def __init__(self, ctx, datasource, name='', password='', sync=None):
        self.ctx = ctx
        self._statement = datasource.getConnection(name, password).createStatement()
        self._fieldsMap = {}
        self._batchedCalls = OrderedDict()
        self.sync = sync

    @property
    def Connection(self):
        return self._statement.getConnection()

# Procedures called by the DataSource
    def createDataBase(self):
        version, error = checkDataBase(self.ctx, self.Connection)
        if error is None:
            createStaticTable(self.ctx, self._statement, getStaticTables())
            tables, queries = getTablesAndStatements(self.ctx, self._statement, version)
            executeSqlQueries(self._statement, tables)
            executeQueries(self.ctx, self._statement, getQueries())
            executeSqlQueries(self._statement, queries)
            views, triggers = getViewsAndTriggers(self.ctx, self._statement)
            executeSqlQueries(self._statement, views)
        return error

    def getDataSource(self):
        return self.Connection.getParent().DatabaseDocument.DataSource

    def storeDataBase(self, url):
        self.Connection.getParent().DatabaseDocument.storeAsURL(url, ())

    def addCloseListener(self, listener):
        self.Connection.Parent.DatabaseDocument.addCloseListener(listener)

    def shutdownDataBase(self, compact=False):
        query = getSqlQuery(self.ctx, 'shutdown', compact)
        self._statement.execute(query)

    def createUser(self, name, password):
        format = {'User': name, 'Password': password, 'Admin': g_admin}
        query = getSqlQuery(self.ctx, 'createUser', format)
        status = self._statement.executeUpdate(query)
        print("DataBase.createUser() %s" % status)
        return status == 0

    def insertUser(self, userid, account, group):
        user = KeyMap()
        call = self._getCall('insertUser')
        call.setString(1, userid)
        call.setString(2, account)
        call.setString(3, group)
        result = call.executeQuery()
        if result.next():
            user = getKeyMapFromResult(result)
        call.close()
        return user

    def selectUser(self, account):
        user = None
        call = self._getCall('getPerson')
        call.setString(1, account)
        result = call.executeQuery()
        if result.next():
            user = getKeyMapFromResult(result)
        call.close()
        return user

    def truncatGroup(self, start):
        format = {'TimeStamp': unparseTimeStamp(start)}
        query = getSqlQuery(self.ctx, 'truncatGroup', format)
        self._statement.execute(query)

    def createSynonym(self, user, name):
        format = {'Schema': user.Resource, 'View': name.title()}
        query = getSqlQuery(self.ctx, 'createSynonym', format)
        self._statement.execute(query)

    def createGroupView(self, user, name, group):
        self._dropGroupView(user, name)
        query = self._getGroupViewQuery('create', user, name, group)
        self._statement.execute(query)

# Procedures called by the User
    def getUserFields(self):
        fields = []
        call = self._getCall('getFieldNames')
        result = call.executeQuery()
        fields = getSequenceFromResult(result)
        call.close()
        return tuple(fields)

# Procedures called by the Replicator
    def getDefaultType(self):
        default = {}
        call = self._getCall('getDefaultType')
        result = call.executeQuery()
        default = getDictFromResult(result)
        call.close()
        return default

    def setLoggingChanges(self, state):
        query = getSqlQuery(self.ctx, 'loggingChanges', state)
        self._statement.execute(query)

    def saveChanges(self, compact=False):
        query = getSqlQuery(self.ctx, 'saveChanges', compact)
        self._statement.execute(query)

    def getFieldsMap(self, method, reverse):
        if method not in self._fieldsMap:
            self._fieldsMap[method] = self._getFieldsMap(method)
        if reverse:
            map = KeyMap(**{i: {'Map': j, 'Type': k, 'Table': l} for i, j, k, l in self._fieldsMap[method]})
        else:
            map = KeyMap(**{j: {'Map': i, 'Type': k, 'Table': l} for i, j, k, l in self._fieldsMap[method]})
        return map

    def getUpdatedGroups(self, user, prefix):
        groups = None
        call = self._getCall('selectUpdatedGroup')
        call.setString(1, prefix)
        call.setLong(2, user.People)
        call.setString(3, user.Resource)
        result = call.executeQuery()
        groups = getKeyMapKeyMapFromResult(result)
        call.close()
        return groups

    def updateSyncToken(self, user, token, data, timestamp):
        value = data.getValue(token)
        call = self._getBatchedCall('update%s' % token)
        call.setString(1, value)
        call.setTimestamp(2, timestamp)
        call.setLong(3, user.People)
        call.addBatch()
        return KeyMap(**{token: value})

    def mergePeople(self, user, resource, timestamp, deleted):
        call = self._getBatchedCall('mergePeople')
        call.setString(1, 'people/')
        call.setString(2, resource)
        call.setLong(3, user.Group)
        call.setTimestamp(4, timestamp)
        call.setBoolean(5, deleted)
        call.addBatch()
        return (0, 1) if deleted else (1, 0)

    def mergePeopleData(self, table, resource, typename, label, value, timestamp):
        format = {'Table': table, 'Type': typename}
        call = self._getBatchedCall(table, 'mergePeopleData', format)
        call.setString(1, 'people/')
        call.setString(2, resource)
        call.setString(3, label)
        call.setString(4, value)
        call.setTimestamp(5, timestamp)
        if typename is not None:
            call.setString(6, table)
            call.setString(7, typename)
        call.addBatch()
        return 1

    def mergeGroup(self, user, resource, name, timestamp, deleted):
        call = self._getBatchedCall('mergeGroup')
        call.setString(1, 'contactGroups/')
        call.setLong(2, user.People)
        call.setString(3, resource)
        call.setString(4, name)
        call.setTimestamp(5, timestamp)
        call.setBoolean(6, deleted)
        call.addBatch()
        return (0, 1) if deleted else (1, 0)

    def mergeConnection(self, user, data, timestamp):
        separator = ','
        call = self._getBatchedCall('mergeConnection')
        call.setString(1, 'contactGroups/')
        call.setString(2, 'people/')
        call.setString(3, data.getValue('Resource'))
        call.setTimestamp(4, timestamp)
        call.setString(5, separator)
        members = data.getDefaultValue('Connections', ())
        call.setString(6, separator.join(members))
        call.addBatch()
        print("DataBase._mergeConnection() %s - %s" % (data.getValue('Resource'), len(members)))
        return len(members)

    def executeBatchCall(self):
        for name in self._batchedCalls:
            call = self._batchedCalls[name]
            call.executeBatch()
            call.close()
        self._batchedCalls = OrderedDict()

# Procedures called internaly
    def _getFieldsMap(self, method):
        map = []
        call = self._getCall('getFieldsMap')
        call.setString(1, method)
        r = call.executeQuery()
        while r.next():
            map.append((r.getString(1), r.getString(2), r.getString(3), r.getString(4)))
        call.close()
        return tuple(map)

    def _dropGroupView(self, user, name):
        query = self._getGroupViewQuery('drop', user, name)
        self._statement.execute(query)

    def _getGroupViewQuery(self, method, user, name, group=0):
        query = '%sGroupView' % method
        account, pwd = user.getCredential('')
        format = {'User': account,
                  'View': '%s.%s' % (user.Name, name.title()),
                  'Group': group}
        return getSqlQuery(self.ctx, query, format)

    def _getCall(self, name, format=None):
        return getDataSourceCall(self.ctx, self.Connection, name, format)

    def _getBatchedCall(self, key, name=None, format=None):
        if key not in self._batchedCalls:
            name = key if name is None else name
            self._batchedCalls[key] = getDataSourceCall(self.ctx, self.Connection, name, format)
        return self._batchedCalls[key]

    def _getPreparedCall(self, name):
        # TODO: cannot use: call = self.Connection.prepareCommand(name, QUERY)
        # TODO: it trow a: java.lang.IncompatibleClassChangeError
        #query = self.Connection.getQueries().getByName(name).Command
        #self._CallsPool[name] = self.Connection.prepareCall(query)
        return self.Connection.prepareCommand(name, QUERY)
