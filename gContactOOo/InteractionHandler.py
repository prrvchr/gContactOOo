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
from com.sun.star.lang import XInitialization
from com.sun.star.task import XInteractionHandler2

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK
from com.sun.star.ui.dialogs.ExecutableDialogResults import CANCEL

from com.sun.star.frame.FrameSearchFlag import GLOBAL

from com.sun.star.uno import Exception as UnoException
from com.sun.star.auth import OAuth2Request

from unolib import createService

from gcontact import g_identifier

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.InteractionHandler' % g_identifier


class InteractionHandler(unohelper.Base,
                         XServiceInfo,
                         XInitialization,
                         XInteractionHandler2):
    def __init__(self, ctx):
        self.ctx = ctx
        self._parent = None

    # XInitialization
    def initialize(self, properties):
        print("InteractionHandler.initialize() 1")
        for property in properties:
            print("InteractionHandler.initialize() 2")
            if property.Name == 'Parent':
                self._parent = property.Value
                print("InteractionHandler.initialize() 3 %s" % self._parent)

    # XInteractionHandler2, XInteractionHandler
    def handle(self, interaction):
        self.handleInteractionRequest(interaction)
    def handleInteractionRequest(self, interaction):
        # TODO: interaction.getRequest() does not seem to be functional under LibreOffice !!!
        # TODO: throw error AttributeError: "args"
        # TODO: on File "/usr/lib/python3/dist-packages/uno.py"
        # TODO: at line 525 in "_uno_struct__setattr__"
        # TODO: as a workaround we must set an "args" attribute of type "sequence<any>" to
        # TODO: IDL file of com.sun.star.auth.OAuth2Request Exception who is normally returned...
        print("InteractionHandler.handleInteractionRequest() 1")
        request = interaction.getRequest()
        print("InteractionHandler.handleInteractionRequest() 2 %s" % (dir(request), ))
        #mri = createService(self.ctx, 'mytools.Mri')
        #if mri:
        #    print("InteractionHandler.handleInteractionRequest() 3")
        #    mri.inspect(interaction)
        print("InteractionHandler.handleInteractionRequest() 4")

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(InteractionHandler,
                                         g_ImplementationName,
                                        (g_ImplementationName,))
