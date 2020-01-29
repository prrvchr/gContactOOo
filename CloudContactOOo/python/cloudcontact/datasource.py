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
from .dbtools import getDataSourceCall
from .dbtools import getWarning

from threading import Condition
import traceback


class DataSource(unohelper.Base,
                 XTerminateListener,
                 XRestDataSource):
    def __init__(self, ctx):
        self.ctx = ctx
        self.Provider = Provider(self.ctx)
        self._Warnings = []
        self._Statement = None
        self._FieldsMap = None
        self._UsersPool = {}
        self.lock = Condition()
        self.replicator = Replicator(self.ctx, self, self.lock)
        msg = "DataSource for Scheme: %s loading ... Done" % self.Provider.Host
        print(msg)

    @property
    def Connection(self):
        if self._Statement is not None:
            return self._Statement.getConnection()
        return None
    @property
    def Logger(self):
        return self.Provider.Logger

    def getWarnings(self):
        if self._Warnings:
            return self._Warnings.pop(0)
        return None
    def clearWarnings(self):
        self._Warnings = []

    def isConnected(self):
        if self.Connection is not None:
            if not self.Connection.isClosed():
                return True
        scheme = self.Provider.Host
        url, error = getDataSourceUrl(self.ctx, scheme, g_identifier, False)
        if error is not None:
            self._Warnings.append(error)
            return False
        connection, error = getDataSourceConnection(self.ctx, url, scheme)
        if error is not None:
            self._Warnings.append(error)
            return False
        # Piggyback DataBase Connections (easy and clean ShutDown ;-) )
        self._Statement = connection.createStatement()
        desktop = 'com.sun.star.frame.Desktop'
        self.ctx.ServiceManager.createInstance(desktop).addTerminateListener(self)
        print("DataSource.connect() OK")
        return True

    # XTerminateListener
    def queryTermination(self, event):
        print("DataSource.queryTermination()")
        msg = "DataSource queryTermination: Scheme: %s ... " % self.Provider.Host
        if self._Statement is None:
            msg += "ERROR: database connection already dropped..."
        else:
            self.replicator.cancel()
            self.replicator.join()
            query = getSqlQuery('shutdown')
            self._Statement.execute(query)
            msg += "Done"
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

    def getRequest(self, name):
        request = createService(self.ctx, g_oauth2)
        if request:
            request.initializeSession(self.Provider.Host, name)
        else:
            msg = "Service: %s is not available... Check your installed extensions!!!" % g_oauth2
            warning = getWarning('Setup ERROR', 1013, msg, self, None)
            self._Warnings.append(warning)
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
            self._Warnings.append(e)
        return user

    def getFieldsMap(self, reverse):
        if self._FieldsMap is None:
            self._FieldsMap = self._getFieldsMap()
        if reverse:
            map = KeyMap(**{i: {'Map': j, 'Type': k, 'Table': l} for i, j, k, l in self._FieldsMap})
        else:
            map = KeyMap(**{j: {'Map': i, 'Type': k, 'Table': l} for i, j, k, l in self._FieldsMap})
        return map

    def _getFieldsMap(self):
        map = []
        call = getDataSourceCall(self.Connection, 'getFieldsMap')
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
            data = self.Provider.getUser(user.Request, name)
            if data.IsPresent:
                user.setMetaData(self._insertUser(data.Value, name))
                if self._createUser(user, password):
                    return True
                else:
                    state = "DataBase ERROR"
                    code = 1014
                    msg = "ERROR: Can't insert User: %s in DataBase" % name
            else:
                state = "Provider ERROR"
                code = 1015
                msg = "ERROR: User: %s does not exist at this Provider" % name
        else:
            state = "OffLine ERROR"
            code = 1013
            msg = "ERROR: Can't retrieve User: %s from provider: network is OffLine" % name
        warning = getWarning(state, code, msg, self, None)
        self._Warnings.append(warning)
        return False

    def _insertUser(self, user, account):
        data = KeyMap()
        resource = self.Provider.getUserId(user)
        call = getDataSourceCall(self.Connection, 'insertPerson')
        call.setString(1, resource)
        call.setString(2, account)
        row = call.executeUpdate()
        call.close()
        if row == 1:
            call = getDataSourceCall(self.Connection, 'getIdentity')
            result = call.executeQuery()
            if result.next():
                key = result.getLong(1)
                print("DataSource.insertUser(): %s" % key)
                data.insertValue('People', key)
                data.insertValue('Resource', resource)
                data.insertValue('Account', account)
                data.insertValue('Token', '')
                print("DataSource.insertUser() %s" % data.getValue('People'))
            call.close()
        return data

    def _createUser(self, user, password):
        try:
            print("createUser 1")
            credential = user.getCredential(password)
            print("createUser 2 %s - %s" % credential)
            sql = getSqlQuery('createUser', credential)
            print("createUser 3 %s " % sql)
            created = self._Statement.executeUpdate(sql)
            sql = getSqlQuery('grantUser', credential[0])
            print("createUser 4 %s " % sql)
            created += self._Statement.executeUpdate(sql)
            print("createUser 5 %s" % created)
            return created == 0
        except Exception as e:
            print("DataSource.createUser() ERROR: %s - %s" % (e, traceback.print_exc()))
