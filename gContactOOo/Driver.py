#!
# -*- coding: utf_8 -*-

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
from com.sun.star.sdbc.ResultSetType import SCROLL_INSENSITIVE
from com.sun.star.sdbc.ResultSetType import SCROLL_SENSITIVE
from com.sun.star.sdbc.ResultSetType import FORWARD_ONLY
from com.sun.star.sdbc.ResultSetConcurrency import READ_ONLY
from com.sun.star.sdbc.ResultSetConcurrency import UPDATABLE


from com.sun.star.uno import Exception as UnoException

from unolib import getConfiguration

from cloudcontact import g_identifier
from cloudcontact import User
from cloudcontact import DataSource
from cloudcontact import Connection
from cloudcontact import getDataSourceUrl
from cloudcontact import getDataSourceConnection
from cloudcontact import getDataBaseInfo
from cloudcontact import logMessage

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

    __dataSource = None
    __usersPool = {}

    def __init__(self, ctx):
        self.ctx = ctx
        self._supportedProtocol = 'sdbc:google:'
        self._supportedSubProtocols = ('people', 'peoples')
        print("Driver.__init__()")

    def __del__(self):
        print("Driver.__del__()")

    @property
    def DataSource(self):
        if Driver.__dataSource is None:
            Driver.__dataSource = DataSource(self.ctx)
        return Driver.__dataSource

    # XDataDefinitionSupplier
    def getDataDefinitionByConnection(self, connection):
        return connection.getTables()
    def getDataDefinitionByURL(self, url, infos):
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
            protocols = url.strip().split(':')
            username, password = self._getUserCredential(infos)
            print("Driver.connect() 1 %s - %s - %s" % (username, password, url))
            if len(protocols) != 3 or not all(protocols):
                msg = "Invalide protocol: '%s'" % url
                raise self._getException('Protocol ERROR', 1001, msg, self)
            elif not self._isSupportedSubProtocols(protocols):
                msg = "Invalide subprotocol: '%s' are not supported\n" % protocols[2]
                msg += "Supported subprotocols are: %s" % self._getSupportedSubProtocols()
                raise self._getException('Protocol ERROR', 1002, msg, self)
            elif not username:
                msg = "You must provide a UserName!"
                raise self._getException('Authentication ERROR', 1003, msg, self)
            level = INFO
            scheme = self.DataSource.Provider.Host
            msg = "Driver for Scheme: %s loading ... " % scheme
            print("Driver.connect() 2 *****************")
            if not self.DataSource.isConnected():
                print("Driver.connect() 3 *****************")
                warning = self.DataSource.getWarnings()
                self._getSupplierWarnings(self.DataSource, warning)
                msg = "Could not connect to DataSource at URL:"
                raise self._getException('DataBase ERROR', 1003, msg, self, warning)
            user = self.DataSource.getUser(username, password)
            if user is None:
                warning = self.DataSource.getWarnings()
                self._getSupplierWarnings(self.DataSource, warning)
                msg = "Could not retrive user: %s from DataSource: %s" % (username, scheme)
                raise self._getException('DataBase ERROR', 1003, msg, self, warning)
                print("Driver.connect() 4 *****************")
            msg += "Done"
            logMessage(self.ctx, INFO, msg, 'Driver', 'connect()')
            #connection = user.getConnection(scheme, password)
            connection = Connection(self.ctx, user, scheme, password, protocols)
            print("Driver.connect() 5 %s" % connection.isClosed())
            version = connection.getMetaData().getDriverVersion()
            print("Driver.connect() 6 %s" % version)
            return connection
        except SQLException as e:
            raise e
        except Exception as e:
            print("Driver.connect() ERROR: %s - %s" % (e, traceback.print_exc()))

    def acceptsURL(self, url):
        print("Driver.acceptsURL() %s" % url)
        return url.startswith(self._supportedProtocol)

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

    def _getUserCredential(self, infos):
        username = ''
        password = ''
        for info in infos:
            if info.Name == 'user':
                username = info.Value.strip()
            elif info.Name == 'password':
                password = info.Value.strip()
            if username and password:
                break
        return username, password

    def _getSupportedSubProtocols(self):
        return ', '.join(self._supportedSubProtocols).title()

    def _isSupportedSubProtocols(self, protocols):
        return protocols[2].lower() in self._supportedSubProtocols

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
