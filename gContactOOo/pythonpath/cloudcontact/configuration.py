#!
# -*- coding: utf_8 -*-

# General configuration
g_identifier = 'com.gmail.prrvchr.extensions.CloudContactOOo'
g_host = 'people.googleapis.com'
g_version = 'v1'
g_url = 'https://%s/%s' % (g_host, g_version)
g_timestamp = '%Y-%m-%dT%H:%M:%S.00'
g_IdentifierRange = (10, 50)
g_userfields = 'userDefined'
g_peoplefields = 'addresses,emailAddresses,names,organizations,phoneNumbers,sipAddresses,userDefined'

# Request / OAuth2 configuration
g_oauth2 = 'com.gmail.prrvchr.extensions.OAuth2OOo.OAuth2Service'

# DataSource configuration
g_protocol = 'jdbc:hsqldb:'
g_path = 'hsqldb'
g_jar = 'hsqldb.jar'
g_class = 'org.hsqldb.jdbcDriver'
g_options = ';default_schema=true;hsqldb.default_table_type=cached;get_column_name=false;ifexists=false'
g_shutdown = ';shutdown=true'
g_csv = '%s.csv;fs=|;ignore_first=true;encoding=UTF-8;quoted=true'
