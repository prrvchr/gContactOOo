#!
# -*- coding: utf_8 -*-


from .unotools import getResourceLocation
from .unotools import getSimpleFile

from .dbtools import getTablesAndStatements
from .dbtools import getDataSourceCall
from .dbtools import getSequenceFromResult
from .dbtools import getKeyMapFromResult
from .dbtools import registerDataSource
from .dbtools import executeQueries
from .dbtools import getDataSourceLocation
from .dbtools import getDataSourceInfo
from .dbtools import getDataSourceJavaInfo

from .keymap import KeyMap
from .dbqueries import getSqlQuery
from .configuration import g_path

import traceback


def getDataSourceUrl(ctx, dbctx, dbname, plugin, register):
    location = getResourceLocation(ctx, plugin, g_path)
    url = '%s/%s.odb' % (location, dbname)
    if not getSimpleFile(ctx).exists(url):
        _createDataSource(ctx, dbctx, url, location, dbname)
        if register:
            registerDataSource(dbctx, dbname, url)
    return url

def _createDataSource(ctx, dbcontext, url, location, dbname):
    datasource = dbcontext.createInstance()
    datasource.URL = getDataSourceLocation(location, dbname, False)
    datasource.Info = getDataSourceInfo() + getDataSourceJavaInfo(location)
    datasource.DatabaseDocument.storeAsURL(url, ())
    _createDataBase(ctx, datasource)
    datasource.DatabaseDocument.store()

def _createDataBase(ctx, datasource):
    connection = datasource.getConnection('', '')
    statement = connection.createStatement()
    _createStaticTable(statement, _getStaticTables())
    tables, statements = getTablesAndStatements(statement)
    _executeQueries(statement, tables)
    _createPreparedStatement(ctx, datasource, statements)
    executeQueries(statement, _getQueries())
    _createDynamicView(statement)
    #mri = ctx.ServiceManager.createInstance('mytools.Mri')
    #mri.inspect(connection)
    connection.close()
    connection.dispose()

def _getTableColumns(connection, tables):
    columns = {}
    metadata = connection.MetaData
    for table in tables:
        columns[table] = _getColumns(metadata, table)
    return columns

def _getColumns(metadata, table):
    columns = []
    result = metadata.getColumns("", "", table, "%")
    while result.next():
        column = '"%s"' % result.getString(4)
        print("DbTools._getColumns() %s - %s" % (table, column))
        columns.append(column)
    return columns

def _createStaticTable(statement, tables):
    for table in tables:
        query = getSqlQuery('createTable' + table)
        print("dbtool._createStaticTable(): %s" % query)
        statement.executeQuery(query)
    columns = _getTableColumns(statement.getConnection(), tables)
    for table in tables:
        statement.executeQuery(getSqlQuery('setTableSource', table))
        #format = (table, '|'.join(columns[table]))
        #print("dbtool._createStaticTable(): %s - %s" % format)
        #statement.executeQuery(getSqlQuery('setTableHeader', format))
        #statement.executeQuery(getSqlQuery('setTableReadOnly', table))

def _createPreparedStatement(ctx, datasource, statements):
    queries = datasource.getQueryDefinitions()
    for name, sql in statements.items():
        if not queries.hasByName(name):
            query = ctx.ServiceManager.createInstance("com.sun.star.sdb.QueryDefinition")
            query.Command = sql
            queries.insertByName(name, query)
    datasource.DatabaseDocument.store()
    #mri = ctx.ServiceManager.createInstance('mytools.Mri')
    #mri.inspect(datasource)

def _createDynamicView(statement):
    queries = _getCreateViewQueries(statement)
    _executeQueries(statement, queries)

def _getCreateViewQueries(statement):
    c1 = []
    s1 = []
    f1 = []
    queries = []
    call = getDataSourceCall(statement.getConnection(), 'getViews')
    tables = getSequenceFromResult(statement.executeQuery(getSqlQuery('getViewName')))
    for table in tables:
        call.setString(1, table)
        result = call.executeQuery()
        while result.next():
            c2 = []
            s2 = []
            f2 = []
            data = getKeyMapFromResult(result, KeyMap())
            view = data.getValue('View')
            ptable = data.getValue('PrimaryTable')
            pcolumn = data.getValue('PrimaryColumn')
            ftable = data.getValue('ForeignTable')
            fcolumn = data.getValue('ForeignColumn')
            labelid = data.getValue('LabelId')
            typeid = data.getValue('TypeId')
            c1.append('"%s"' % view)
            c2.append('"%s"' % pcolumn)
            c2.append('"Value"')
            s1.append('"%s"."Value"' % view)
            s2.append('"%s"."%s"' % (table, pcolumn))
            s2.append('"%s"."Value"' % table)
            f = 'LEFT JOIN "%s" ON "%s"."%s"="%s"."%s"' % (view, ftable, fcolumn, view, pcolumn)
            f1.append(f)
            f2.append('"%s"' % table)
            f = 'JOIN "Labels" ON "%s"."Label"="Labels"."Label" AND "Labels"."Label"=%s'
            f2.append(f % (table, labelid))
            if typeid:
                f = 'JOIN "Types" ON "%s"."Type"="Types"."Type" AND "Types"."Type"=%s'
                f2.append(f % (table, typeid))
            format = (view, ','.join(c2), ','.join(s2), ' '.join(f2))
            query = getSqlQuery('createView', format)
            print("dbtool._getCreateViewQueries(): 4 %s" % query)
            queries.append(query)
    call.close()
    if queries:
        c1.insert(0, '"%s"' % pcolumn)
        s1.insert(0, '"%s"."%s"' % (ftable, fcolumn))
        f1.insert(0, 'JOIN "%s" ON "%s"."%s"="%s"."%s"' % (ftable, ptable, pcolumn, ftable, pcolumn))
        f1.insert(0, '"%s"' % ptable)
        f1.append('WHERE "%s"."%s"=CURRENT_USER' % (ptable, pcolumn))
        format = ('AddressBook', ','.join(c1), ','.join(s1), ' '.join(f1))
        query = getSqlQuery('createView', format)
        queries.append(query)
        queries.append( getSqlQuery('grantRole'))
        print("dbtool._getCreateViewQueries(): 5 %s" % query)
    return queries

def _executeQueries(statement, queries):
    for query in queries:
        statement.executeQuery(query)

def _getStaticTables():
    tables = ('Tables',
              'Types',
              'Columns',
              'TableType',
              'TableColumn',
              'Fields',
              'Labels',
              'TableLabel',
              'Settings')
    return tables

def _getQueries():
    return ('createRole', )
