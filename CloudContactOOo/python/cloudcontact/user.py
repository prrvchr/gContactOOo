#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE
from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.sdbc import XRestUser

from .configuration import g_identifier
from .dbinit import getDataSourceUrl
from .dbtools import getDataSourceConnection
from .dbtools import getDataBaseConnection

import traceback


class User(unohelper.Base,
           XRestUser):
    def __init__(self, ctx, datasource, name):
        self.ctx = ctx
        self._Statement = None
        self._Warnings = None
        self.Request = datasource.getRequest(name)
        self.MetaData = datasource.selectUser(name)

    @property
    def People(self):
        return self.MetaData.getDefaultValue('People', None)
    @property
    def Resource(self):
        return self.MetaData.getDefaultValue('Resource', None)
    @property
    def Account(self):
        return self.MetaData.getDefaultValue('Account', None)
    @property
    def Token(self):
        return self.MetaData.getDefaultValue('Token', None)
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

    def setMetaData(self, metadata):
        self.MetaData = metadata

    def getConnection(self, dbname, password):
        url, self.Warnings = getDataSourceUrl(self.ctx, dbname, g_identifier, False)
        if self.Warnings is None:
            credential = self.getCredential(password)
            connection, self.Warnings = getDataBaseConnection(self.ctx, url, dbname, *credential)
            if self.Warnings is None:
                return connection
        return None

    def getCredential(self, password):
        return self.Resource, password
