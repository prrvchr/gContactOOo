#!
# -*- coding: utf_8 -*-

# General configuration
g_extension = 'gContactOOo'
g_identifier = 'com.gmail.prrvchr.extensions.%s' % g_extension
g_logger = '%s.Logger' % g_identifier

g_host = 'people.googleapis.com'
g_version = 'v1'
g_url = 'https://%s/%s' % (g_host, g_version)
g_page = 100
g_member = 1000
g_admin = False
g_sync = 600

g_group = 'all'
g_filter = 'USER_CONTACT_GROUP'
g_timestamp = '%Y-%m-%dT%H:%M:%S.00'
