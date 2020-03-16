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
g_member = 500
g_admin = False

g_timestamp = '%Y-%m-%dT%H:%M:%S.00'
g_IdentifierRange = (10, 50)
g_userfields = 'userDefined'
g_peoplefields = 'addresses,emailAddresses,names,organizations,phoneNumbers,sipAddresses,userDefined'
