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

from com.sun.star.frame import XNotifyingDispatch

from com.sun.star.frame.DispatchResultState import SUCCESS
from com.sun.star.frame.DispatchResultState import FAILURE

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from gcontact import createService
from gcontact import createMessageBox

import traceback


class Dispatch(unohelper.Base,
               XNotifyingDispatch):
    def __init__(self, ctx, parent):
        self._ctx = ctx
        self._parent = parent
        self._listeners = []


# XNotifyingDispatch
    def dispatchWithNotification(self, url, arguments, listener):
        state, result = self.dispatch(url, arguments)
        struct = 'com.sun.star.frame.DispatchResultEvent'
        notification = uno.createUnoStruct(struct, self, state, result)
        listener.dispatchFinished(notification)

    def dispatch(self, url, arguments):
        state = SUCCESS
        result = None
        if url.Path == 'request':
            state, result = self._getRequest(arguments)
        return state, result

    def addStatusListener(self, listener, url):
        pass

    def removeStatusListener(self, listener, url):
        pass

# Dispatch private methods
    def _getRequest(self, arguments):
        try:
            state = FAILURE
            result = None
            mri = createService(self._ctx, 'mytools.Mri')
            window = self._parent.getToolkit().getActiveTopWindow()
            print("Dispatch._getRequest() 1 %s" % window)
            #mri.inspect(window)
            box = createMessageBox(self._parent, 'Test', 'Test')
            if box.execute():
                print("Dispatch._getRequest() 2")
            print("Dispatch._getRequest() 3")
            return state, result
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            print(msg)
