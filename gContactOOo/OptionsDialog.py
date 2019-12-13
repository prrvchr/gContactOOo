#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.awt import XDialogEventHandler
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from cloudcontact import g_identifier
from cloudcontact import getConfiguration

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OptionsDialog' % g_identifier


class OptionsDialog(unohelper.Base,
                    XServiceInfo,
                    XContainerWindowEventHandler,
                    XDialogEventHandler):
    def __init__(self, ctx):
        self.ctx = ctx

    # XContainerWindowEventHandler, XDialogEventHandler
    def callHandlerMethod(self, dialog, event, method):
        handled = False
        if method == 'external_event':
            if event == 'ok':
                self._saveSetting(dialog)
                handled = True
            elif event == 'back':
                self._loadSetting(dialog)
                handled = True
            elif event == 'initialize':
                self._loadSetting(dialog)
                handled = True
        elif method == 'LoadUcp':
            self._loadUcp(dialog)
            handled = True
        return handled
    def getSupportedMethodNames(self):
        return ('external_event', 'LoadUcp')

    def _loadSetting(self, dialog):
        pass

    def _saveSetting(self, dialog):
        pass

    def _loadUcp(self, window):
        try:
            print("OptionDialog._loadUcp()")
            configuration = getConfiguration(self.ctx, 'org.openoffice.Office.DataAccess', True)
            mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
            #mri.inspect(configuration)
            drivermgr = self.ctx.ServiceManager.createInstance('com.sun.star.sdbc.DriverManager')
            connection = drivermgr.getConnection('sdbc:google-contact:prrvchr')
            #drivers = drivermgr.createEnumeration()
            #while drivers.hasMoreElements():
            #    driver = drivers.nextElement()
            #    if driver:
            #        print("Driver: %s" % driver.getImplementationName())
            #        infos = driver.getPropertyInfo('sdbc:odbc://', ())
            #        for info in infos:
            #            print("Driver: %s" % info)
            #mri.inspect(connection)
        except Exception as e:
            print("OptionDialog._loadUcp() ERROR: %s - %s" % (e, traceback.print_exc()))

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OptionsDialog,
                                         g_ImplementationName,
                                        (g_ImplementationName,))
