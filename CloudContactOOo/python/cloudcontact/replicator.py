#!
# -*- coding: utf_8 -*-

#from __futur__ import absolute_import

import uno
import unohelper

from com.sun.star.util import XCancellable
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from unolib import KeyMap
from unolib import parseDateTime

from .dataparser import DataParser
from .dbtools import getDataSourceCall
from .logger import logMessage
from .logger import getMessage

from threading import Thread
import traceback


class Replicator(unohelper.Base,
                 XCancellable,
                 Thread):
    def __init__(self, ctx, datasource, lock):
        Thread.__init__(self)
        self.ctx = ctx
        self.datasource = datasource
        self.lock = lock
        self.running = True
        self._Calls = {}
        self._Fields = None
        self._Peoples = None
        self._Types = None
        self._Labels = None
        self.start()

    # XCancellable
    def cancel(self):
        if self.is_alive():
            self.running = False
            with self.lock:
                self.lock.notify()

    def run(self):
        while self.running:
            with self.lock:
                self.lock.wait()
            for user in self.datasource._UsersPool.values():
                if self.running:
                    self._synchronize(user)

    def _synchronize(self, user) :
        level = INFO
        status = False
        msg = getMessage(self.ctx, 110, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        try:
            if user.Request.isOffLine(self.datasource.Provider.Host):
                msg = getMessage(self.ctx, 111)
                status = True
            else:
                pages = insert = update = 0
                timestamp = parseDateTime()
                parameter = self.datasource.Provider.getRequestParameter('getPeople', user.MetaData)
                parser = DataParser(self.datasource)
                map = self.datasource.getFieldsMap(False)
                pattern = self._getFields()
                enumerator = user.Request.getEnumeration(parameter, parser)
                while self.running and enumerator.hasMoreElements():
                    response = enumerator.nextElement()
                    status = response.IsPresent
                    if status:
                        pages += 1
                        i, u = self._syncResponse(user, map, pattern, response.Value, timestamp)
                        insert += i
                        update += u
                self._closeDataSourceCall()
                format = (pages, insert, update)
                msg = getMessage(self.ctx, 112, format)
                logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        except Exception as e:
            msg = getMessage(self.ctx, 113, (e, traceback.print_exc()))
            logMessage(self.ctx, SEVERE, msg, 'Replicator', '_synchronize()')
        msg = getMessage(self.ctx, 114, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        return status

    def _syncResponse(self, user, map, pattern, data, timestamp):
        insert = update = 0
        if data.hasValue(pattern):
            insert, update = self._mergeResource(user, map, pattern, data, timestamp)
        else:
            for key in data.getKeys():
                d = data.getValue(key)
                m = map.getValue(key).getValue('Type')
                i, u = self._mergeResponse(user, map, pattern, key, d, timestamp, m)
                insert += i
                update += u
        return insert, update

    def _mergeResponse(self, user, map, pattern, key, data, timestamp, method):
        insert = update = 0
        if method == 'Sequence':
            m = map.getValue(key).getValue('Table')
            for d in data:
                i, u = self._mergeResponse(user, map, pattern, key, d, timestamp, m)
                insert += i
                update += u
        elif method == 'Field':
            self._updateField(user, key, data, timestamp)
        elif method == 'Header':
            pass
        elif data.hasValue(pattern):
            insert, update = self._mergeResource(user, map, pattern, data, timestamp)
        return insert, update

    def _mergeData(self, map, index, key, data, timestamp, method):
        if method == 'Sequence':
            m = map.getValue(key).getValue('Table')
            for d in data:
                self._mergeData(map, index, key, d, timestamp, m)
        elif method == 'Tables':
            t = self._getTypes(key, data)
            for k in data.getKeys():
                if k == 'Type':
                    continue
                d = data.getValue(k)
                self._mergeField(key, index, t, k, d, timestamp)
        elif method == 'Field':
            pass

    def _mergeResource(self, user, map, pattern, data, timestamp):
        index, insert, update = self._getPeoples(user, data.getValue(pattern))
        for key in data.getKeys():
            if key == pattern:
                continue
            d = data.getValue(key)
            method = map.getValue(key).getValue('Type')
            self._mergeData(map, index, key, data.getValue(key), timestamp, method)
        return insert, update

    def _mergeField(self, table, index, typ, field, value, timestamp):
        label = self._getLabels(field)
        if label is None:
            return
        call = self._getPreparedCall('update' + table)
        call.setString(1, value)
        call.setTimestamp(2, timestamp)
        call.setLong(3, index)
        call.setLong(4, label)
        if typ is not None:
            call.setLong(5, typ)
        row = call.executeUpdate()
        if row != 1:
            call = self._getPreparedCall('insert' + table)
            call.setString(1, value)
            call.setLong(2, index)
            call.setLong(3, label)
            if typ is not None:
                call.setLong(4, typ)
            row = call.executeUpdate()

    def _updateField(self, user, key, value, timestamp):
        call = self._getDataSourceCall('update' + key)
        call.setString(1, value)
        call.setTimestamp(2, timestamp)
        call.setLong(3, user.People)
        row = call.executeUpdate()
        if row and user.MetaData.hasValue(key):
            oldvalue = user.MetaData.getValue(key)
            user.MetaData.setValue(key, value)

    def _getPeoples(self, user, resource):
        insert = update = 0
        if self._Peoples is None:
            self._Peoples = self._getPeopleIndex()
        if resource not in self._Peoples:
            people = self._insertResource(user, resource)
            if people is not None:
                self._Peoples[resource] = people
                insert = 1
        else:
            people = self._Peoples[resource]
            update = 1
        return people, insert, update

    def _getPeopleIndex(self):
        map = {}
        call = getDataSourceCall(self.datasource.Connection, 'getPeopleIndex')
        result = call.executeQuery()
        while result.next():
            map[result.getString(1)] = result.getLong(2)
        call.close()
        return map

    def _insertResource(self, user, resource):
        people = None
        call = self._getDataSourceCall('insertPeople')
        call.setString(1, resource)
        row = call.executeUpdate()
        if row == 1:
            call = self._getDataSourceCall('getIdentity')
            result = call.executeQuery()
            if result.next():
                people = result.getLong(1)
                call = self._getDataSourceCall('insertConnection')
                call.setLong(1, user.People)
                call.setLong(2, people)
                row = call.executeUpdate()
        return people

    def _getTypes(self, key, data):
        if self._Types is None:
            self._Types = self._getTypeIndex()
        if not data.hasValue('Type'):
            if key in self._Types['Default']:
                return self._Types['Default'][key]
            return None
        value = data.getValue('Type')
        if value in self._Types['Index']:
            return self._Types['Index'][value]
        idx = self._insertType(value)
        if idx is not None:
            self._Types['Index'][value] = idx
        return idx

    def _getTypeIndex(self):
        map = {}
        for method in ('Index','Default'):
            map[method] = {}
            call = getDataSourceCall(self.datasource.Connection, 'getType' + method)
            result = call.executeQuery()
            while result.next():
               map[method][result.getString(1)] = result.getLong(2)
            call.close()
        return map

    def _insertType(self, value):
        identity = None
        call = self._getDataSourceCall('insertTypes')
        call.setString(1, value)
        call.setString(2, value)
        row = call.executeUpdate()
        if row == 1:
            call = self._getDataSourceCall('getIdentity')
            result = call.executeQuery()
            if result.next():
                identity = result.getLong(1)
        return identity

    def _getLabels(self, value):
        if self._Labels is None:
            self._Labels = self._getLabelIndex()
        if value in self._Labels:
            return self._Labels[value]
        return None

    def _getLabelIndex(self):
        map = {}
        call = getDataSourceCall(self.datasource.Connection, 'getLabelIndex')
        result = call.executeQuery()
        while result.next():
            map[result.getString(1)] = result.getLong(2)
        call.close()
        return map

    def _getFields(self):
        if self._Fields is None:
            self._Fields = self._getFieldIndex()
        return self._Fields

    def _getFieldIndex(self):
        primary = ''
        call = getDataSourceCall(self.datasource.Connection, 'getFieldIndex')
        r = call.executeQuery()
        while r.next():
            primary = r.getString(1)
        call.close()
        return primary

    def _closeDataSourceCall(self):
        for call in self._Calls.values():
            call.close()
        self._Calls = {}

    def _getPreparedCall(self, name):
        if name in self._Calls:
            return self._Calls[name]
        # TODO: cannot use: call = self.Connection.prepareCommand(name, QUERY)
        # TODO: it trow a: java.lang.IncompatibleClassChangeError
        query = self.datasource.Connection.getQueries().getByName(name).Command
        call = self.datasource.Connection.prepareCall(query)
        self._Calls[name] = call
        return call

    def _getDataSourceCall(self, name):
        if name in self._Calls:
            return self._Calls[name]
        call = getDataSourceCall(self.datasource.Connection, name)
        self._Calls[name] = call
        return call
