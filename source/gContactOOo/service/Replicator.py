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

from gcontact import Cancel

from queue import SimpleQueue

from gcontact import executeReplicator
from gcontact import getConfiguration
from gcontact import getLogger

from gcontact import g_identifier
from gcontact import g_synclog

import traceback


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = 'io.github.prrvchr.gContactOOo.Replicator'
g_ServiceNames = ('io.github.prrvchr.gContactOOo.Replicator',
                  'com.sun.star.task.Job')


class Replicator(unohelper.Base,
                 XServiceInfo,
                 XAsyncJob):
    def __init__(self, ctx):
        print("Replicator.__init__() 1")
        self._ctx = ctx
        self._config = getConfiguration(ctx, g_identifier)
        self.cancel = Cancel()
        print("Replicator.__init__() 2")

    _queue = SimpleQueue()

    # com.sun.star.task.XAsyncJob
    def executeAsync(self, arguments, listener):
        try:
            print("Replicator.executeAsync() 1")
            queue = Replicator._queue
            queue.put(arguments, listener)
            if queue.qsize() == 1:
                self.cancel.reset()
                logger = getLogger(self._ctx, g_synclog)
                timeout = self._config.getByName('ReplicateTimeout')
                executeReplicator(self._ctx, self, logger, self.cancel, timeout, queue)
            print("Replicator.executeAsync() 2")
        except Exception:
            print("Replicator.executeAsync() ERROR: %s" % traceback.format_exc())
            if listener is not None:
                listener.jobFinished(self, None)
        return None

    # XComponent
    def dispose(self):
        self.cancel.set(disposed=True)

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)

    def getImplementationName(self):
        return g_ImplementationName

    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(Replicator,
                                         g_ImplementationName,
                                         g_ServiceNames)
