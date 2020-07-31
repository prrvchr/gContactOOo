#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.util import XCloseListener

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.sdb.CommandType import QUERY

from com.sun.star.sdbc import XRestDataSource

from unolib import g_oauth2

from .configuration import g_identifier
from .configuration import g_group
from .configuration import g_compact

from .database import DataBase
from .provider import Provider
from .user import User
from .replicator import Replicator

from .dbtools import getDataSource
from .dbtools import getSqlException

from .logger import logMessage
from .logger import getMessage

import traceback


class DataSource(unohelper.Base,
                 XCloseListener,
                 XRestDataSource):
    def __init__(self, ctx, sync):
        print("DataSource.__init__() 1")
        self.ctx = ctx
        self._Warnings = None
        self._Users = {}
        self.sync = sync
        self.Error = None
        self.Provider = Provider(self.ctx)
        dbname = self.Provider.Host
        datasource, url, created = getDataSource(self.ctx, dbname, g_identifier, True)
        self.DataBase = DataBase(self.ctx, datasource)
        if created:
            self.Error = self.DataBase.createDataBase()
            if self.Error is None:
                self.DataBase.storeDataBase(url)
        self.DataBase.addCloseListener(self)
        self.Replicator = Replicator(self.ctx, datasource, self.Provider, self._Users, self.sync)
        print("DataSource.__init__() 2")

    @property
    def Warnings(self):
        return self._Warnings
    @Warnings.setter
    def Warnings(self, warning):
        if warning is not None:
            if self._Warnings is not None:
                warning.NextException = self._Warnings
            self._Warnings = warning

    def isValid(self):
        return self.Error is None
    def getWarnings(self):
        return self._Warnings
    def clearWarnings(self):
        self._Warnings = None

    # XCloseListener
    def queryClosing(self, source, ownership):
        if self.Replicator.is_alive():
            self.Replicator.cancel()
            self.Replicator.join()
        compact = self.Replicator.count >= g_compact
        self.DataBase.shutdownDataBase(compact)
        msg = "DataSource queryClosing: Scheme: %s ... Done" % self.Provider.Host
        logMessage(self.ctx, INFO, msg, 'DataSource', 'queryClosing()')
        print(msg)
    def notifyClosing(self, source):
        pass

    # XRestDataSource
    def getUser(self, name, password):
        if name in self._Users:
            user = self._Users[name]
        else:
            user = User(self.ctx, self, name)
            if not self._initializeUser(user, name, password):
                return None
            self._Users[name] = user
            # User has been initialized and the connection to the database is done...
            # We can start the database replication in a background task.
            self.sync.set()
        return user

    def _initializeUser(self, user, name, password):
        print("DataSource._initializeUser() 1")
        if user.Request is not None:
            if user.MetaData is not None:
                return True
            if self.Provider.isOnLine():
                data = self.Provider.getUser(user.Request, user)
                if data.IsPresent:
                    print("DataSource._initializeUser() 2")
                    userid = self.Provider.getUserId(data.Value)
                    user.MetaData = self.DataBase.insertUser(userid, name, g_group)
                    credential = user.getCredential(password)
                    print("DataSource._initializeUser() 3 %s" % (user.MetaData.getKeys(), ))
                    if self.DataBase.createUser(*credential):
                        print("DataSource._initializeUser() 4")
                        self.DataBase.createGroupView(user, g_group, user.Group)
                        print("DataSource._initializeUser() 5")
                        return True
                    else:
                        warning = self._getWarning(1005, 1106, name)
                else:
                    warning = self._getWarning(1006, 1107, name)
            else:
                warning = self._getWarning(1004, 1108, name)
        else:
            warning = self._getWarning(1003, 1105, g_oauth2)
        self.Warnings = warning
        return False

    def _getWarning(self, state, code, format):
        state = getMessage(self.ctx, state)
        msg = getMessage(self.ctx, code, format)
        warning = getSqlException(state, code, msg, self)
        return warning
