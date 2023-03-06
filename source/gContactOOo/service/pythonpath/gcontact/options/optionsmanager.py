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

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from ..unotool import getDesktop
from ..unotool import getResourceLocation
from ..unotool import getSimpleFile

from ..logger import LogManager

from ..configuration import g_identifier
from ..configuration import g_host
from ..configuration import g_driverlog

from ..dbconfig  import g_folder

import os
import sys
import traceback


class OptionsManager(unohelper.Base):
    def __init__(self, ctx, window):
        self._ctx = ctx
        print("OptionsManager.__init__() 1")
        version  = ' '.join(sys.version.split())
        path = os.pathsep.join(sys.path)
        infos = {111: version, 112: path}
        self._logger = LogManager(ctx, window.getPeer(), infos, g_identifier, g_driverlog)
        self._window = window
        print("OptionsManager.__init__() 2")

    def loadSetting(self):
        self._logger.reloadSetting()

    def saveSetting(self):
        self._logger.saveSetting()

    def viewData(self):
        folder = g_folder + '/' + g_host
        location = getResourceLocation(self._ctx, g_identifier, folder)
        url = location + '.odb'
        if getSimpleFile(self._ctx).exists(url):
            desktop = getDesktop(self._ctx)
            desktop.loadComponentFromURL(url, '_default', 0, ())
            self._window.endDialog(OK)

