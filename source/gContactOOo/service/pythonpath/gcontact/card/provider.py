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

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE

from ..provider import Provider as ProviderMain

from ..dbtool import currentDateTimeInTZ
from ..dbtool import currentUnoDateTime

from ..configuration import g_host
from ..configuration import g_url
from ..configuration import g_page
from ..configuration import g_member
from ..configuration import g_chunk

import json
import ijson
import traceback


class Provider(ProviderMain):
    def __init__(self, ctx, scr, database):
        ProviderMain.__init__(self, ctx, src)
        paths, maps, types, tmps, fields = database.getMetaData('item', 'metadata')
        self._paths = paths
        self._maps = maps
        self._types = types
        self._tmps = tmps
        self._fields = fields

    @property
    def Host(self):
        return g_host
    @property
    def BaseUrl(self):
        return g_url

# Method called from DataSource.getConnection()
    def getUserUri(self, server, name):
        return name

    def initAddressbooks(self, logger, database, user):
        mtd = 'initAddressbooks'
        logger.logprb(INFO, self._cls, mtd, 1321, user.Name)
        # FIXME: Google Contact only offers one address book...
        name = 'Tous mes Contacts'
        iterator = (item for item in ((user.Uri, name, '', ''), ))
        self.initUserBooks(logger, database, user, iterator)
        logger.logprb(INFO, self._cls, mtd, 1322, user.Name)

    def initUserGroups(self, logger, database, user, uri):
        pass

    # Method called from User.__init__()
    def insertUser(self, logger, database, request, scheme, server, name, pwd):
        mtd = 'insertUser'
        logger.logprb(INFO, self._cls, mtd, 1301, name)
        userid = self._getNewUserId(request, scheme, server, name, pwd)
        logger.logprb(INFO, self._cls, mtd, 1302, userid, name)
        return database.insertUser(userid, scheme, server, '', name)

    # Private method
    def _getNewUserId(self, request, scheme, server, name, pwd):
        parameter = self._getRequestParameter(request, 'getUser')
        response = request.execute(parameter)
        if not response.Ok:
            self.raiseForStatus('_getNewUserId', response, name)
        userid = self._parseUser(response)
        return userid

    def _parseUser(self, response):
        userid = None
        events = ijson.sendable_list()
        parser = ijson.parse_coro(events)
        iterator = response.iterContent(g_chunk, False)
        while iterator.hasMoreElements():
            parser.send(iterator.nextElement().value)
            for prefix, event, value in events:
                if (prefix, event) == ('resourceName', 'string'):
                    userid = self._getResource(value)
            del events[:]
        parser.close()
        response.close()
        return userid


# Method called from Replicator.run()
    def firstPullCard(self, database, user, addressbook, page, count):
        return self._pullCard(database, 'firstPullCard()', user, addressbook, page, count)

    def pullCard(self, database, user, addressbook, page, count):
        return self._pullCard(database, 'pullCard()', user, addressbook, page, count)

    def parseCard(self, database):
        try:
            start = database.getLastSync('CardSync')
            stop = currentDateTimeInTZ()
            iterator = self._parseCardValue(database, start, stop)
            count = database.mergeCardValue(iterator)
            database.updateCardSync(stop)
            return count
        except Exception as e:
            print("Provider.parseCard() ERROR: %s" % traceback.format_exc())

    def syncGroups(self, database, user, addressbook, page, count):
        page, count, args = self._pullGroups(database, user, addressbook, page, count)
        if not args:
            page, count, args = self._pullGroupMembers(database, user, addressbook, page, count)
        return  page, count, args

    # Private method
    def _pullCard(self, database, mtd, user, addressbook, page, count):
        args = []
        parameter = self._getRequestParameter(user.Request, 'getCards', addressbook)
        iterator = self._parseCards(user, parameter, mtd, args)
        count += database.mergeCard(addressbook.Id, iterator)
        page += parameter.PageCount
        if not args:
            if parameter.SyncToken:
                database.updateAddressbookToken(addressbook.Id, parameter.SyncToken)
        return page, count, args

    def _parseCardValue(self, database, start, stop):
        indexes = database.getColumnIndexes()
        for book, card, query, data in database.getChangedCard(start, stop):
            if query == 'Deleted':
                continue
            else:
                for column, value in json.loads(data).items():
                    index = indexes.get(column)
                    if index:
                        yield book, card, index, value

    def _parseCards(self, user, parameter, mtd, args):
        key = tmp = False
        query =  uno.getConstantByName('com.sun.star.rest.ParameterType.QUERY')
        while parameter.hasNextPage():
            response = user.Request.execute(parameter)
            if not response.Ok:
                args += self.getLoggerArgs(response, mtd, parameter, user.Name)
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                parser.send(iterator.nextElement().value)
                for prefix, event, value in events:
                    if (prefix, event) == ('nextPageToken', 'string'):
                        parameter.setNextPage('pageToken', value, query)
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
                        key = tmp = None
                        suffix = ''
                    elif event == 'map_key' and prefix in self._maps and value in self._maps.get(prefix):
                        suffix = value
                    elif event == 'string' and key is None and prefix in self._types:
                        key = self._types.get(prefix).get(value + suffix)
                    elif event == 'string' and tmp is None and prefix in self._tmps:
                        tmp = value
                    elif event == 'end_map' and key and tmp and prefix in self._maps:
                        data[key] = tmp
                        key = tmp = False
                    elif (prefix, event) == ('connections.item', 'end_map'):
                        yield cid, etag, deleted, json.dumps(data)
                del events[:]
            parser.close()
            response.close()

    def _pullGroups(self, database, user, addressbook, page, count):
        args = []
        parameter = self._getRequestParameter(user.Request, 'getGroups', addressbook)
        iterator = self._parseGroups(user, parameter, '_pullGroups()', args)
        count += database.mergeGroup(addressbook.Id, iterator)
        page += parameter.PageCount
        return page, count, args

    def _parseGroups(self, user, parameter, mtd, args):
        while parameter.hasNextPage():
            response = user.Request.execute(parameter)
            if not response.Ok:
                args += self.getLoggerArgs(response, mtd, parameter, user.Name)
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

    def _pullGroupMembers(self, database, user, addressbook, page, count):
        args = []
        timestamp = currentUnoDateTime()
        for gid, group in database.getGroups(addressbook.Id):
            parameter = self._getRequestParameter(user.Request, 'getGroupMembers', group)
            response = user.Request.execute(parameter)
            if not response.Ok:
                args += self.getLoggerArgs(response, '_pullGroupMembers()', parameter, user.Name)
                break
            members = self._parseGroupMembers(response)
            count += database.mergeGroupMembers(gid, timestamp, members)
            page += 1
        return  page, count, args

    def _parseGroupMembers(self, response):
        members = []
        events = ijson.sendable_list()
        parser = ijson.parse_coro(events)
        iterator = response.iterContent(g_chunk, False)
        while iterator.hasMoreElements():
            parser.send(iterator.nextElement().value)
            for prefix, event, value in events:
                if (prefix, event) == ('memberResourceNames.item', 'string'):
                    members.append(self._getResource(value))
            del events[:]
        parser.close()
        response.close()
        return tuple(members)


    def _getRequestParameter(self, request, method, data=None):
        parameter = request.getRequestParameter(method)
        parameter.Url = self.BaseUrl

        if method == 'getUser':
            parameter.Url += '/people/me'
            parameter.setQuery('personFields', 'metadata')

        elif method == 'getCards':
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

        elif method == 'getGroupMembers':
            parameter.Url += '/contactGroups/' + data
            parameter.setQuery('groupFields', 'clientData')
            parameter.setQuery('maxMembers', g_member)

        return parameter

    def _getResource(self, value):
        tmp, sep, value = value.rpartition('/')
        return value

