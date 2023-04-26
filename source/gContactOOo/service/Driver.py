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

import uno
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

from gcontact import getDriverPropertyInfos
from gcontact import getLogger
from gcontact import getSqlException

from gcontact import g_defaultlog
from gcontact import g_host
from gcontact import g_identifier
from gcontact import g_scheme

import validators
import traceback


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.Driver' % g_identifier


class Driver(unohelper.Base,
             XCreateCatalog,
             XDataDefinitionSupplier,
             XDriver,
             XDropCatalog,
             XServiceInfo):
    def __init__(self, ctx):
        self._ctx = ctx
        self._supportedProtocol = 'sdbc:address:google'
        self._logger = getLogger(ctx, g_defaultlog)
        self._logger.logprb(INFO, 'Driver', '__init__()', 101)

    _datasource = None

    @property
    def DataSource(self):
        if Driver._datasource is None:
            Driver._datasource = DataSource(self._ctx)
        return Driver._datasource

# XCreateCatalog
    def createCatalog(self, info):
        pass

# XDataDefinitionSupplier
    def getDataDefinitionByConnection(self, connection):
        return connection
    def getDataDefinitionByURL(self, url, infos):
        connection = self.connect(url, infos)
        return self.getDataDefinitionByConnection(connection)

# XDriver
    def connect(self, url, infos):
        try:
            self._logger.logprb(INFO, 'Driver', 'connect()', 111, url)
            protocols = url.strip().split(':')
            if len(protocols) != 4 or not all(protocols):
                raise getSqlException(self._ctx, self, 112, 1101, 'connect()', url)
            user, pwd = protocols[3], ''
            if not validators.email(user):
                raise getSqlException(self._ctx, self, 113, 1102, 'connect()', user)
            connection = self.DataSource.getConnection(g_scheme, g_host, user, pwd)
            version = connection.getMetaData().getDriverVersion()
            name = connection.getMetaData().getUserName()
            self._logger.logprb(INFO, 'Driver', 'connect()', 114, version, name)
            return connection
        except SQLException as e:
            raise e
        except Exception as e:
            self._logger.logprb(SEVERE, 'Driver', 'connect()', 115, e, traceback.format_exc())

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


g_ImplementationHelper.addImplementation(Driver,
                                         g_ImplementationName,
                                        (g_ImplementationName,
                                        'com.sun.star.sdbc.Driver',
                                        'com.sun.star.sdbcx.Driver'))
