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
from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.sdbc import XRestUser

from unolib import getRequest

from .database import DataBase

from .configuration import g_identifier
from .dbinit import getDataSourceUrl
from .dbtools import getDataSourceConnection
from .dbtools import getDataBaseConnection

import traceback


class User(unohelper.Base,
           XRestUser):
    def __init__(self, ctx, source, name):
        self.ctx = ctx
        self._Warnings = None
        self.MetaData = source.DataBase.selectUser(name)
        self.Fields = source.DataBase.getUserFields()
        self.Provider = source.Provider
        self.Request = getRequest(self.ctx, self.Provider.Host, name)

    @property
    def People(self):
        return self.MetaData.getDefaultValue('People', None)
    @property
    def Group(self):
        return self.MetaData.getDefaultValue('Group', None)
    @property
    def Resource(self):
        return self.MetaData.getDefaultValue('Resource', None)
    @property
    def Account(self):
        return self.MetaData.getDefaultValue('Account', None)
    @property
    def Name(self):
        account = self.MetaData.getDefaultValue('Account', '')
        return account.split('@').pop(0)
    @property
    def PeopleSync(self):
        return self.MetaData.getDefaultValue('PeopleSync', None)
    @property
    def GroupSync(self):
        return self.MetaData.getDefaultValue('GroupSync', None)
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

    def getConnection(self, datasource, password):
        name, password = self.getCredential(password)
        connection = datasource.getConnection(name, password)
        return connection

    def getCredential(self, password):
        return self.Account, password
