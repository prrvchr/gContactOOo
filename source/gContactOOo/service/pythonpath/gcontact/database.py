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

from .card import DataBase as DataBaseSuper

import json
import traceback


class DataBase(DataBaseSuper):

    def getMetaData(self, tag, default=None, dot='.', sep=','):
        try:
            paths =  dict(list(self._getPaths(tag, dot)))
            maps = dict(list(self._getMaps(tag, dot)))
            types = dict(list(self._getTypes(tag, dot)))
            tmps = list(self._getTmps(tag, dot))
            fields = next(self._getFields(default, sep))
        except Exception as e:
            msg = "Error: %s" % traceback.print_exc()
            print(msg)
        return paths, maps, types, tmps, fields

    def _getPaths(self, tag, dot):
        sep = dot + tag + dot
        call = self._getCall('getPaths')
        result = call.executeQuery()
        while result.next():
            key = result.getString(1) + sep + result.getString(2) + sep + result.getString(3)
            value = result.getString(4)
            print("DataBase._getPaths() key: '%s' - Value: %s" % (key, value))
            yield key, value
        result.close()
        call.close()

    def _getMaps(self, tag, dot):
        sep = dot + tag + dot
        call = self._getCall('getMaps')
        result = call.executeQuery()
        while result.next():
            key = result.getString(1) + sep + result.getString(2) + dot + tag
            paths = result.getArray(3).getArray(None)
            print("DataBase._getMaps() key: '%s' - List: %s" % (key, paths))
            yield key, paths
        result.close()
        call.close()

    def _getTypes(self, tag, dot):
        sep = dot + tag + dot
        call = self._getCall('getTypes')
        result = call.executeQuery()
        while result.next():
            key = result.getString(1) + sep + result.getString(2) + sep + result.getString(3)
            maps = {}
            for map in result.getArray(4).getArray(None):
                maps.update(json.loads(map))
            print("DataBase._getTypes() key: '%s' - Dict: %s" % (key, maps))
            yield key, maps
        result.close()
        call.close()

    def _getTmps(self, tag, dot):
        sep = dot + tag + dot
        call = self._getCall('getTmps')
        result = call.executeQuery()
        while result.next():
            key = result.getString(1)
            key += sep + result.getString(2)
            key += sep + result.getString(3)
            print("DataBase._getTmps() key: '%s'" % key)
            yield key
        result.close()
        call.close()

    def _getFields(self, defaults, sep):
        fields = defaults.split(sep)
        call = self._getCall('getFields')
        result = call.executeQuery()
        while result.next():
            fields.append(result.getString(1))
        result.close()
        call.close()
        print("DataBase._getFields() Fields: '%s'" % sep.join(fields))
        yield sep.join(fields)

