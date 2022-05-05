#!
# -*- coding: utf_8 -*-

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

from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.auth.RestRequestTokenType import TOKEN_NONE
from com.sun.star.auth.RestRequestTokenType import TOKEN_URL
from com.sun.star.auth.RestRequestTokenType import TOKEN_REDIRECT
from com.sun.star.auth.RestRequestTokenType import TOKEN_QUERY
from com.sun.star.auth.RestRequestTokenType import TOKEN_JSON
from com.sun.star.auth.RestRequestTokenType import TOKEN_SYNC

from com.sun.star.sdbc import XRestProvider

from .unotool import getConnectionMode

from .configuration import g_host
from .configuration import g_url
from .configuration import g_page
from .configuration import g_member
from .logger import logMessage
from .logger import getMessage

import json


class Provider(unohelper.Base,
               XRestProvider):
    def __init__(self, ctx):
        self._ctx = ctx
        self._Error = ''
        self.SessionMode = OFFLINE

    @property
    def Host(self):
        return g_host
    @property
    def BaseUrl(self):
        return g_url

    def isOnLine(self):
        return getConnectionMode(self._ctx, self.Host) != OFFLINE
    def isOffLine(self):
        return getConnectionMode(self._ctx, self.Host) != ONLINE

    def getRequestParameter(self, method, data=None):
        parameter = uno.createUnoStruct('com.sun.star.auth.RestRequestParameter')
        parameter.Name = method
        parameter.Url = self.BaseUrl
        if method == 'getUser':
            parameter.Method = 'GET'
            parameter.Url += '/people/me'
            parameter.Query = '{"personFields": "%s"}' % ','.join(data)
        elif method == 'People':
            parameter.Method = 'GET'
            parameter.Url += '/people/me/connections'
            fields = '"personFields": "%s"' % ','.join(data.Fields)
            sources = '"sources": "READ_SOURCE_TYPE_CONTACT"'
            page = '"pageSize": %s' % g_page
            sync = data.PeopleSync
            if sync:
                token = '"syncToken": "%s"' % sync
            else:
                token = '"requestSyncToken": true'
            parameter.Query = '{%s, %s, %s, %s}' % (fields, sources, page, token)
            token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            token.Type = TOKEN_QUERY | TOKEN_SYNC
            token.Field = 'nextPageToken'
            token.Value = 'pageToken'
            token.SyncField = 'nextSyncToken'
            enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            enumerator.Field = 'connections'
            enumerator.Token = token
            parameter.Enumerator = enumerator
        elif method == 'Group':
            parameter.Method = 'GET'
            parameter.Url += '/contactGroups'
            page = '"pageSize": %s' % g_page
            query = [page]
            sync = data.GroupSync
            if sync:
                query.append('"syncToken": "%s"' % sync)
            parameter.Query = '{%s}' % ','.join(query)
            token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            token.Type = TOKEN_QUERY | TOKEN_SYNC
            token.Field = 'nextPageToken'
            token.Value = 'pageToken'
            token.SyncField = 'nextSyncToken'
            enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            enumerator.Field = 'contactGroups'
            enumerator.Token = token
            parameter.Enumerator = enumerator
        elif method == 'Connection':
            parameter.Method = 'GET'
            parameter.Url += '/contactGroups:batchGet'
            resources = '","'.join(data.getKeys())
            parameter.Query = '{"resourceNames": ["%s"], "maxMembers": %s}' % (resources, g_member)
        return parameter

    def transcode(self, name, value):
        if name == 'People':
            value = self._getResource('people', value)
        elif name == 'Group':
            value = self._getResource('contactGroups', value)
        return value
    def transform(self, name, value):
        #if name == 'Resource' and value.startswith('people'):
        #    value = value.split('/').pop()
        return value

    def getUser(self, request, fields):
        parameter = self.getRequestParameter('getUser', fields)
        return request.execute(parameter)
    def getUserId(self, user):
        return user.getValue('resourceName').split('/').pop()
        #return user.getValue('resourceName')
    def getItemId(self, item):
        return item.getDefaultValue('resourceName', '').split('/').pop()

    def _getResource(self, resource, keys):
        groups = []
        for k in keys:
            groups.append('%s/%s' % (resource, k))
        return tuple(groups)
            
