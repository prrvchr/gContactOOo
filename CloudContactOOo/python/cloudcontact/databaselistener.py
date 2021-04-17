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

from com.sun.star.util import XCloseListener

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from .configuration import g_compact

from .logger import logMessage
from .logger import getMessage

import traceback


class DataBaseListener(unohelper.Base,
                       XCloseListener):
    def __init__(self, ctx, replicator):
        print("DataBaseListener.__init__() 1")
        self._ctx = ctx
        self._replicator = replicator
        print("DataBaseListener.__init__() 2")

    # XCloseListener
    def queryClosing(self, source, ownership):
        print("DataBaseListener.queryClosing() 1")
        if self._replicator.is_alive():
            self._replicator.cancel()
            self._replicator.join()
        print("DataBaseListener.queryClosing() 2")
        compact = self._replicator.count >= g_compact
        self._replicator.DataBase.shutdownDataBase(compact)
        print("DataBaseListener.queryClosing() 3")
        msg = "DataSource queryClosing: Scheme: %s ... Done" % self._replicator.Provider.Host
        logMessage(self._ctx, INFO, msg, 'DataBaseListener', 'queryClosing()')
        print(msg)
    def notifyClosing(self, source):
        pass
