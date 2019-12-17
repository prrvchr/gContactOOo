#!
# -*- coding: utf-8 -*-

import traceback
try:
    from .user import User
    from .datasource import DataSource
    from .connection import Connection
    from .provider import Provider

    from .configuration import g_identifier
    from .configuration import g_host
    from .configuration import g_url

    from .dbinit import getDataSourceUrl
    from .dbtools import getDataSourceConnection
    from .dbtools import getDataBaseInfo
except Exception as e:
    print("cloudcontact.__init__() ERROR: %s - %s" % (e, traceback.print_exc()))

