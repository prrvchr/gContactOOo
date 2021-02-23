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

from com.sun.star.util import XCloseListener

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.sdb.CommandType import QUERY

from com.sun.star.sdbc import XRestDataSource

from oauth2lib import g_oauth2

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
g_message = 'datasource'

import traceback


class DataSource(unohelper.Base,
                 XRestDataSource):
    def __init__(self, ctx, sync):
        print("DataSource.__init__() 1")
        self._ctx = ctx
        self._Warnings = None
        self._Users = {}
        self.sync = sync
        self.Error = None
        self.Provider = Provider(ctx)
        dbname = self.Provider.Host
        datasource, url, created = getDataSource(ctx, dbname, g_identifier, True)
        self.DataBase = DataBase(ctx, datasource)
        if created:
            self.Error = self.DataBase.createDataBase()
            if self.Error is None:
                self.DataBase.storeDataBase(url)
        self.Replicator = Replicator(ctx, datasource, self.Provider, self._Users, self.sync)
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

    # XRestDataSource
    def getUser(self, name, password):
        if name in self._Users:
            user = self._Users[name]
        else:
            user = User(self._ctx, self, name)
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
        state = getMessage(self._ctx, g_message, state)
        msg = getMessage(self._ctx, g_message, code, format)
        warning = getSqlException(state, code, msg, self)
        return warning
