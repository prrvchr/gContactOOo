#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE
from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.sdbc import XRestUser

from unolib import getRequest

from .configuration import g_identifier
from .dbinit import getDataSourceUrl
from .dbtools import getDataSourceConnection
from .dbtools import getDataBaseConnection

import traceback


class User(unohelper.Base,
           XRestUser):
    def __init__(self, ctx, source, name, database=None):
        self.ctx = ctx
        self.DataBase = database
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

    def setMetaData(self, metadata):
        self.MetaData = metadata

    def getConnection(self):
        return self.DataBase.Connection

    def getConnection1(self, dbname, password):
        url, self.Warnings = getDataSourceUrl(self.ctx, dbname, g_identifier, True)
        if self.Warnings is None:
            credential = self.getCredential(password)
            connection, self.Warnings = getDataSourceConnection(self.ctx, url, dbname, *credential)
            #connection, self.Warnings = getDataBaseConnection(self.ctx, url, dbname, *credential)
            if self.Warnings is None:
                #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
                #mri.inspect(connection)
                return connection
        return None

    def setDataBase(self, datasource, password, sync):
        name, password = self.getCredential(password)
        self.DataBase = DataBase(self.ctx, datasource, name, password, sync)

    def getCredential(self, password):
        return self.Account, password
