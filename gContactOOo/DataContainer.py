#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.lang import XInitialization

from gcontact import g_identifier

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.DataContainer' % g_identifier


class DataContainer(unohelper.Base,
                    XServiceInfo,
                    XInitialization):

    def __init__(self, ctx):
        self.ctx = ctx
        print("DataContainer.__init__()")


    # XInitialization
    def initialize(self, args):
        print("DataContainer.initialize()")
        for arg in args:
            print("DataContainer.initialize() %s - %s" % (arg.Name, arg.Value))

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(DataContainer,
                                         g_ImplementationName,
                                        (g_ImplementationName,
                                        'com.sun.star.sdb.DefinitionContainer',
                                        'com.sun.star.sdb.DocumentContainer'))
