#!
# -*- coding: utf-8 -*-

from .configuration import g_identifier

from .unotools import getConfiguration

from .dbinit import getDataSourceUrl
from .dbtools import getDataSourceConnection
from .dbtools import getDataBaseInfo

from .logger import getLogger

from .user import User
from .datasource import DataSource
from .connection import Connection
