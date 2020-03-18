#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.sdbc import SQLException
from com.sun.star.lang import XEventListener
from com.sun.star.frame import XTerminateListener
from com.sun.star.util import XCloseListener
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE
from com.sun.star.sdb.CommandType import QUERY
from com.sun.star.ucb.ConnectionMode import ONLINE

from com.sun.star.sdbc import XRestDataSource

from unolib import KeyMap
from unolib import g_oauth2
from unolib import createService
from unolib import getResourceLocation
from unolib import getPropertyValueSet
from unolib import getPropertyValue
from unolib import parseDateTime

from .configuration import g_identifier
from .configuration import g_admin
from .provider import Provider
from .dataparser import DataParser
from .user import User
from .replicator import Replicator

from .dbconfig import g_path
from .dbqueries import getSqlQuery
from .dbinit import getDataSourceUrl
from .dbtools import getDataSourceJavaInfo
from .dbtools import getDataSourceLocation
from .dbtools import getDataBaseConnection
from .dbtools import getDataSourceConnection
from .dbtools import getKeyMapFromResult
from .dbtools import getSequenceFromResult
from .dbtools import getDataSourceCall
from .dbtools import getSqlException
from .logger import logMessage
from .logger import getMessage

from threading import Condition
import traceback


class DataSource(unohelper.Base,
                 XTerminateListener,
                 XRestDataSource):
    def __init__(self, ctx):
        self.ctx = ctx
        self.Provider = Provider(self.ctx)
        self._Warnings = None
        self._Statement = None
        self._FieldsMap = {}
        self._UsersPool = {}
        self._CallsPool = {}
        self.lock = Condition()
        self.replicator = Replicator(self.ctx, self, self.lock)

    @property
    def Connection(self):
        if self._Statement is not None:
            return self._Statement.getConnection()
        return None
    @property
    def Warnings(self):
        return self._Warnings
    @Warnings.setter
    def Warnings(self, warning):
        if warning is None:
            return
        warning.NextException = self._Warnings
        self._Warnings = warning

    def getWarnings(self):
        return self._Warnings
    def clearWarnings(self):
        self._Warnings = None

    def isConnected(self):
        if self.Connection is not None and not self.Connection.isClosed():
            return True
        dbname = self.Provider.Host
        url, self.Warnings = getDataSourceUrl(self.ctx, dbname, g_identifier, False)
        if self.Warnings is not None:
            return False
        connection, self.Warnings = getDataSourceConnection(self.ctx, url, dbname)
        if self.Warnings is not None:
            return False
        # Piggyback DataBase Connections (easy and clean ShutDown ;-) )
        self._Statement = connection.createStatement()
        desktop = 'com.sun.star.frame.Desktop'
        self.ctx.ServiceManager.createInstance(desktop).addTerminateListener(self)
        print("DataSource.connect() OK")
        #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
        #mri.inspect(connection)
        return True

    # XTerminateListener
    def queryTermination(self, event):
        level = INFO
        msg = getMessage(self.ctx, 101, self.Provider.Host)
        if self._Statement is None:
            level = SEVERE
            msg += getMessage(self.ctx, 103)
        else:
            self.replicator.cancel()
            self.replicator.join()
            query = getSqlQuery('shutdownCompact')
            self._Statement.execute(query)
            msg += getMessage(self.ctx, 102)
        logMessage(self.ctx, level, msg, 'DataSource', 'queryTermination()')
        print("DataSource.queryTermination() %s" % msg)
    def notifyTermination(self, event):
        pass

    # XRestDataSource
    def getUser(self, name, password):
        if name in self._UsersPool:
            user = self._UsersPool[name]
        else:
            user = User(self.ctx, self, name)
            if not self._initializeUser(user, name, password):
                return None
            self._UsersPool[name] = user
        with self.lock:
            self.lock.notify()
        return user

    def getUserFields(self):
        fields = []
        call = getDataSourceCall(self.Connection, 'getFieldNames')
        result = call.executeQuery()
        fields = getSequenceFromResult(result)
        call.close()
        print("DataSource.getUserFields() %s" % (fields, ))
        return tuple(fields)

    def getRequest(self, name):
        request = createService(self.ctx, g_oauth2)
        if request:
            request.initializeSession(self.Provider.Host, name)
        else:
            state = getMessage(self.ctx, 1003)
            msg = getMessage(self.ctx, 1105, g_oauth2)
            self.Warnings = getSqlException(state, 1105, msg, self)
        return request

    def selectUser(self, account):
        user = None
        print("DataSource.selectUser() %s - %s" % (account, user))
        try:
            call = getDataSourceCall(self.Connection, 'getPerson')
            call.setString(1, account)
            result = call.executeQuery()
            if result.next():
                user = getKeyMapFromResult(result)
            call.close()
            print("DataSource.selectUser() %s - %s" % (account, user))
        except SQLException as e:
            self.Warnings = e
        return user

    def getFieldsMap(self, method, reverse):
        if method not in self._FieldsMap:
            self._FieldsMap[method] = self._getFieldsMap(method)
        if reverse:
            map = KeyMap(**{i: {'Map': j, 'Type': k, 'Table': l} for i, j, k, l in self._FieldsMap[method]})
        else:
            map = KeyMap(**{j: {'Map': i, 'Type': k, 'Table': l} for i, j, k, l in self._FieldsMap[method]})
        return map

    def getIdentity(self):
        identity = -1
        call = getDataSourceCall(self.Connection, 'getIdentity')
        result = call.executeQuery()
        if result.next():
            identity = result.getLong(1)
        call.close()
        return identity

    def getUpdatedGroups(self, user, prefix):
        groups = []
        call = self.getDataSourceCall('selectGroup')
        call.setString(1, prefix)
        call.setLong(2, user.People)
        result = call.executeQuery()
        while result.next():
            groups.append(result.getString(1))
        return tuple(groups)

    def createGroupView(self, user, name, group):
        self.dropGroupView(user, name)
        query = self._getGroupView(user, name, 'create', group)
        self._Statement.execute(query)

    def dropGroupView(self, user, name):
        query = self._getGroupView(user, name, 'drop')
        self._Statement.execute(query)

    def updateSyncToken(self, user, token, value, timestamp):
        call = self.getDataSourceCall('update%s' % token)
        call.setString(1, value)
        call.setTimestamp(2, timestamp)
        call.setLong(3, user.People)
        if call.executeUpdate():
            user.MetaData.setValue(token, value)
        print("datasource.updateSyncToken(): %s - %s" % (token, value))

    def _getGroupView(self, user, name, method, group=0):
        query = '%sGroupView' % method
        format = {'Schema': user.Resource, 'View': name.title(), 'Group': group}
        return getSqlQuery(query, format)

    def _getFieldsMap(self, method):
        map = []
        call = getDataSourceCall(self.Connection, 'getFieldsMap')
        call.setString(1, method)
        r = call.executeQuery()
        while r.next():
            map.append((r.getString(1), r.getString(2), r.getString(3), r.getString(4)))
        call.close()
        return tuple(map)

    def _initializeUser(self, user, name, password):
        if user.Request is None:
            return False
        if user.MetaData is not None:
            return True
        if not user.Request.isOffLine(self.Provider.Host):
            data = self.Provider.getUser(user.Request, user)
            if data.IsPresent:
                resource = self.Provider.getUserId(data.Value)
                if self._createUser(resource, password):
                    user.MetaData, group = self._insertUser(resource, name)
                    self.createGroupView(user, 'All', group)
                    return True
                else:
                    state = getMessage(self.ctx, 1005)
                    code = 1106
                    msg = getMessage(self.ctx, code, name)
            else:
                state = getMessage(self.ctx, 1006)
                code = 1107
                msg = getMessage(self.ctx, code, name)
        else:
            state = getMessage(self.ctx, 1004)
            code = 1108
            msg = getMessage(self.ctx, code, name)
        self.Warnings = getSqlException(state, code, msg, self)
        return False

    def _insertUser(self, resource, account):
        data = KeyMap()
        call = getDataSourceCall(self.Connection, 'insertUser')
        call.setString(1, resource)
        call.setString(2, account)
        result = call.executeQuery()
        if result.next():
            data = getKeyMapFromResult(result)
        group = call.getLong(3)
        call.close()
        return data, group

    def _createUser(self, name, password):
        credential = {'UserName': name, 'Password': password, 'Admin': g_admin}
        sql = getSqlQuery('createUser', credential)
        status = self._Statement.executeUpdate(sql)
        sql = getSqlQuery('createSchema', credential)
        status += self._Statement.executeUpdate(sql)
        sql = getSqlQuery('setUserSchema', credential)
        status += self._Statement.executeUpdate(sql)
        return status == 0

    def getDataSourceCall(self, name):
        if name  not in self._CallsPool:
            self._CallsPool[name] = getDataSourceCall(self.Connection, name)
        return self._CallsPool[name]

    def getPreparedCall(self, name):
        if name not in self._CallsPool:
            # TODO: cannot use: call = self.Connection.prepareCommand(name, QUERY)
            # TODO: it trow a: java.lang.IncompatibleClassChangeError
            query = self.Connection.getQueries().getByName(name).Command
            call = self.Connection.prepareCall(query)
            self._CallsPool[name] = call
        return self._CallsPool[name]

    def closeDataSourceCall(self):
        for name in self._CallsPool:
            call = self._CallsPool[name]
            call.close()
        self._CallsPool = {}
