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

from unolib import getConfiguration

from gcontact import User
from gcontact import DataSource
from gcontact import Connection

from gcontact import g_identifier
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

from threading import Event


class Driver(unohelper.Base,
             XServiceInfo,
             XDataDefinitionSupplier,
             XCreateCatalog,
             XDropCatalog,
             XDriver):

    _dataSource = None

    def __init__(self, ctx):
        self.ctx = ctx
        self._supportedProtocol = 'sdbc:address:google'
        self.event = Event()
        msg = getMessage(self.ctx, g_message, 101)
        print(msg)
        logMessage(self.ctx, INFO, msg, 'Driver', '__init__()')

    @property
    def DataSource(self):
        if Driver._dataSource is None:
            Driver._dataSource = DataSource(self.ctx, self.event)
        return Driver._dataSource

    # XDataDefinitionSupplier
    def getDataDefinitionByConnection(self, connection):
        print("Driver.getDataDefinitionByConnection()")
        return connection
    def getDataDefinitionByURL(self, url, infos):
        print("Driver.getDataDefinitionByURL()")
        connection = self.connect(url, infos)
        return self.getDataDefinitionByConnection(connection)

    # XCreateCatalog
    def createCatalog(self, info):
        print("Driver.createCatalog()")

    # XDropCatalog
    def dropCatalog(self, name, info):
        print("Driver.dropCatalog()")

    # XDriver
    def connect(self, url, infos):
        try:
            msg = getMessage(self.ctx, g_message, 111, url)
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            print("Driver.connect() 1")
            protocols = url.strip().split(':')
            if len(protocols) != 4 or not all(protocols):
                state = getMessage(self.ctx, g_message, 112)
                msg = getMessage(self.ctx, g_message, 1101, url)
                raise getSqlException(state, 1101, msg, self)
            username = protocols[3]
            password = ''
            if not validators.email(username):
                state = getMessage(self.ctx, g_message, 113)
                msg = getMessage(self.ctx, g_message, 1102, username)
                msg += getMessage(self.ctx, g_message, 1103)
                raise getSqlException(state, 1104, msg, self)
            level = INFO
            print("Driver.connect() 2")
            dbname = self.DataSource.Provider.Host
            msg = getMessage(self.ctx, g_message, 114, dbname)
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            print("Driver.connect() 3")
            if not self.DataSource.isValid():
                state = getMessage(self.ctx, g_message, 115)
                msg = self.DataSource.Error
                logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
                raise getSqlException(state, 1104, msg, self)
            msg = getMessage(self.ctx, g_message, 116, dbname)
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            user = self.DataSource.getUser(username, password)
            print("Driver.connect() 4")
            if user is None:
                msg = getMessage(self.ctx, g_message, 117, username)
                logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
                raise self.DataSource.getWarnings()
            msg = getMessage(self.ctx, g_message, 118, username)
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            datasource = self.DataSource.DataBase.getDataSource()
            connection = user.getConnection(datasource, url, password, self.event)
            print("Driver.connect() 5")
            if connection is None:
                raise user.getWarnings()
            msg = getMessage(self.ctx, g_message, 119, username)
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            print("Driver.connect() 6 %s" % connection.isClosed())
            version = connection.getMetaData().getDriverVersion()
            msg = getMessage(self.ctx, g_message, 120, (version, username))
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            print("Driver.connect() 7 %s" % version)
            return connection
        except SQLException as e:
            raise e
        except Exception as e:
            msg = getMessage(self.ctx, g_message, 121, (e, traceback.print_exc()))
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            print(msg)

    def acceptsURL(self, url):
        msg = 'Load request for url: %s' % url
        logMessage(self.ctx, INFO, msg, 'Driver', 'acceptsURL()')
        print("Driver.acceptsURL() %s" % url)
        value = url.startswith(self._supportedProtocol)
        print("Driver.acceptsURL() %s" % value)
        return value

    def getPropertyInfo(self, url, infos):
        try:
            print("Driver.getPropertyInfo() %s" % url)
            for info in infos:
                print("Driver.getPropertyInfo():   %s - '%s'" % (info.Name, info.Value))
            drvinfo = []
            dbinfo = getDataBaseInfo()
            for info in dbinfo:
                drvinfo.append(self._getDriverPropertyInfo(info, dbinfo[info]))
            for info in infos:
                if info.Name not in dbinfo:
                    drvinfo.append(self._getDriverPropertyInfo(info.Name, info.Value))
            print("Driver.getPropertyInfo():\n")
            for info in drvinfo:
                print("Driver.getPropertyInfo():   %s - %s" % (info.Name, info.Value))
            return tuple(drvinfo)
        except Exception as e:
            print("Driver.getPropertyInfo() ERROR: %s - %s" % (e, traceback.print_exc()))

    def getMajorVersion(self):
        print("Driver.getMajorVersion()")
        return 1
    def getMinorVersion(self):
        print("Driver.getMinorVersion()")
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
        print("Driver._getDriverPropertyInfo() %s - %s - %s" % (name, value, type(value)))
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
