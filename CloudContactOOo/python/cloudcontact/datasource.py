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
        if user.Request is not None:
            if user.MetaData is not None:
                user.setDataBase(self.DataBase.getDataSource(), password, self.sync)
                return True
            if self.Provider.isOnLine():
                data = self.Provider.getUser(user.Request, user)
                if data.IsPresent:
                    userid = self.Provider.getUserId(data.Value)
                    user.MetaData = self.DataBase.insertUser(userid, name)
                    credential = user.getCredential(password)
                    if self.DataBase.createUser(*credential):
                        self.DataBase.createGroupView(user, g_group, user.Group)
                        user.setDataBase(self.DataBase.getDataSource(), password, self.sync)
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








    def shutdownDataBase(self, compact=False):
        try:
            print("DataSource.shutdownDataBase() 1")
            level = INFO
            msg = getMessage(self.ctx, 101, self.Provider.Host)
            print("DataSource.shutdownDataBase() 2")
            if self.Connection is None or self.Connection.isClosed():
                print("DataSource.shutdownDataBase() 3")
                level = SEVERE
                msg += getMessage(self.ctx, 103)
            else:
                print("DataSource.shutdownDataBase() 4")
                compact = self.replicator.Compact
                query = getSqlQuery(self.ctx, 'shutdown', compact)
                print("DataSource.shutdownDataBase() 5")
                self._Statement.execute(query)
                print("DataSource.shutdownDataBase() 6")
                msg += getMessage(self.ctx, 102)
            logMessage(self.ctx, level, msg, 'DataSource', 'queryTermination()')
            print("DataSource.shutdownDataBase() %s" % msg)
        except Exception as e:
            print("datasource.shutdownDataBase() ERROR: %s - %s" % (e, traceback.print_exc()))

    # XTerminateListener
    def queryTermination(self, event):
        level = INFO
        msg = getMessage(self.ctx, 101, self.Provider.Host)
        print("DataSource.queryTermination() 1")
        self.event.set()
        self.replicator.join(30)
        print("DataSource.queryTermination() 2")
        if self.Connection is None or self.Connection.isClosed():
            level = SEVERE
            msg += getMessage(self.ctx, 103)
        else:
            compact = self.count >= g_compact
            query = getSqlQuery(self.ctx, 'shutdown', compact)
            print("DataSource.queryTermination() 3")
            self._Statement.execute(query)
            msg += getMessage(self.ctx, 102)
        logMessage(self.ctx, level, msg, 'DataSource', 'queryTermination()')
        print("DataSource.queryTermination() 4 - %s" % msg)
    def notifyTermination(self, event):
        pass

    def isConnected(self):
        print("DataSource.isConnected() 1")
        if self.Connection is not None and not self.Connection.isClosed():
            return True
        dbname = self.Provider.Host
        print("DataSource.isConnected() 2")
        url, self.Warnings = getDataSourceUrl(self.ctx, dbname, g_identifier, True)
        print("DataSource.isConnected() 3 %s" % url)
        if self.Warnings is not None:
            return False
        print("DataSource.isConnected() 4")
        connection, self.Warnings = getDataSourceConnection(self.ctx, url, dbname)
        if self.Warnings is not None:
            return False
        print("DataSource.isConnected() 5")
        # Piggyback DataBase Connections (easy and clean ShutDown ;-) )
        self._Statement = connection.createStatement()
        # Add a TerminateListener  which is responsible for the shutdown of the database
        desktop = 'com.sun.star.frame.Desktop'
        print("DataSource.isConnected() 6")
        self.ctx.ServiceManager.createInstance(desktop).addTerminateListener(self)
        print("DataSource.connect() OK")
        #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
        #mri.inspect(connection)
        return True
