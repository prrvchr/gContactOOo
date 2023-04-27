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
    def __init__(self, ctx, paths, maps, types, tmps, fields):
        self._ctx = ctx
        self._paths = dict(list(paths))
        for p in self._paths:
            print("Provider.__init__() Paths: %s - %s" % (p, self._paths[p]))
        self._maps = dict(list(maps))
        for p in self._maps:
            print("Provider.__init__() Maps: %s - %s" % (p, self._maps[p]))
        self._types = dict(list(types))
        for p in self._types:
            print("Provider.__init__() Types: %s - %s" % (p, self._types[p]))
        self._tmps = list(tmps)
        print("Provider.__init__() Tmps: %s" % (self._tmps, ))
        self._fields = next(fields)
        print("Provider.__init__() Fileds: %s" % self._fields)

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

    def parseCard(self, database):
        start = database.getLastUserSync()
        stop = currentDateTimeInTZ()
        iterator = self._parseCard(database, start, stop)
        count = database.mergeCardValue(iterator)
        print("Provider.parseCard() Count: %s" % count)
        database.updateUserSync(stop)

    def syncGroups(self, database, user, addressbook, pages, count):
        timestamp = currentUnoDateTime()
        for gid, group in database.getGroups(addressbook.Id):
            parameter = self._getRequestParameter(user.Request, 'getGroup', group)
            count += database.mergeGroupData(gid, timestamp, self._parseGroup(user.Request, parameter))
            pages += parameter.PageCount
        return  pages, count

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

    def _pullCard(self, database, user, addressbook, page, count):
        parameter = self._getRequestParameter(user.Request, 'getPeoples', addressbook)
        count += database.mergeCard(addressbook.Id, self._parsePeople(user.Request, parameter))
        if parameter.SyncToken:
            database.updateAddressbookToken(addressbook.Id, parameter.SyncToken)
        page, count = self._pullGroup(database, user, addressbook, parameter.PageCount, count)
        return parameter.PageCount + page, count

    def _pullGroup(self, database, user, addressbook, page, count):
        parameter = self._getRequestParameter(user.Request, 'getGroups', addressbook)
        count += database.mergeGroup(addressbook.Id, self._parseGroups(user.Request, parameter))
        return parameter.PageCount + page, count

    def _parseCard(self, database, start, stop):
        indexes = database.getColumnIndexes()
        for aid, cid, data, query in database.getChangedCard(start, stop):
            if query == 'Deleted':
                continue
            else:
                for column, value in json.loads(data).items():
                    i = indexes.get(column)
                    if i:
                        yield cid, i, value
                    else:
                        print("Provider._parseCard() CID: %s - Column: '%s' - Value: '%s'" % (cid, column, value))

    def _parsePeople(self, request, parameter):
        map = tmp = False
        while parameter.hasNextPage():
            response = request.execute(parameter)
            if not response.Ok:
                response.close()
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                parser.send(iterator.nextElement().value)
                for prefix, event, value in events:
                    if (prefix, event) == ('nextPageToken', 'string'):
                        parameter.setNextPage('pageToken', value, QUERY)
                    elif (prefix, event) == ('nextSyncToken', 'string'):
                        parameter.SyncToken = value
                    elif (prefix, event) == ('connections.item', 'start_map'):
                        cid = etag = tmp = label = None
                        data = {}
                        deleted = False
                    elif (prefix, event) == ('connections.item.metadata.item.deleted.', 'boolean'):
                        deleted = value
                    elif (prefix, event) == ('connections.item.resourceName', 'string'):
                        cid = self._getResource(value)
                    elif (prefix, event) == ('connections.item.etag', 'string'):
                        etag = value
                    # FIXME: All the data parsing is done based on the tables: Resources, Properties and Types 
                    # FIXME: Only properties listed in these tables will be parsed
                    # FIXME: This is the part for simple property import (use of tables: Resources and Properties)
                    elif event == 'string' and prefix in self._paths:
                        data[self._paths.get(prefix)] = value
                    # FIXME: This is the part for typed property import (use of tables: Resources, Properties and Types)
                    elif event == 'start_map' and prefix in self._maps:
                        map = tmp = None
                        suffix = ''
                    elif event == 'map_key' and prefix in self._maps and value in self._maps.get(prefix):
                        suffix = value
                    elif event == 'string' and map is None and prefix in self._types:
                        map = self._types.get(prefix).get(value + suffix)
                    elif event == 'string' and tmp is None and prefix in self._tmps:
                        tmp = value
                    elif event == 'end_map' and map and tmp and prefix in self._maps:
                        data[map] = tmp
                        map = tmp = False
                    elif (prefix, event) == ('connections.item', 'end_map'):
                        yield cid, etag, deleted, json.dumps(data)
                del events[:]
            parser.close()
            response.close()

    def _parseGroups(self, request, parameter):
        while parameter.hasNextPage():
            response = request.execute(parameter)
            if not response.Ok:
                response.close()
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                parser.send(iterator.nextElement().value)
                for prefix, event, value in events:
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
                        print("Provider._parseGroups() resourceName: %s" % value)
                        uri = self._getResource(value)
                    elif (prefix, event) == ('contactGroups.item.name', 'string'):
                        name = value
                    elif (prefix, event) == ('contactGroups.item.groupType', 'string'):
                        parse = value == 'USER_CONTACT_GROUP'
                    elif (prefix, event) == ('contactGroups.item', 'end_map') and parse:
                        yield uri, deleted, name, updated
                del events[:]
            parser.close()
            response.close()

    def _parseGroup(self, request, parameter):
        response = request.execute(parameter)
        if response.Ok:
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            members = []
            while iterator.hasMoreElements():
                parser.send(iterator.nextElement().value)
                for prefix, event, value in events:
                    if (prefix, event) == ('memberResourceNames.item', 'string'):
                        members.append(self._getResource(value))
                del events[:]
            yield members
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
            parameter.setQuery('personFields', self._fields)
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
            #TODO: We need to manager Token and deleted record
            #if data.Token:
            #    parameter.setQuery('syncToken', data.Token)
            #else:
            #parameter.setQuery('requestSyncToken', 'true')

        elif method == 'getGroup':
            parameter.Url += f'/contactGroups/{data}'
            parameter.setQuery('groupFields', 'clientData')
            parameter.setQuery('maxMembers', g_member)

        return parameter

    def _getResource(self, value):
        tmp, sep, value = value.partition('/')
        return value

