#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-25 https://prrvchr.github.io                                  ║
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
from com.sun.star.task import XAsyncJob

from gcontact.logger.dialog.logmanager import LogManager

from gcontact.unotool import findFrame
from gcontact.unotool import getJobArguments
from gcontact.unotool import notifyDispatch

import traceback


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = 'io.github.prrvchr.gContactOOo.Logger'
g_ServiceNames = ('io.github.prrvchr.gContactOOo.Logger',
                  'com.sun.star.task.Job')


class Logger(unohelper.Base,
             XServiceInfo,
             XAsyncJob):
    def __init__(self, ctx):
        print("Logger.__init__() 1")
        self._ctx = ctx

    # XAsyncJob
    def executeAsync(self, arguments, listener):
        print("Logger.executeAsync() 1")
        try:
            kwargs = getJobArguments(arguments)
            name = kwargs.get('name', None)
            if name:
                frame = findFrame(self._ctx, name)
                if frame:
                    frame.getContainerWindow().toFront()
                    notifyDispatch(self, kwargs.get('dispatch'))
                else:
                    LogManager(self._ctx, self, **kwargs)
                print("Logger.executeAsync() 2")
        except Exception:
            # FIXME: It is essential to notify LibreOffice of
            # FIXME: the Job's completion so as not to block its loading.
            print("Logger.executeAsync() ERROR: %s" % traceback.format_exc())
            pass
        finally:
            if listener is not None:
                listener.jobFinished(self, None)
        return None

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)

    def getImplementationName(self):
        return g_ImplementationName

    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(Logger,
                                         g_ImplementationName,
                                         g_ServiceNames)
