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

from .database import DataBase
from .dataparser import DataParser

from .configuration import g_sync
from .configuration import g_filter

from .logger import logMessage
from .logger import getMessage

from threading import Thread
import traceback


class Replicator(unohelper.Base,
                 Thread):
    def __init__(self, ctx, datasource, provider, users, sync):
        Thread.__init__(self)
        self.ctx = ctx
        self.DataBase = DataBase(self.ctx, datasource)
        self.Provider = provider
        self.Users = users
        self.canceled = False
        self.fullPull = False
        self.sync = sync
        sync.clear()
        self.error = None
        self.count = 0
        self.start()

    # XRestReplicator
    def cancel(self):
        self.canceled = True
        self.sync.set()
        self.join()

    def run(self):
        print("replicator.run()1")
        try:
            while not self.canceled:
                self.sync.wait(g_sync)
                print("replicator.run()2")
                self._synchronize()
                self.sync.clear()
            print("replicator.run()3 query=%s" % self.count)
        except Exception as e:
            msg = "Replicator run(): Error: %s - %s" % (e, traceback.print_exc())
            print(msg)

    def _synchronize(self):
        timestamp = getDateTime(False)
        if self.Provider.isOffLine():
            msg = getMessage(self.ctx, 111)
            logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        elif not self.canceled:
            self._syncData(timestamp)

    def _syncData(self, timestamp):
        result = KeyMap()
        self.DataBase.setLoggingChanges(False)
        self.DataBase.saveChanges()
        self.DataBase.Connection.setAutoCommit(False)
        for user in self.Users.values():
            if not self.canceled:
                msg = getMessage(self.ctx, 110, user.Account)
                logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
                result.setValue(user.Account, self._syncUser(user, timestamp))
                msg = getMessage(self.ctx, 116, user.Account)
                logMessage(self.ctx, INFO, msg, 'Replicator', '_synchronize()')
        if not self.canceled:
            self.DataBase.executeBatchCall()
            self.DataBase.Connection.commit()
            for account in result.getKeys():
                user = self.Users[account]
                user.MetaData += result.getValue(account)
                print("Replicator._syncData(): %s" % (user.MetaData, ))
                self._syncConnection(user, timestamp)
        self.DataBase.executeBatchCall()
        self.DataBase.Connection.commit()
        self.DataBase.setLoggingChanges(True)
        self.DataBase.saveChanges()
        self.DataBase.Connection.setAutoCommit(True)

    def _syncUser(self, user, timestamp):
        result = KeyMap()
        try:
            if self.canceled:
                return result
            result += self._syncPeople(user, timestamp)
            if self.canceled:
                return result
            result += self._syncGroup(user, timestamp)
        except Exception as e:
            msg = getMessage(self.ctx, 115, (e, traceback.print_exc()))
            logMessage(self.ctx, SEVERE, msg, 'Replicator', '_synchronize()')
        return result

    def _syncPeople(self, user, timestamp):
        token = None
        method = {'Name': 'People',
                  'PrimaryKey': 'Resource',
                  'ResourceFilter': (),
                  'Deleted': (('metadata','deleted'), True),
                  'Filter': (('metadata', 'primary'), True),
                  'Skip': ('Type', 'metadata')}
        pages = update = delete = 0
        parameter = self.Provider.getRequestParameter(method['Name'], user)
        parser = DataParser(self.DataBase, self.Provider, method['Name'])
        map = self.DataBase.getFieldsMap(method['Name'], False)
        enumerator = user.Request.getEnumeration(parameter, parser)
        while not self.canceled and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                u, d, t = self._syncResponse(method, user, map, response.Value, timestamp)
                update += u
                delete += d
                token = t
        format = (pages, update, delete)
        msg = getMessage(self.ctx, 112, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncPeople()')
        self.count += update + delete
        print("replicator._syncPeople() 1 %s" % method['PrimaryKey'])
        return token

    def _syncGroup(self, user, timestamp):
        token = None
        method = {'Name': 'Group',
                  'PrimaryKey': 'Resource',
                  'ResourceFilter': (('groupType', ), g_filter),
                  'Deleted': (('metadata','deleted'), True)}
        pages = update = delete = 0
        parameter = self.Provider.getRequestParameter(method['Name'], user)
        parser = DataParser(self.DataBase, self.Provider, method['Name'])
        map = self.DataBase.getFieldsMap(method['Name'], False)
        enumerator = user.Request.getEnumeration(parameter, parser)
        while not self.canceled and enumerator.hasMoreElements():
            response = enumerator.nextElement()
            status = response.IsPresent
            if status:
                pages += 1
                u, d, t = self._syncResponse(method, user, map, response.Value, timestamp)
                update += u
                delete += d
                token = t
        format = (pages, update, delete)
        msg = getMessage(self.ctx, 113, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncGroup()')
        self.count += update + delete
        return token

    def _syncConnection(self, user, timestamp):
        token = None
        pages = update = delete = 0
        groups = self.DataBase.getUpdatedGroups(user, 'contactGroups/')
        if groups.Count > 0:
            for group in groups:
                self.DataBase.createGroupView(user, group.getValue('Name'), group.getValue('Group'))
            print("replicator._syncConnection(): %s" % ','.join(groups.getKeys()))
            method = {'Name': 'Connection',
                      'PrimaryKey': 'Group',
                      'ResourceFilter': ()}
            parameter = self.Provider.getRequestParameter(method['Name'], groups)
            parser = DataParser(self.DataBase, self.Provider, method['Name'])
            map = self.DataBase.getFieldsMap(method['Name'], False)
            request = user.Request.getRequest(parameter, parser)
            response = request.execute()
            if response.IsPresent:
                pages += 1
                u, d, token = self._syncResponse(method, user, map, response.Value, timestamp)
                update += u
        else:
            print("replicator._syncConnection(): nothing to sync")
        format = (pages, len(groups), update)
        msg = getMessage(self.ctx, 114, format)
        logMessage(self.ctx, INFO, msg, 'Replicator', '_syncConnection()')
        self.count += update
        return token

    def _syncResponse(self, method, user, map, data, timestamp):
        update = delete = 0
        token = None
        for key in data.getKeys():
            field = map.getValue(key).getValue('Type')
            if field == 'Field':
                token = self.DataBase.updateSyncToken(user, key, data, timestamp)
            elif field != 'Header':
                u, d = self._mergeResponse(method, user, map, key, data.getValue(key), timestamp, field)
                update += u
                delete += d
        return update, delete, token

    def _mergeResponse(self, method, user, map, key, data, timestamp, field):
        update = delete = 0
        if field == 'Sequence':
            f = map.getValue(key).getValue('Table')
            for d in data:
                u , d, = self._mergeResponse(method, user, map, key, d, timestamp, f)
                update += u
                delete += d
        elif data.hasValue(method['PrimaryKey']):
            if self._filterResponse(data, *method['ResourceFilter']):
                resource = data.getValue(method['PrimaryKey'])
                func = getattr(self, '_merge%s' % method['Name'])
                update, delete = func(method, resource, user, map, data, timestamp)
        return update, delete

    def _filterResponse(self, data, filters=(), value=None, index=0):
        if index < len(filters):
            filter = filters[index]
            if data.hasValue(filter):
                return self._filterResponse(data.getValue(filter), filters, value, index + 1)
            return False
        return data if value is None else data == value

    def _mergePeople(self, method, resource, user, map, data, timestamp):
        update = delete = 0
        deleted = self._filterResponse(data, *method['Deleted'])
        update, delete = self.DataBase.mergePeople(user, resource, timestamp, deleted)
        for key in data.getKeys():
            if key == method['PrimaryKey']:
                continue
            f = map.getValue(key).getValue('Type')
            update += self._mergePeopleData(method, map, resource, key, data.getValue(key), timestamp, f)
        return update, delete

    def _mergeGroup(self, method, resource, user, map, data, timestamp):
        update = delete = 0
        name = data.getDefaultValue('Name', '')
        deleted = self._filterResponse(data, *method['Deleted'])
        update, delete = self.DataBase.mergeGroup(user, resource, name, timestamp, deleted)
        return update, delete

    def _mergeConnection(self, method, resource, user, map, data, timestamp):
        update = self.DataBase.mergeConnection(user, resource, timestamp)
        return update, 0

    def _mergePeopleData(self, method, map, resource, key, data, timestamp, field):
        update = 0
        if field == 'Sequence':
            f = map.getValue(key).getValue('Table')
            for d in data:
                update += self._mergePeopleData(method, map, resource, key, d, timestamp, f)
        elif field == 'Tables':
            if self._filterResponse(data, *method['Filter']):
                typename = data.getDefaultValue('Type', None)
                for label in data.getKeys():
                    if label in method['Skip']:
                        continue
                    value = data.getValue(label)
                    update += self.DataBase.mergePeopleData(key, resource, typename, label, value, timestamp)
        return update
