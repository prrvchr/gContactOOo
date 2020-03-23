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
                 Thread):
    def __init__(self, ctx, datasource, event):
        Thread.__init__(self)
        self.ctx = ctx
        self.datasource = datasource
        self.event = event
        self._Peoples = self.datasource.getTableIndex('People')
        index = self.datasource.getTableIndex('Type')
        default = self.datasource.getTableIndex('TypeDefault')
        self._Types = {'Index': index, 'Default': default}
        self._Labels = self.datasource.getTableIndex('Label')
        self.count = 1
        self.start()

    def run(self):
        print("replicator.run()1 count=%s" % self.count)
        while self.count > 0:
            self.event.clear()
            print("replicator.run()2 count=%s" % self.count)
            if not self.event.is_set():
                self._synchronize()
                while not self.event.wait(g_sync):
                    self._synchronize()
            self.count -= 1
        print("replicator.run()3 count=%s - query=%s" % (self.count, self.datasource.count))
        #self.datasource.shutdownDataBase(False)
        #self.datasource._Statement = None
        #self.datasource.Connection.close()
        #print("replicator.run()4 count=%s" % self.count)

    def _synchronize(self):
        timestamp = getDateTime(False)
        for user in self.datasource._UsersPool.values():
            if not self.event.is_set():
                self._syncUser(user, timestamp)
        self.datasource.closeDataSourceCall()

    def _syncUser(self, user, timestamp):
        msg = getMessage(self.ctx, 110, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        try:
            if user.Request.isOffLine(self.datasource.Provider.Host):
                msg = getMessage(self.ctx, 111)
            elif not self.event.is_set():
                self._syncPeople(user, timestamp)
                if not self.event.is_set():
                    self._syncGroup(user, timestamp)
                    if not self.event.is_set():
                       self._syncConnection(user, timestamp)
        except Exception as e:
            msg = getMessage(self.ctx, 115, (e, traceback.print_exc()))
            logMessage(self.ctx, SEVERE, msg, 'Replicator', '_synchronize()')
        msg = getMessage(self.ctx, 116, user.Account)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')

    def _syncPeople(self, user, timestamp):
        method = {'Name': 'People',
                  'PrimaryKey': 'Resource',
                  'ResourceFilter': (),
                  'Deleted': (('metadata','deleted'), True),
                  'Filter': (('metadata', 'primary'), True),
                  'Skip': ('Type', 'metadata')}
        pages = inserted = updated = deleted = 0
        parameter = self.datasource.Provider.getRequestParameter(method['Name'], user)
        parser = DataParser(self.datasource, method['Name'])
        map = self.datasource.getFieldsMap(method['Name'], False)
        enumerator = user.Request.getEnumeration(parameter, parser)
        while not self.event.is_set() and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                i, u, d = self._syncResponse(method, user, map, response.Value, timestamp)
                inserted += i
                updated += u
                deleted += d
        format = (pages, inserted, updated, deleted)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncPeople()')
        self.datasource.count += inserted + updated + deleted
        print("replicator._syncPeople() 1 %s" % method['PrimaryKey'])

    def _syncGroup(self, user, timestamp):
        method = {'Name': 'Group',
                  'PrimaryKey': 'Resource',
                  'ResourceFilter': (('groupType', ), g_filter),
                  'Deleted': (('metadata','deleted'), True)}
        pages = inserted = updated = deleted = 0
        parameter = self.datasource.Provider.getRequestParameter(method['Name'], user)
        parser = DataParser(self.datasource, method['Name'])
        map = self.datasource.getFieldsMap(method['Name'], False)
        enumerator = user.Request.getEnumeration(parameter, parser)
        while not self.event.is_set() and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                i, u, d = self._syncResponse(method, user, map, response.Value, timestamp)
                inserted += i
                updated += u
                deleted += d
        format = (pages, inserted, updated, deleted)
        msg = getMessage(self.ctx, 113, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncGroup()')
        self.datasource.count += inserted + updated + deleted

    def _syncConnection(self, user, timestamp):
        pages = i = u = d = 0
        groups = self.datasource.getUpdatedGroups(user, 'contactGroups/')
        if len(groups) > 0:
            print("replicator._syncConnection(): %s" % ','.join(groups))
            method = {'Name': 'Connection',
                      'PrimaryKey': 'Group',
                      'ResourceFilter': ()}
            data = KeyMap(**{'Resources': groups})
            parameter = self.datasource.Provider.getRequestParameter(method['Name'], data)
            parser = DataParser(self.datasource, method['Name'])
            map = self.datasource.getFieldsMap(method['Name'], False)
            request = user.Request.getRequest(parameter, parser)
            response = request.execute()
            if response.IsPresent:
                pages += 1
                i, u, d = self._syncResponse(method, user, map, response.Value, timestamp)
        else:
            print("replicator._syncConnection(): nothing to sync")
        format = (pages, len(groups), i)
        msg = getMessage(self.ctx, 114, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncConnection()')
        self.datasource.count += i

    def _syncResponse(self, method, user, map, data, timestamp):
        inserted = updated = deleted = 0
        for key in data.getKeys():
            field = map.getValue(key).getValue('Type')
            i, u, d = self._mergeResponse(method, user, map, key, data.getValue(key), timestamp, field)
            inserted += i
            updated += u
            deleted += d
        return inserted, updated, deleted

    def _mergeResponse(self, method, user, map, key, data, timestamp, field):
        inserted = updated = deleted = 0
        if field == 'Sequence':
            f = map.getValue(key).getValue('Table')
            for d in data:
                i, u , d = self._mergeResponse(method, user, map, key, d, timestamp, f)
                inserted += i
                updated += u
                deleted += d
        elif field == 'Field':
            self.datasource.updateSyncToken(user, key, data, timestamp)
        elif field == 'Header':
            pass
        elif data.hasValue(method['PrimaryKey']):
            if self._filterResource(data, *method['ResourceFilter']):
                func = getattr(self, '_merge%s' % method['Name'])
                inserted, updated, deleted = func(method, user, map, data, timestamp)
        return inserted, updated, deleted

    def _filterResource(self, data, filters=(), value=None, index=0):
        if index < len(filters):
            filter = filters[index]
            if data.hasValue(filter):
                d = data.getValue(filter)
                return self._filterResource(d, filters, value, index + 1)
            return False
        return True if value is None else data == value

    def _mergeGroup(self, method, user, map, data, timestamp):
        inserted = updated = deleted = 0
        pkey = method['PrimaryKey']
        resource = data.getValue(pkey)
        if self._filterResource(data, *method['Deleted']):
            deleted = self.datasource.deleteGroup(user, resource)
        else:
            name = data.getDefaultValue('Name', None)
            #timestamp = data.getValue('metadata').getValue('updateTime')
            inserted, updated = self.datasource.mergeGroup(user, name, resource, timestamp)
        return inserted, updated, deleted

    def _mergePeople(self, method, user, map, data, timestamp):
        inserted = updated = deleted = 0
        pkey = method['PrimaryKey']
        resource = data.getValue(pkey)
        if self._filterResource(data, *method['Deleted']):
            deleted = self.datasource.deletePeople(resource)
        else:
            index, inserted, updated = self._getPeoples(user, resource, timestamp)
            for key in data.getKeys():
                if key == pkey:
                    continue
                d = data.getValue(key)
                f = map.getValue(key).getValue('Type')
                self._mergePeopleData(method, map, index, key, data.getValue(key), timestamp, f)
        return inserted, updated, deleted

    def _mergeConnection(self, method, user, map, data, timestamp):
        inserted = self.datasource.mergeConnection(user, data.getValue('Group'), timestamp)
        return inserted, 0, 0

    def _mergePeopleData(self, method, map, index, key, data, timestamp, field):
        if field == 'Sequence':
            f = map.getValue(key).getValue('Table')
            for d in data:
                self._mergePeopleData(method, map, index, key, d, timestamp, f)
        elif field == 'Tables':
            if self._filterResource(data, *method['Filter']):
                t = self._getTypes(key, data)
                for k in data.getKeys():
                    if k in method['Skip']:
                        continue
                    self._mergePeopleField(key, index, t, k, data.getValue(k), timestamp)

    def _mergePeopleField(self, table, index, typ, field, value, timestamp):
        label = self._getLabels(field)
        if label is not None:
            self.datasource.mergePeople(table, index, typ, label, field, value, timestamp)

    def _getPeoples(self, user, resource, timestamp):
        inserted = updated = 0
        if resource not in self._Peoples:
            people = self.datasource.insertPeople(user, resource, timestamp)
            if people is not None:
                self._Peoples[resource] = people
                inserted = 1
        else:
            people = self._Peoples[resource]
            updated = 1
        return people, inserted, updated

    def _getTypes(self, key, data):
        if not data.hasValue('Type'):
            if key in self._Types['Default']:
                return self._Types['Default'][key]
            return None
        value = data.getValue('Type')
        if value in self._Types['Index']:
            return self._Types['Index'][value]
        idx = self.datasource.insertType(value)
        if idx is not None:
            self._Types['Index'][value] = idx
        return idx

    def _getLabels(self, value):
        return self._Labels.get(value, None)
