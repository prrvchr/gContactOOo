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

from com.sun.star.rest.ParameterType import QUERY

from .providerbase import ProviderBase

from .dbtool import currentDateTimeInTZ
from .dbtool import currentUnoDateTime

from .configuration import g_host
from .configuration import g_url
from .configuration import g_page
from .configuration import g_member
from .configuration import g_chunk

import json
from . import ijson
import traceback


class Provider(ProviderBase):
    def __init__(self, ctx, columns, fields):
        self._ctx = ctx
        self._columns = columns
        self._fields = fields
        #self._fields = fields + ('metadata', )

    @property
    def Host(self):
        return g_host
    @property
    def BaseUrl(self):
        return g_url
    @property
    def DateTimeFormat(self):
        return '%Y-%m-%dT%H:%M:%S.%fZ'

    # Method called from DataSource.getConnection()
    def getUserUri(self, server, name):
        return name

    # Method called from User._getNewUser()
    def insertUser(self, database, request, scheme, server, name, pwd):
        parameter = self._getRequestParameter(request, 'getUser')
        response = request.execute(parameter)
        userid = self._parseUser(response)
        return database.insertUser(userid, scheme, server, '', name)

    def _parseUser(self, response):
        userid = None
        if response.Ok:
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                chunk = iterator.nextElement().value
                print("Provider.parseData() Method: %s- Page: %s - Content: \n: %s" % (response.Parameter.Name, response.Parameter.PageCount, chunk.decode('utf-8')))
                parser.send(chunk)
                for prefix, event, value in events:
                    print("Provider.parseData() Prefix: %s - Event: %s - Value: %s" % (prefix, event, value))
                    if (prefix, event) == ('resourceName', 'string'):
                        userid = self._getResource(value)
                del events[:]
            parser.close()
        response.close()
        return userid

    def initAddressbooks(self, database, user):
        print("Provider.initAddressbooks() Name: %s - Uri: %s" % (user.Name, user.Uri))
        # FIXME: Google Contact only offers one address book...
        name = 'Tous mes Contacts'
        iterator = (item for item in ((user.Uri, name, '', ''), ))
        count, modified = user.Addressbooks.initAddressbooks(database, user.Id, iterator)
        if not count:
            #TODO: Raise SqlException with correct message!
            print("User.initAddressbooks() 1 %s" % (addressbooks, ))
            raise self.getSqlException(1004, 1108, 'initAddressbooks', '%s has no support of CardDAV!' % user.Server)
        if modified:
            database.initAddressbooks(user)

    def firstPullCard(self, database, user, addressbook, page, count):
        return self._pullCard(database, user, addressbook, page, count)

    def pullCard(self, database, user, addressbook, page, count):
        return self._pullCard(database, user, addressbook, page, count)

    def _pullCard(self, database, user, addressbook, page, count):
        parameter = self._getRequestParameter(user.Request, 'getPeoples', addressbook)
        count += database.mergeCard(addressbook.Id, self._parsePeople(user.Request, parameter))
        if parameter.SyncToken:
            database.updateAddressbookToken(addressbook.Id, parameter.SyncToken)
        page, count = self._pullGroup(database, user, addressbook, parameter.PageCount, count)
        return parameter.PageCount + page, count

    def _pullGroup(self, database, user, addressbook, page, count):
        parameter = self._getRequestParameter(user.Request, 'getGroups', addressbook)
        count += database.mergeGroup(addressbook.Id, self._parseGroup(user.Request, parameter))
        return parameter.PageCount + page, count

    def parseCard(self, database):
        start = database.getLastUserSync()
        stop = currentDateTimeInTZ()
        iterator = self._parseCard(database, start, stop)
        count = database.mergeCardValue(iterator)
        print("Provider.parseCard() Count: %s" % count)
        database.updateUserSync(stop)

    def syncGroups(self, database):
        database.syncGroups()

    def _parseCard(self, database, start, stop):
        for aid, cid, data, query in database.getChangedCard(start, stop):
            if query == 'Deleted':
                continue
            else:
                for column, value in json.loads(data).items():
                    yield cid, column, value

    def _parsePeople(self, request, parameter):
        print("Provider._parsePeople() Columns Keys: %s" % (self._columns.keys(), ))
        while parameter.hasNextPage():
            response = request.execute(parameter)
            if not response.Ok:
                response.close()
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                chunk = iterator.nextElement().value
                #print("Provider.parseData() Method: %s- Page: %s - Content: \n: %s" % (parameter.Name, parameter.PageCount, chunk.decode('utf-8')))
                parser.send(chunk)
                for prefix, event, value in events:
                    #print("Provider.parseData() Prefix: %s - Event: %s - Value: %s" % (prefix, event, value))
                    if (prefix, event) == ('nextPageToken', 'string'):
                        parameter.setNextPage('pageToken', value, QUERY)
                    elif (prefix, event) == ('nextSyncToken', 'string'):
                        parameter.SyncToken = value
                    elif (prefix, event) == ('connections.item', 'start_map'):
                        cid = etag = None
                        data = {}
                        deleted = False
                    elif (prefix, event) == ('connections.item.metadata.item.deleted.', 'boolean'):
                        deleted = value
                    elif (prefix, event) == ('connections.item.resourceName', 'string'):
                        cid = self._getResource(value)
                    elif (prefix, event) == ('connections.item.etag', 'string'):
                        etag = value
                    elif prefix in self._columns and event == 'string':
                        data[self._columns.get(prefix)] = value
                    elif (prefix, event) == ('connections.item', 'end_map'):
                        yield cid, etag, deleted, json.dumps(data)
                del events[:]
            parser.close()
            response.close()

    def _parseGroup(self, request, parameter):
        print("Provider._parseGroup() Name: %s" % parameter.Name)
        while parameter.hasNextPage():
            response = request.execute(parameter)
            if not response.Ok:
                response.close()
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                chunk = iterator.nextElement().value
                print("Provider._parseGroup() Method: %s- Page: %s - Content: \n: %s" % (parameter.Name, parameter.PageCount, chunk.decode('utf-8')))
                parser.send(chunk)
                for prefix, event, value in events:
                    print("Provider._parseGroup() Prefix: %s - Event: %s - Value: %s" % (prefix, event, value))
                    if (prefix, event) == ('nextPageToken', 'string'):
                        parameter.setNextPage('pageToken', value, QUERY)
                    elif (prefix, event) == ('nextSyncToken', 'string'):
                        parameter.SyncToken = value
                    elif (prefix, event) == ('contactGroups.item', 'start_map'):
                        uri = name = None
                        updated = currentUnoDateTime()
                        parse = deleted = False
                    elif (prefix, event) == ('contactGroups.item.metadata.deleted.', 'boolean'):
                        deleted = value
                    elif (prefix, event) == ('contactGroups.item.metadata.updateTime.', 'string'):
                        updated = self.parseDateTime(value)
                    elif (prefix, event) == ('contactGroups.item.resourceName', 'string'):
                        uri = self._getResource(value)
                    elif (prefix, event) == ('contactGroups.item.name', 'string'):
                        name = value
                    elif (prefix, event) == ('contactGroups.item.groupType.', 'string'):
                        if value == 'USER_CONTACT_GROUP':
                            parse = True
                    elif (prefix, event) == ('contactGroups.item', 'end_map') and parse:
                        yield uri, deleted, name, updated
                del events[:]
            parser.close()
            response.close()


    def _getRequestParameter(self, request, method, data=None):
        parameter = request.getRequestParameter(method)
        parameter.Url = self.BaseUrl
        if method == 'getUser':
            parameter.Url += '/people/me'
            parameter.setQuery('personFields', 'metadata')

        elif method == 'getPeoples':
            parameter.Url += '/people/me/connections'
            parameter.setQuery('personFields', self._fields.get('connections'))
            parameter.setQuery('sources', 'READ_SOURCE_TYPE_CONTACT')
            parameter.setQuery('pageSize', '%s' % g_page)
            if data.Token:
                parameter.setQuery('syncToken', data.Token)
            else:
                parameter.setQuery('requestSyncToken', 'true')

        elif method == 'getGroups':
            parameter.Url += '/contactGroups'
            parameter.setQuery('groupFields', 'name,groupType,memberCount,metadata')
            parameter.setQuery('pageSize', '%s' % g_page)
            if data.Token:
                parameter.setQuery('syncToken', data.Token)
            else:
                parameter.setQuery('requestSyncToken', 'true')

        elif method == 'Connection':
            parameter.Url += '/contactGroups:batchGet'
            parameter.setQuery('resourceNames', json.dumps(data.getKeys()))
            parameter.setQuery('maxMembers', g_member)

        return parameter

    def _getResource(self, value):
        tmp, sep, value = value.partition('/')
        return value

