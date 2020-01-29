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
from .dbtools import getWarning

import traceback


class User(unohelper.Base,
           XRestUser):
    def __init__(self, ctx, datasource, name):
        self.ctx = ctx
        self._Statement = None
        self._Warnings = []
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

    def getWarnings(self):
        if self._Warnings:
            return self._Warnings.pop(0)
        return None
    def clearWarnings(self):
        self._Warnings = []

    def setMetaData(self, metadata):
        self.MetaData = metadata

    def getConnection(self, scheme, password):
        url, error = getDataSourceUrl(self.ctx, scheme, g_identifier, False)
        if error is None:
            credential = self.getCredential(password)
            print("User.getConnection() 1 %s - %s" % credential)
            connection, error = getDataBaseConnection(self.ctx, url, scheme, *credential)
            if error is None:
                return connection
            else:
                state = "DataBase ERROR"
                code = 1017
                msg = "ERROR: Can't connect to new DataBase: %s" % scheme
        else:
            state = "DataBase ERROR"
            code = 1016
            msg = "ERROR: Can't create new DataBase: %s" % scheme
        warning = getWarning(state, code, msg, self, error)
        self._Warnings.append(warning)
        return False

    def getCredential(self, password):
        return self.Resource, password
