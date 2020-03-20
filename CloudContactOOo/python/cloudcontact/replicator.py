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
from .configuration import g_filter
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
        self._Peoples = None
        self._Types = None
        self._Labels = None
        self.start()

    @property
    def Peoples(self):
        if self._Peoples is None:
            self._Peoples = self.datasource.getTableIndex('People')
        return self._Peoples
    @property
    def Types(self):
        if self._Types is None:
            index = self.datasource.getTableIndex('Type')
            default = self.datasource.getTableIndex('TypeDefault')
            self._Types = {'Index': index, 'Default': default}
        return self._Types
    @property
    def Labels(self):
        if self._Labels is None:
            self._Labels = self.datasource.getTableIndex('Label')
        return self._Labels

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
        except Exception as e:
            msg = getMessage(self.ctx, 115, (e, traceback.print_exc()))
            logMessage(self.ctx, SEVERE, msg, 'Replicator', '_synchronize()')
        msg = getMessage(self.ctx, 116, user.Account)
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
                 'Filters': ('groupType', ),
                 'Skips': ()}
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
        msg = getMessage(self.ctx, 113, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncGroup()')

    def _syncConnection(self, user, timestamp):
        pages = insert = update = 0
        groups = self.datasource.getUpdatedGroups(user, 'contactGroups/')
        if len(groups) > 0:
            print("replicator._syncConnection(): %s" % ','.join(groups))
            rules = {'Method': 'Connection',
                     'PrimaryKey': 'Group',
                     'Filters': (),
                     'Skips': ()}
            data = KeyMap(**{'Resources': groups})
            parameter = self.datasource.Provider.getRequestParameter(rules['Method'], data)
            parser = DataParser(self.datasource, rules['Method'])
            map = self.datasource.getFieldsMap(rules['Method'], False)
            request = user.Request.getRequest(parameter, parser)
            response = request.execute()
            if response.IsPresent:
                pages += 1
                insert, update = self._syncResponse(rules, user, map, response.Value, timestamp)
        else:
            print("replicator._syncConnection(): nothing to sync")
        format = (pages, insert, update)
        msg = getMessage(self.ctx, 114, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncConnection()')

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

    def _filterResource(self, data, filters, value=None, index=0):
        if index < len(filters):
            filter = filters[index]
            if data.hasValue(filter):
                d = data.getValue(filter)
                return self._filterResource(d, filters, value, index + 1)
            return False
        return data if value is None else data == value

    def _mergeResource(self, rules, user, map, data, timestamp):
        insert = update = 0
        method = rules['Method']
        if method == 'People':
            insert, update = self._mergePeople(rules, user, map, data, timestamp)
        elif method == 'Group':
            if self._filterResource(data, rules['Filters'], g_filter):
                insert, update = self._mergeGroup(rules, user, map, data, timestamp)
        elif method == 'Connection':
            insert, update = self._mergeConnection(rules, user, map, data, timestamp)
        return insert, update

    def _mergeGroup(self, rules, user, map, data, timestamp):
        insert = update = 0
        resource = data.getValue('Resource')
        if self._filterResource(data, ('metadata','deleted'), True):
            insert, update = self.datasource.deleteGroup(user, resource)
        else:
            name = data.getDefaultValue('Name', None)
            #timestamp = data.getValue('metadata').getValue('updateTime')
            insert, update = self.datasource.mergeGroup(user, name, resource, timestamp)
        return insert, update

    def _mergePeople(self, rules, user, map, data, timestamp):
        pkey = rules['PrimaryKey']
        index, insert, update = self._getPeoples(user, data.getValue(pkey), timestamp)
        for key in data.getKeys():
            if key == pkey:
                continue
            d = data.getValue(key)
            f = map.getValue(key).getValue('Type')
            #print("replicator._mergePeople() %s - %s - %s" % (map, key, f))
            self._mergePeopleData(rules, map, index, key, data.getValue(key), timestamp, f)
        return insert, update

    def _mergeConnection(self, rules, user, map, data, timestamp):
        return self.datasource.mergeConnection(user, data.getValue('Group'), timestamp)

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

    def _mergePeopleField(self, table, index, typ, field, value, timestamp):
        label = self._getLabels(field)
        if label is not None:
            self.datasource.mergePeople(table, index, typ, label, field, value, timestamp)

    def _getPeoples(self, user, resource, timestamp):
        insert = update = 0
        if resource not in self.Peoples:
            people = self.datasource.insertPeople(user, resource, timestamp)
            if people is not None:
                self.Peoples[resource] = people
                insert = 1
        else:
            people = self.Peoples[resource]
            update = 1
        return people, insert, update

    def _getTypes(self, key, data):
        if not data.hasValue('Type'):
            if key in self.Types['Default']:
                return self.Types['Default'][key]
            return None
        value = data.getValue('Type')
        if value in self.Types['Index']:
            return self.Types['Index'][value]
        idx = self.datasource.insertType(value)
        if idx is not None:
            self.Types['Index'][value] = idx
        return idx

    def _getLabels(self, value):
        return self.Labels.get(value, None)
