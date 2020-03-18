#!
# -*- coding: utf_8 -*-

#from __futur__ import absolute_import

import uno
import unohelper

from com.sun.star.util import XCancellable
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from unolib import KeyMap
from unolib import getDateTime

from .configuration import g_sync
from .dataparser import DataParser
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
        self.datasource.closeDataSourceCall()

    def _syncUser(self, user):
        msg = getMessage(self.ctx, 110, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        try:
            if user.Request.isOffLine(self.datasource.Provider.Host):
                msg = getMessage(self.ctx, 111)
            else:
                timestamp = getDateTime(True)
                self._syncPeople(user, timestamp)
                self._syncGroup(user, timestamp)
                self._syncConnection(user, timestamp)
                #parser = DataParser(self.datasource, 'People')
        except Exception as e:
            msg = getMessage(self.ctx, 113, (e, traceback.print_exc()))
            logMessage(self.ctx, SEVERE, msg, 'Replicator', '_synchronize()')
        msg = getMessage(self.ctx, 114, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')

    def _syncPeople(self, user, timestamp):
        rules = {'Method': 'People',
                 'PrimaryKey': 'Resource',
                 'Filters': ('metadata', 'primary'),
                 'Skips': ('Type', 'metadata')}
        pages = insert = update = 0
        parameter = self.datasource.Provider.getRequestParameter(rules['Method'], user)
        parser = DataParser(self.datasource, rules['Method'])
        map = self.datasource.getFieldsMap(rules['Method'], False)
        enumerator = user.Request.getEnumeration(parameter, parser)
        while self.running and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                i, u = self._syncResponse(rules, user, map, response.Value, timestamp)
                insert += i
                update += u
        format = (pages, insert, update)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncPeople()')
        print("replicator._syncPeople() 1 %s" % rules['PrimaryKey'])

    def _syncGroup(self, user, timestamp):
        rules = {'Method': 'Group',
                 'PrimaryKey': 'Resource',
                 'Filters': (),
                 'Skips': ()}
        pages = insert = update = 0
        parameter = self.datasource.Provider.getRequestParameter(rules['Method'], user)
        parser = DataParser(self.datasource, rules['Method'])
        map = self.datasource.getFieldsMap(rules['Method'], False)
        #pkey = self._getFields(method)
        enumerator = user.Request.getEnumeration(parameter, parser)
        while self.running and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                i, u = self._syncResponse(rules, user, map, response.Value, timestamp)
                insert += i
                update += u
        format = (pages, insert, update)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncGroup()')

    def _syncConnection(self, user, timestamp):
        groups = self.datasource.getUpdatedGroups(user, 'contactGroups/')
        if len(groups) == 0:
            print("replicator._syncConnection(): nothing to sync")
            return
        print("replicator._syncConnection(): %s" % ','.join(groups))
        rules = {'Method': 'Connection',
                 'PrimaryKey': 'Group',
                 'Filters': (),
                 'Skips': ()}
        pages = insert = update = 0
        data = KeyMap(**{'Resources': groups})
        parameter = self.datasource.Provider.getRequestParameter(rules['Method'], data)
        parser = DataParser(self.datasource, rules['Method'])
        map = self.datasource.getFieldsMap(rules['Method'], False)
        request = user.Request.getRequest(parameter, parser)
        response = request.execute()
        if response.IsPresent:
            pages += 1
            i, u = self._syncResponse(rules, user, map, response.Value, timestamp)
        format = (pages, insert, update)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncMember()')

    def _syncResponse(self, rules, user, map, data, timestamp):
        insert = update = 0
        for key in data.getKeys():
            field = map.getValue(key).getValue('Type')
            i, u = self._mergeResponse(rules, user, map, key, data.getValue(key), timestamp, field)
            insert += i
            update += u
        return insert, update

    def _mergeResponse(self, rules, user, map, key, data, timestamp, field):
        insert = update = 0
        if field == 'Sequence':
            f = map.getValue(key).getValue('Table')
            for d in data:
                i, u = self._mergeResponse(rules, user, map, key, d, timestamp, f)
                insert += i
                update += u
        elif field == 'Field':
            self.datasource.updateSyncToken(user, key, data, timestamp)
        elif field == 'Header':
            pass
        elif data.hasValue(rules['PrimaryKey']):
            insert, update = self._mergeResource(rules, user, map, data, timestamp)
        return insert, update

    def _filterResource(self, data, filters, index=0):
        if index < len(filters):
            filter = filters[index]
            if data.hasValue(filter):
                d = data.getValue(filter)
                return self._filterResource(d, filters, index + 1)
            return False
        return data

    def _mergeResource(self, rules, user, map, data, timestamp):
        insert = update = 0
        method = rules['Method']
        if method == 'People':
            insert, update = self._mergePeople(rules, user, map, data, timestamp)
        elif method == 'Group':
            resource = data.getValue('Resource')
            name = data.getDefaultValue('Name', None)
            if name is None:
                insert, update = self._deleteGroup(user, resource)
            else:
                #timestamp = data.getValue('metadata').getValue('updateTime')
                insert, update = self._mergeGroup(user, name, resource, timestamp)
        elif method == 'Connection':
            insert, update = self._mergeConnection(user, data.getValue('Group'), timestamp)
        return insert, update

    def _mergePeople(self, rules, user, map, data, timestamp):
        pkey = rules['PrimaryKey']
        index, insert, update = self._getPeoples(user, data.getValue(pkey))
        for key in data.getKeys():
            if key == pkey:
                continue
            d = data.getValue(key)
            f = map.getValue(key).getValue('Type')
            #print("replicator._mergePeople() %s - %s - %s" % (map, key, f))
            self._mergePeopleData(rules, map, index, key, data.getValue(key), timestamp, f)
        return insert, update

    def _mergePeopleData(self, rules, map, index, key, data, timestamp, field):
        if field == 'Sequence':
            f = map.getValue(key).getValue('Table')
            for d in data:
                self._mergePeopleData(rules, map, index, key, d, timestamp, f)
        elif field == 'Tables':
            if self._filterResource(data, rules['Filters']):
                t = self._getTypes(key, data)
                for k in data.getKeys():
                    if k in rules['Skips']:
                        continue
                    self._mergePeopleField(key, index, t, k, data.getValue(k), timestamp)

    def _deleteGroup(self, user, resource):
        call = self.datasource.getDataSourceCall('deleteGroup')
        call.setString(1, 'contactGroups/')
        call.setLong(2, user.People)
        call.setString(3, resource)
        i = call.execute()
        name = call.getString(4)
        self.datasource.dropGroupView(user, call.getString(4))
        return 0, i

    def _mergeGroup(self, user, name, resource, timestamp):
        call = self.datasource.getDataSourceCall('mergeGroup')
        call.setString(1, 'contactGroups/')
        call.setLong(2, user.People)
        call.setString(3, resource)
        call.setString(4, name)
        call.setTimestamp(5, timestamp)
        i = call.execute()
        self.datasource.createGroupView(user, name, call.getLong(6))
        return i, 0

    def _mergeConnection(self, user, data, timestamp):
        i = u = 0
        separator = ','
        call = self.datasource.getDataSourceCall('mergeConnection')
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

    def _mergePeopleField(self, table, index, typ, field, value, timestamp):
        label = self._getLabels(field)
        if label is None:
            return
        call = self.datasource.getPreparedCall('update%s' % table)
        call.setString(1, value)
        call.setTimestamp(2, timestamp)
        call.setLong(3, index)
        call.setLong(4, label)
        if typ is not None:
            call.setLong(5, typ)
        row = call.executeUpdate()
        if row != 1:
            call = self.datasource.getPreparedCall('insert%s' % table)
            call.setString(1, value)
            call.setLong(2, index)
            call.setLong(3, label)
            if typ is not None:
                call.setLong(4, typ)
            row = call.executeUpdate()
        #print("replicator._mergePeopleField() %s - %s - %s - %s - %s" % (table, index, typ, field, value))

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
        call = self.datasource.getDataSourceCall('getPeopleIndex')
        result = call.executeQuery()
        while result.next():
            map[result.getString(1)] = result.getLong(2)
        return map

    def _insertResource(self, user, resource):
        people = None
        call = self.datasource.getDataSourceCall('insertPeople')
        call.setString(1, resource)
        row = call.executeUpdate()
        if row == 1:
            people = self.datasource.getIdentity()
            #call = self.datasource.getDataSourceCall('insertConnection')
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
            call = self.datasource.getDataSourceCall('getType%s' % m)
            result = call.executeQuery()
            while result.next():
               map[m][result.getString(1)] = result.getLong(2)
        return map

    def _insertType(self, value):
        identity = None
        call = self.datasource.getDataSourceCall('insertTypes')
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
        call = self.datasource.getDataSourceCall('getLabelIndex')
        result = call.executeQuery()
        while result.next():
            map[result.getString(1)] = result.getLong(2)
        return map

    def _getFields(self, method):
        if method not in self._Fields:
            self._Fields[method] = self._getFieldIndex(method)
        return self._Fields[method]

    def _getFieldIndex(self, method):
        primary = ''
        call = self.datasource.getDataSourceCall('getFieldIndex')
        call.setString(1, method)
        r = call.executeQuery()
        while r.next():
            primary = r.getString(1)
        return primary
