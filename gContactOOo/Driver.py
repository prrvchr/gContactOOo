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

from com.sun.star.lang import XServiceInfo

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.sdbc import SQLException
from com.sun.star.sdbc import XDriver

from com.sun.star.sdbcx import XCreateCatalog
from com.sun.star.sdbcx import XDataDefinitionSupplier
from com.sun.star.sdbcx import XDropCatalog

from gcontact import DataSource

from gcontact import g_identifier
from gcontact import g_host
from gcontact import getDriverPropertyInfos
from gcontact import getSqlException

from gcontact import logMessage
from gcontact import getMessage
g_message = 'Driver'

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
        msg = getMessage(ctx, g_message, 101)
        logMessage(ctx, INFO, msg, 'Driver', '__init__()')

    _dataSource = None

    @property
    def DataSource(self):
        if Driver._dataSource is None:
            Driver._dataSource = DataSource(self._ctx)
        return Driver._dataSource

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
            msg = getMessage(self._ctx, g_message, 111, url)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            protocols = url.strip().split(':')
            if len(protocols) != 4 or not all(protocols):
                state = getMessage(self._ctx, g_message, 112)
                msg = getMessage(self._ctx, g_message, 1101, url)
                raise getSqlException(state, 1101, msg, self)
            username = protocols[3]
            password = ''
            if not validators.email(username):
                state = getMessage(self._ctx, g_message, 113)
                msg = getMessage(self._ctx, g_message, 1102, username)
                msg += getMessage(self._ctx, g_message, 1103)
                raise getSqlException(state, 1104, msg, self)
            msg = getMessage(self._ctx, g_message, 114, g_host)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            self.DataSource.setUser(username, password)
            msg = getMessage(self._ctx, g_message, 118, username)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            connection = self.DataSource.getConnection(username, password)
            msg = getMessage(self._ctx, g_message, 119, username)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            version = connection.getMetaData().getDriverVersion()
            msg = getMessage(self._ctx, g_message, 120, (version, username))
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            return connection
        except SQLException as e:
            raise e
        except Exception as e:
            msg = getMessage(self._ctx, g_message, 121, (e, traceback.print_exc()))
            logMessage(self._ctx, SEVERE, msg, 'Driver', 'connect()')
            print(msg)

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
