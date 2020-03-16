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

from .configuration import g_sync
from .dataparser import DataParser
from .dbtools import getDataSourceCall
from .dbqueries import getSqlQuery
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
        self._Fields = {}
        self._Peoples = None
        self._Types = None
        self._Labels = None
        self._Groups = {}
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
                self.lock.wait(g_sync)
            if self.running:
                self._synchronize()

    def _synchronize(self):
        for user in self.datasource._UsersPool.values():
            if self.running:
                self._syncUser(user)
        self._closeDataSourceCall()

    def _syncUser(self, user):
        msg = getMessage(self.ctx, 110, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        try:
            if user.Request.isOffLine(self.datasource.Provider.Host):
                msg = getMessage(self.ctx, 111)
            else:
                timestamp = parseDateTime()
                self._syncPeople(user, timestamp)
                self._syncGroup(user, timestamp)
                self._syncConnection(user, timestamp)
        except Exception as e:
            msg = getMessage(self.ctx, 113, (e, traceback.print_exc()))
            logMessage(self.ctx, SEVERE, msg, 'Replicator', '_synchronize()')
        msg = getMessage(self.ctx, 114, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')

    def _syncPeople(self, user, timestamp):
        method = 'People'
        pages = insert = update = 0
        parameter = self.datasource.Provider.getRequestParameter(method, user.MetaData)
        parser = DataParser(self.datasource, method)
        map = self.datasource.getFieldsMap(method, False)
        #pkey = self._getFields(method)
        pkey = 'Resource'
        enumerator = user.Request.getEnumeration(parameter, parser)
        while self.running and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                i, u = self._syncResponse(method, user, map, pkey, response.Value, timestamp)
                insert += i
                update += u
        format = (pages, insert, update)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncPeople()')
        print("replicator._syncPeople() 1 %s" % pkey)

    def _syncGroup(self, user, timestamp):
        method = 'Group'
        pages = insert = update = 0
        parameter = self.datasource.Provider.getRequestParameter(method, user.MetaData)
        parser = DataParser(self.datasource, method)
        map = self.datasource.getFieldsMap(method, False)
        #pkey = self._getFields(method)
        pkey = 'Resource'
        enumerator = user.Request.getEnumeration(parameter, parser)
        while self.running and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                i, u = self._syncResponse(method, user, map, pkey, response.Value, timestamp)
                insert += i
                update += u
        format = (pages, insert, update)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncGroup()')

    def _syncConnection(self, user, timestamp):
        groups = self.datasource.getUpdatedGroups(user, timestamp, 'contactGroups/')
        if len(groups) == 0:
            return
        print("replicator._syncMember(): %s" % ','.join(groups))
        method = 'Connection'
        pages = insert = update = 0
        data = KeyMap(**{'Resources': groups})
        parameter = self.datasource.Provider.getRequestParameter(method, data)
        parser = DataParser(self.datasource, method)
        map = self.datasource.getFieldsMap(method, False)
        pkey = 'Group'
        request = user.Request.getRequest(parameter, parser)
        response = request.execute()
        if response.IsPresent:
            pages += 1
            i, u = self._syncResponse(method, user, map, pkey, response.Value, timestamp)
        format = (pages, insert, update)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncMember()')

    def _syncResponse(self, method, user, map, pkey, data, timestamp):
        insert = update = 0
        for key in data.getKeys():
            d = data.getValue(key)
            m = map.getValue(key).getValue('Type')
            i, u = self._mergeResponse(method, user, map, pkey, key, d, timestamp, m)
            insert += i
            update += u
        return insert, update

    def _mergeResponse(self, method, user, map, pkey, key, data, timestamp, field):
        insert = update = 0
        if field == 'Sequence':
            m = map.getValue(key).getValue('Table')
            for d in data:
                i, u = self._mergeResponse(method, user, map, pkey, key, d, timestamp, m)
                insert += i
                update += u
        elif field == 'Field':
            self._updateField(user, key, data, timestamp)
        elif field == 'Header':
            pass
        elif data.hasValue(pkey):
            insert, update = self._mergeResource(method, user, map, pkey, data, timestamp)
        return insert, update

    def _mergeData(self, method, map, index, key, data, timestamp, field):
        if field == 'Sequence':
            f = map.getValue(key).getValue('Table')
            for d in data:
                self._mergeData(method, map, index, key, d, timestamp, f)
        elif field == 'Tables':
            t = self._getTypes(key, data)
            for k in data.getKeys():
                if k == 'Type':
                    continue
                d = data.getValue(k)
                self._mergeField(method, key, index, t, k, d, timestamp)
        elif field == 'Field':
            pass

    def _mergeResource(self, method, user, map, pkey, data, timestamp):
        insert = update = 0
        if method == 'People':
            insert, update = self._mergePeople(method, user, map, pkey, data, timestamp)
        elif method == 'Group':
            name = data.getValue('Name')
            resource = data.getValue('Resource')
            insert, update = self._mergeGroup(user, name, resource, timestamp)
        elif method == 'Connection':
            insert, update = self._mergeConnection(user, data.getValue('Group'), timestamp)
        return insert, update

    def _mergePeople(self, method, user, map, pkey, data, timestamp):
        index, insert, update = self._getPeoples(user, data.getValue(pkey))
        for key in data.getKeys():
            if key == pkey:
                continue
            d = data.getValue(key)
            f = map.getValue(key).getValue('Type')
            self._mergeData(method, map, index, key, data.getValue(key), timestamp, f)
        return insert, update

    def _mergeGroup(self, user, name, resource, timestamp):
        i = u = 0
        call = self._getDataSourceCall('mergeGroup')
        call.setString(1, 'contactGroups/')
        call.setLong(2, user.People)
        call.setString(3, resource)
        call.setString(4, name)
        call.setTimestamp(5, timestamp)
        i = call.execute()
        group = call.getLong(6)
        schema = user.Resource
        view = name.title()
        statement = call.getConnection().createStatement()
        query = getSqlQuery('dropGroupView',(schema, view))
        statement.executeQuery(query)
        query = getSqlQuery('createGroupView',(schema, view, group))
        print("replicator._mergeGroup() %s\n%s" % (view, query))
        statement.executeQuery(query)
        return i, u

    def _mergeConnection(self, user, data, timestamp):
        i = u = 0
        separator = ','
        call = self._getDataSourceCall('mergeConnection')
        call.setString(1, 'contactGroups/')
        call.setString(2, 'people/')
        call.setString(3, data.getValue('Resource'))
        call.setTimestamp(4, timestamp)
        call.setString(5, separator)
        members = data.getDefaultValue('Connections', ())
        call.setString(6, separator.join(members))
        row = call.execute()
        print("replicator._mergeConnection() %s - %s" % (data.getValue('Resource'), len(members)))
        return i, u

    def _mergeField(self, method, table, index, typ, field, value, timestamp):
        if method == 'People':
            self._mergePeopleField(table, index, typ, field, value, timestamp)
        elif method == 'Group':
            self._mergeGroupField(table, index, typ, field, value, timestamp)
        elif method == 'Connection':
            print("replicator._mergeField() *******************************")

    def _mergePeopleField(self, table, index, typ, field, value, timestamp):
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
        #print("replicator._mergePeopleField() %s - %s - %s - %s - %s" % (table, index, typ, field, value))

    def _mergeGroupField(self, table, index, typ, field, value, timestamp):
        print("replicator._mergeGroupField() %s - %s - %s - %s - %s" % (table, index, typ, field, value))

    def _updateField(self, user, key, value, timestamp):
        call = self._getDataSourceCall('update' + key)
        call.setString(1, value)
        call.setTimestamp(2, timestamp)
        call.setLong(3, user.People)
        row = call.executeUpdate()
        if row and user.MetaData.hasValue(key):
            oldvalue = user.MetaData.getValue(key)
            user.MetaData.setValue(key, value)
        print("replicator._updateField() %s - %s" % (key, value))

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
            people = self.datasource.getIdentity()
            #call = self._getDataSourceCall('insertConnection')
            #call.setLong(1, user.People)
            #call.setLong(2, people)
            #row = call.executeUpdate()
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
        for m in ('Index','Default'):
            map[m] = {}
            call = getDataSourceCall(self.datasource.Connection, 'getType' + m)
            result = call.executeQuery()
            while result.next():
               map[m][result.getString(1)] = result.getLong(2)
            call.close()
        return map

    def _insertType(self, value):
        identity = None
        call = self._getDataSourceCall('insertTypes')
        call.setString(1, value)
        call.setString(2, value)
        row = call.executeUpdate()
        if row == 1:
            identity = self.datasource.getIdentity()
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

    def _getFields(self, method):
        if method not in self._Fields:
            self._Fields[method] = self._getFieldIndex(method)
        return self._Fields[method]

    def _getFieldIndex(self, method):
        primary = ''
        call = getDataSourceCall(self.datasource.Connection, 'getFieldIndex')
        call.setString(1, method)
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
