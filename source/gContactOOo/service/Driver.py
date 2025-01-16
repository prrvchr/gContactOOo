#!
# -*- coding: utf-8 -*-

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

import unohelper

from com.sun.star.lang import XServiceInfo

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.sdbc import SQLException
from com.sun.star.sdbc import XDriver

from com.sun.star.sdbcx import XCreateCatalog
from com.sun.star.sdbcx import XDataDefinitionSupplier
from com.sun.star.sdbcx import XDropCatalog

from gcontact import DataSource

from gcontact import getDataSourceUrl
from gcontact import getDriverPropertyInfos
from gcontact import getLogger
from gcontact import getLogException

from gcontact import g_defaultlog
from gcontact import g_protocol
from gcontact import g_version

from gcontact import g_identifier
from gcontact import g_scheme
from gcontact import g_scope
from gcontact import g_host

import validators


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = f'{g_identifier}.Driver'


class Driver(unohelper.Base,
             XCreateCatalog,
             XDataDefinitionSupplier,
             XDriver,
             XDropCatalog,
             XServiceInfo):
    def __init__(self, ctx):
        self._cls = 'Driver'
        mtd = '__init__'
        self._ctx = ctx
        self._supportedProtocol = g_protocol
        self._logger = getLogger(ctx, g_defaultlog)
        self._logger.logprb(INFO, self._cls, mtd, 1101)

    __datasource = None

    @property
    def DataSource(self):
        if Driver.__datasource is None:
            Driver.__datasource = self._getDataSource()
        return Driver.__datasource

# XCreateCatalog
    def createCatalog(self, info):
        pass

# XDataDefinitionSupplier
    def getDataDefinitionByConnection(self, connection):
        return connection

    def getDataDefinitionByURL(self, url, infos):
        return self.connect(url, infos)

# XDriver
    def connect(self, url, infos):
        mtd = 'connect'
        self._logger.logprb(INFO, self._cls, mtd, 1111, url)
        protocols = url.strip().split(':')
        if len(protocols) != 4 or not all(protocols):
            raise getLogException(self._logger, self, 1000, 1112, self._cls, mtd, url)
        username = protocols[3]
        if not validators.email(username):
            raise getLogException(self._logger, self, 1001, 1114, self._cls, mtd, username)
        connection = self.DataSource.getConnection(self, g_scope, g_scheme, g_host, username)
        version = self.DataSource.DataBase.Version
        name = connection.getMetaData().getUserName()
        self._logger.logprb(INFO, self._cls, mtd, 1115, version, name)
        return connection

    def acceptsURL(self, url):
        accept = url.startswith(self._supportedProtocol)
        return accept

    def getPropertyInfo(self, url, infos):
        properties = ()
        if self.acceptsURL(url):
            properties = getDriverPropertyInfos()
        return properties

    def getMajorVersion(self):
        return 1

    def getMinorVersion(self):
        return 0

# XDropCatalog
    def dropCatalog(self, name, info):
        pass

# XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)

    def getImplementationName(self):
        return g_ImplementationName

    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)

# Private getter methods
    def _getDataSource(self):
        mtd = '_getDataSource'
        url = getDataSourceUrl(self._ctx, self._logger, self, 1003, 1121, self._cls, mtd)
        try:
            datasource = DataSource(self._ctx, self._logger, url)
        except SQLException as e:
            raise getLogException(self._logger, self, 1005, 1123, self._cls, mtd, url, e.Message)
        except Exception as e:
            raise getLogException(self._logger, self, 1005, 1123, self._cls, mtd, url, str(e))
        if not datasource.isUptoDate():
            raise getLogException(self._logger, self, 1005, 1124, self._cls, mtd, datasource.getDataBaseVersion(), g_version)
        return datasource


g_ImplementationHelper.addImplementation(Driver,
                                         g_ImplementationName,
                                        (g_ImplementationName,
                                        'com.sun.star.sdbc.Driver',
                                        'com.sun.star.sdbcx.Driver'))
