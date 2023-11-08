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

from gcontact import DataBase

from gcontact import DataSource

from gcontact import checkVersion
from gcontact import getConnectionUrl
from gcontact import getDriverPropertyInfos
from gcontact import getExtensionVersion
from gcontact import getLogger
from gcontact import getOAuth2Version
from gcontact import getSqlException

from gcontact import g_oauth2ext
from gcontact import g_oauth2ver

from gcontact import g_jdbcext
from gcontact import g_jdbcid
from gcontact import g_jdbcver

from gcontact import g_extension
from gcontact import g_identifier
from gcontact import g_protocol
from gcontact import g_scheme
from gcontact import g_host
from gcontact import g_folder
from gcontact import g_defaultlog
from gcontact import g_version

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
        self._supportedProtocol = g_protocol
        self._logger = getLogger(ctx, g_defaultlog)
        self._logger.logprb(INFO, 'Driver', '__init__()', 101)

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
        connection = self.connect(url, infos)
        return self.getDataDefinitionByConnection(connection)

# XDriver
    def connect(self, url, infos):
        try:
            self._logger.logprb(INFO, 'Driver', 'connect()', 111, url)
            protocols = url.strip().split(':')
            if len(protocols) != 4 or not all(protocols):
                self._logSqlException(1101, url)
                raise self._getSqlException(112, 1101, url)
            username = protocols[3]
            password = ''
            if not validators.email(username):
                self._logSqlException(1102, username)
                raise self._getSqlException(113, 1102, username)
            connection = self.DataSource.getConnection(self, g_scheme, g_host, username, password)
            version = self.DataSource.DataBase.Version
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

# Private getter methods
    def _getDataSource(self):
        oauth2 = getOAuth2Version(self._ctx)
        driver = getExtensionVersion(self._ctx, g_jdbcid)
        if oauth2 is None:
            self._logSqlException(501, g_oauth2ext, ' ', g_extension)
            raise self._getSqlException(1003, 501, g_oauth2ext, '\n', g_extension)
        elif not checkVersion(oauth2, g_oauth2ver):
            self._logSqlException(502, oauth2, g_oauth2ext, ' ', g_oauth2ver)
            raise self._getSqlException(1003, 502, oauth2, g_oauth2ext, '\n', g_oauth2ver)
        elif driver is None:
            self._logSqlException(501, g_jdbcext, ' ', g_extension)
            raise self._getSqlException(1003, 501, g_jdbcext, '\n', g_extension)
        elif not checkVersion(driver, g_jdbcver):
            self._logSqlException(502, driver, g_jdbcext, ' ', g_jdbcver)
            raise self._getSqlException(1003, 502, driver, g_jdbcext, '\n', g_jdbcver)
        else:
            path = g_folder + '/' + g_host
            url = getConnectionUrl(self._ctx, path)
            try:
                database = DataBase(self._ctx, url)
            except SQLException as e:
                self._logSqlException(503, url, ' ', e.Message)
                raise self._getSqlException(1005, 503, url, '\n', e.Message)
            else:
                if not database.isUptoDate():
                    self._logSqlException(504, database.Version, ' ', g_version)
                    raise self._getSqlException(1005, 504, database.Version, '\n', g_version)
                else:
                    return DataSource(self._ctx, database)
        return None

    def _logSqlException(self, code, *args):
        self._logger.logprb(SEVERE, 'Driver', 'connect()', code, *args)

    def _getSqlException(self, state, code, *args):
        state = self._logger.resolveString(state)
        msg = self._logger.resolveString(code, *args)
        return getSqlException(state, code, msg, self)


g_ImplementationHelper.addImplementation(Driver,
                                         g_ImplementationName,
                                        (g_ImplementationName,
                                        'com.sun.star.sdbc.Driver',
                                        'com.sun.star.sdbcx.Driver'))
