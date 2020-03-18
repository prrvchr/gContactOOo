#!
# -*- coding: utf_8 -*-

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
        self.ctx = ctx
        self.SessionMode = OFFLINE
        self._Error = ''

    @property
    def Host(self):
        return g_host
    @property
    def BaseUrl(self):
        return g_url

    def isOnLine(self):
        return self.SessionMode != OFFLINE
    def isOffLine(self):
        return self.SessionMode != ONLINE

    def getRequestParameter(self, method, data=None):
        parameter = uno.createUnoStruct('com.sun.star.auth.RestRequestParameter')
        parameter.Name = method
        parameter.Url = self.BaseUrl
        if method == 'getUser':
            parameter.Method = 'GET'
            parameter.Url += '/people/me'
            parameter.Query = '{"personFields": "%s"}' % ','.join(data.Fields)
        elif method == 'People':
            parameter.Method = 'GET'
            parameter.Url += '/people/me/connections'
            fields = '"personFields": "%s"' % ','.join(data.Fields)
            page = '"pageSize": %s' % g_page
            sync = data.PeopleSync
            if sync:
                token = '"syncToken": "%s"' % sync
            else:
                token = '"requestSyncToken": true'
            parameter.Query = '{%s, %s, %s}' % (fields, page, token)
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
            resources = '","'.join(data.getValue('Resources'))
            parameter.Query = '{"maxMembers": %s, "resourceNames": ["%s"]}' % (g_member, resources)
        return parameter

    def transcode(self, name, value):
        if name == 'People':
            value = self._getResource('people', value)
        elif name == 'Group':
            value = self._getResource('contactGroups', value)
        return value
    def transform(self, name, value):
        if name == 'Resource' and value.startswith('people'):
            value = value.split('/').pop()
        return value

    def getUser(self, request, user):
        parameter = self.getRequestParameter('getUser', user)
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
            
