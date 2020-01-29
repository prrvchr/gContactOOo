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
        self._PrimaryField = None
        self._PeopleIndex = None
        self._Types = None
        self._LabelIndex = None
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
        try:
            print("Replicator._synchronize() 1")
            if user.Request.isOffLine(self.datasource.Provider.Host):
                print("Replicator._synchronize() 2 OffLine")
                return True
            status = False
            timestamp = parseDateTime()
            parameter = self.datasource.Provider.getRequestParameter('getPeople', user.MetaData)
            parser = DataParser(self.datasource)
            map = self.datasource.getFieldsMap(False)
            pattern = self.getPrimaryField()
            enumerator = user.Request.getEnumeration(parameter, parser)
            while self.running and enumerator.hasMoreElements():
                response = enumerator.nextElement()
                status = response.IsPresent
                if status:
                    self._syncResponse(user, map, pattern, response.Value, timestamp)
            self._closeDataSourceCall()
            print("Replicator._synchronize() 3")
            return status
        except Exception as e:
            print("Replicator._synchronize() ERROR: %s - %s" % (e, traceback.print_exc()))

    def _syncResponse(self, user, map, pattern, data, timestamp):
        if data.hasValue(pattern):
            self._mergeResource(user, map, pattern, data, timestamp)
        else:
            for key in data.getKeys():
                d = data.getValue(key)
                m = map.getValue(key).getValue('Type')
                self._mergeResponse(user, map, pattern, key, d, timestamp, m)

    def _mergeResponse(self, user, map, pattern, key, data, timestamp, method):
        print("DataSource._mergeResponse: %s" % (method, ))
        if method == 'Sequence':
            m = map.getValue(key).getValue('Table')
            for d in data:
                self._mergeResponse(user, map, pattern, key, d, timestamp, m)
        elif method == 'Field':
            self._updateField(user, key, data, timestamp)
        elif method == 'Header':
            pass
        elif data.hasValue(pattern):
            self._mergeResource(user, map, pattern, data, timestamp)

    def _mergeData(self, map, index, key, data, timestamp, method):
        if method == 'Sequence':
            m = map.getValue(key).getValue('Table')
            for d in data:
                self._mergeData(map, index, key, d, timestamp, m)
        elif method == 'Tables':
            t = self.getTypeIndex(key, data)
            for k in data.getKeys():
                if k == 'Type':
                    continue
                d = data.getValue(k)
                print("DataSource._mergeData: 1 %s - %s - %s - %s" % (key, t, k, d))
                self._mergeField(key, index, t, k, d, timestamp)
        elif method == 'Field':
            print("DataSource._mergeData: 2 %s - %s" % (key, data))

    def _mergeResource(self, user, map, pattern, data, timestamp):
        index = self.getPeopleIndex(user, data.getValue(pattern))
        for key in data.getKeys():
            if key == pattern:
                continue
            d = data.getValue(key)
            method = map.getValue(key).getValue('Type')
            self._mergeData(map, index, key, data.getValue(key), timestamp, method)
        print("DataSource._mergeResource: %s" % (data.getValue(pattern), ))

    def _mergeField(self, table, index, typ, field, value, timestamp):
        label = self.getLabelIndex(field)
        print("DataSource._mergeField: 1: %s - %s - %s - %s" % (value, index, label, typ))
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
            print("DataSource._mergeField: 2: %s - %s - %s" % (value, field, label))

    def _updateField(self, user, key, value, timestamp):
        print("DataSource._updateField: %s - %s" % (key, value))
        call = self._getDataSourceCall('update' + key)
        call.setString(1, value)
        call.setTimestamp(2, timestamp)
        call.setLong(3, user.People)
        row = call.executeUpdate()
        if row and user.MetaData.hasValue(key):
            oldvalue = user.MetaData.getValue(key)
            user.MetaData.setValue(key, value)
            print("DataSource._updateField: %s - %s" % (oldvalue, user.MetaData.getValue(key)))

    def getPeopleIndex(self, user, resource):
        if self._PeopleIndex is None:
            self._PeopleIndex = self._getPeopleIndex()
        if resource not in self._PeopleIndex:
            people = self._insertResource(user, resource)
            if people is not None:
                self._PeopleIndex[resource] = people
        else:
            people = self._PeopleIndex[resource]
        return people

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

    def getTypeIndex(self, key, data):
        if self._Types is None:
            self._Types = self._getTypes()
        if not data.hasValue('Type'):
            if key in self._Types['Default']:
                print("DataSource.getTypeIndex() %s - %s **********************" % (key, self._Types['Default'][key]))
                return self._Types['Default'][key]
            return None
        value = data.getValue('Type')
        if value in self._Types['Index']:
            return self._Types['Index'][value]
        print("DataSource.getTypeIndex() %s ******************************" % value)
        idx = self._insertType(value)
        if idx is not None:
            self._Types['Index'][value] = idx
        print("DataSource.getTypeIndex() %s ******************************" % idx)
        return idx

    def _getTypes(self):
        map = {}
        for method in ('Index','Default'):
            map[method] = {}
            call = getDataSourceCall(self.datasource.Connection, 'getTypes' + method)
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

    def getLabelIndex(self, value):
        if self._LabelIndex is None:
            self._LabelIndex = self._getLabelIndex()
        if value in self._LabelIndex:
            return self._LabelIndex[value]
        print("DataSource.getLabelIndex() %s ******************************" % value)
        return None

    def _getLabelIndex(self):
        map = {}
        call = getDataSourceCall(self.datasource.Connection, 'getLabelIndex')
        result = call.executeQuery()
        while result.next():
            map[result.getString(1)] = result.getLong(2)
        call.close()
        return map

    def getPrimaryField(self):
        if self._PrimaryField is None:
            self._PrimaryField = self._getPrimaryField()
        return self._PrimaryField

    def _getPrimaryField(self):
        primary = ''
        call = getDataSourceCall(self.datasource.Connection, 'getPrimaryField')
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
