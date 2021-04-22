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
from com.sun.star.sdbc import XDriver
from com.sun.star.sdbcx import XDataDefinitionSupplier
from com.sun.star.sdbcx import XCreateCatalog
from com.sun.star.sdbcx import XDropCatalog

from com.sun.star.sdbc import SQLException

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from gcontact import DataSource

from gcontact import g_identifier
from gcontact import g_host
from gcontact import getDataBaseInfo
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
             XServiceInfo,
             XDataDefinitionSupplier,
             XCreateCatalog,
             XDropCatalog,
             XDriver):
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

    # XDataDefinitionSupplier
    def getDataDefinitionByConnection(self, connection):
        return connection
    def getDataDefinitionByURL(self, url, infos):
        connection = self.connect(url, infos)
        return self.getDataDefinitionByConnection(connection)

    # XCreateCatalog
    def createCatalog(self, info):
        pass

    # XDropCatalog
    def dropCatalog(self, name, info):
        pass

    # XDriver
    def connect(self, url, infos):
        try:
            print("Driver.connect() 1")
            msg = getMessage(self._ctx, g_message, 111, url)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            protocols = url.strip().split(':')
            if len(protocols) != 4 or not all(protocols):
                state = getMessage(self._ctx, g_message, 112)
                msg = getMessage(self._ctx, g_message, 1101, url)
                raise getSqlException(state, 1101, msg, self)
            username = protocols[3]
            password = ''
            print("Driver.connect() 2")
            if not validators.email(username):
                state = getMessage(self._ctx, g_message, 113)
                msg = getMessage(self._ctx, g_message, 1102, username)
                msg += getMessage(self._ctx, g_message, 1103)
                raise getSqlException(state, 1104, msg, self)
            print("Driver.connect() 3")
            msg = getMessage(self._ctx, g_message, 114, g_host)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            print("Driver.connect() 4")
            self.DataSource.setUser(username, password)
            print("Driver.connect() 5")
            msg = getMessage(self._ctx, g_message, 118, username)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            connection = self.DataSource.getConnection(username, password)
            print("Driver.connect() 6")
            msg = getMessage(self._ctx, g_message, 119, username)
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            version = connection.getMetaData().getDriverVersion()
            msg = getMessage(self._ctx, g_message, 120, (version, username))
            logMessage(self._ctx, INFO, msg, 'Driver', 'connect()')
            print("Driver.connect() 7")
            return connection
        except SQLException as e:
            raise e
        except Exception as e:
            msg = getMessage(self._ctx, g_message, 121, (e, traceback.print_exc()))
            logMessage(self._ctx, SEVERE, msg, 'Driver', 'connect()')
            print(msg)

    def acceptsURL(self, url):
        msg = 'Load request for url: %s' % url
        logMessage(self._ctx, INFO, msg, 'Driver', 'acceptsURL()')
        value = url.startswith(self._supportedProtocol)
        return value

    def getPropertyInfo(self, url, infos):
        try:
            #for info in infos:
            #    print("Driver.getPropertyInfo():   %s - '%s'" % (info.Name, info.Value))
            drvinfo = []
            dbinfo = getDataBaseInfo()
            for info in dbinfo:
                drvinfo.append(self._getDriverPropertyInfo(info, dbinfo[info]))
            for info in infos:
                if info.Name not in dbinfo:
                    drvinfo.append(self._getDriverPropertyInfo(info.Name, info.Value))
            #for info in drvinfo:
            #    print("Driver.getPropertyInfo():   %s - %s" % (info.Name, info.Value))
            return tuple(drvinfo)
        except Exception as e:
            print("Driver.getPropertyInfo() ERROR: %s - %s" % (e, traceback.print_exc()))

    def getMajorVersion(self):
        return 1
    def getMinorVersion(self):
        return 0

    def _getSupplierWarnings(self, supplier, error):
        self._getWarnings(supplier, error)
        supplier.clearWarnings()

    def _getWarnings(self, supplier, error):
        warning = supplier.getWarnings()
        if warning:
            error.NextException = warning
            self._getWarnings(supplier, warning)

    def _getException(self, state, code, message, context=None, exception=None):
        error = SQLException()
        error.SQLState = state
        error.ErrorCode = code
        error.NextException = exception
        error.Message = message
        error.Context = context
        return error

    def _getDriverPropertyInfo(self, name, value):
        info = uno.createUnoStruct('com.sun.star.sdbc.DriverPropertyInfo')
        info.Name = name
        required = value is not None and not isinstance(value, tuple)
        info.IsRequired = required
        if required:
            info.Value = value
        info.Choices = ()
        return info

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
