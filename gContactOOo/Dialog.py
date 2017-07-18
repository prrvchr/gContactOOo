#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo, Locale
from com.sun.star.task import XJobExecutor, XInteractionHandler
from com.sun.star.awt import XDialogEventHandler, XActionListener, XItemListener
from com.sun.star.sdbc import XRowSetListener
from com.sun.star.uno import XCurrentContext
from com.sun.star.mail import XAuthenticator, MailAttachment
from com.sun.star.datatransfer import XTransferable, DataFlavor
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.gContactOOo.Dialog"

g_SettingNodePath = "com.gmail.prrvchr.extensions.gContactOOo/Options"


class PyDialog(unohelper.Base, XServiceInfo, XJobExecutor, XDialogEventHandler, XActionListener, XItemListener,
                XRowSetListener, XCurrentContext, XAuthenticator, XTransferable, XInteractionHandler):
    def __init__(self, ctx):
        self.ctx = ctx
        self.tableindex = 0
        self.columnindex = 4
        self.columnfilters = (0, 1, 4)
        self.attachmentsjoin = ", "
        self.maxsize = 5 * 1024 * 1024
        self.transferable = []
        self.dialog = None
        self.table = None
        self.query = None
        self.address = None
        self.recipient = None
        self.index = None
        self.step = 1

    # XJobExecutor
    def trigger(self, args):
        self._openDialog()

    # XInteractionHandler
    def handle(self, request):
        pass

    # XCurrentContext
    def getValueByName(self, name):
        if name == "ServerName":
            return self._getConfiguration("/org.openoffice.Office.Writer/MailMergeWizard").getByName("MailServer")
        elif name == "Port":
            return self._getConfiguration("/org.openoffice.Office.Writer/MailMergeWizard").getByName("MailPort")
        elif name ==  "ConnectionType":
            if self._getConfiguration("/org.openoffice.Office.Writer/MailMergeWizard").getByName("IsSecureConnection"):
                return "SSL"
            else:
                return "Insecure"

    # XAuthenticator
    def getUserName(self):
        return self._getConfiguration("/org.openoffice.Office.Writer/MailMergeWizard").getByName("MailUserName")
    def getPassword(self):
        return self._getConfiguration("/org.openoffice.Office.Writer/MailMergeWizard").getByName("MailPassword")

    # XTransferable
    def getTransferData(self, flavor):
        transferable = self.transferable.pop(0)
        if transferable == "body":
            if flavor.MimeType == "text/plain;charset=utf-16":
                return self._getDocumentDescription()
            elif flavor.MimeType == "text/html;charset=utf-8":
                return self._getUrlContent(self._saveDocumentAs("html"))
        else:
            return self._getUrlContent(transferable)
    def getTransferDataFlavors(self):
        flavor = DataFlavor()
        transferable = self.transferable[0]
        if transferable == "body":
            if self._getDocumentUserProperty("SendAsHtml"):
                flavor.MimeType = "text/html;charset=utf-8"
                flavor.HumanPresentableName = "HTML-Documents"
            else:
                flavor.MimeType = "text/plain;charset=utf-16"
                flavor.HumanPresentableName = "Unicode text"
        else:
            type = self._getAttachmentType(transferable)
            flavor.MimeType = type
            flavor.HumanPresentableName = type
        return (flavor,)
    def isDataFlavorSupported(self, flavor):
        transferable = self.transferable[0]
        if transferable == "body":
            return (flavor.MimeType == "text/plain;charset=utf-16" or flavor.MimeType == "text/html;charset=utf-8")
        else:
            return flavor.MimeType == self._getAttachmentType(transferable)

    # XDialogEventHandler
    def callHandlerMethod(self, dialog, event, method):
        if self.dialog == dialog:
            if method == "DialogBack":
                self._setStep(self.step - 1)
                return True
            elif method == "DialogNext":
                self._setStep(self.step + 1)
                return True
            elif method == "AddressBook":
                self._executeShell("thunderbird", "-addressbook")
                return True
            elif method == "RecipientAdd":
                self._recipientAdd()
                return True
            elif method == "RecipientAddAll":
                self._recipientAddAll()
                return True
            elif method == "RecipientRemove":
                self._recipientRemove()
                return True
            elif method == "RecipientRemoveAll":
                self._recipientRemoveAll()
                return True
            elif method == "SendAsHtml":
                state = (event.Source.Model.State == 1)
                self._setDocumentUserProperty("SendAsHtml", state)
                self.dialog.getControl("Description").Model.Enabled = not state
                return True
            elif method == "ViewHtml":
                url = self._saveDocumentAs("html")
                self._executeShell(url)
                return True
            elif method == "SendAsPdf":
                state = (event.Source.Model.State == 1)
                self._setDocumentUserProperty("SendAsPdf", state)
                return True
            elif method == "ViewPdf":
                url = self._saveDocumentAs("pdf")
                self._executeShell(url)
                return True
            elif method == "AttachmentAdd":
                self._addAttachments()
                return True
            elif method == "AttachmentRemove":
                self._removeAttachments()
                return True
            elif method == "AttachmentView":
                self._viewAttachments()
                return True
        return False
    def getSupportedMethodNames(self):
        return ("DialogBack", "DialogNext", "AddressBook", "RecipientAdd", "RecipientAddAll",
                "RecipientRemove", "RecipientRemoveAll", "SendAsHtml", "ViewHtml", "SendAsPdf",
                "ViewPdf", "AttachmentAdd", "AttachmentRemove", "AttachmentView")

    # XActionListener, XItemListener, XRowSetListener
    def disposing(self, event):
        pass
    def actionPerformed(self, event):
        if event.Source == self.dialog.getControl("DataSource"):
            self._setDataSource(event.Source.SelectedItem)
        elif event.Source == self.dialog.getControl("AddressBook"):
            self._setAddressBook(event.Source.SelectedItem)
    def itemStateChanged(self, event):
        if event.Source == self.dialog.getControl("Address"):
            self._setAddress(event.Source.SelectedItemPos)
        elif event.Source == self.dialog.getControl("Recipient"):
            self._setRecipient(event.Source.SelectedItemPos)
        elif event.Source == self.dialog.getControl("Attachments"):
            self._setAttachments(event.Source.SelectedItemPos)
    def cursorMoved(self, event):
        pass
    def rowChanged(self, event):
        pass
    def rowSetChanged(self, event):
        if event.Source == self.address:
            self._updateAddress()
        elif event.Source == self.recipient:
            self._updateRecipient()

    # XServiceInfo
    def supportsService(self, serviceName):
        return g_ImplementationHelper.supportsService(g_ImplementationName, serviceName)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)

    def _openDialog(self):
        provider = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.DialogProvider", self.ctx)
        self.dialog = provider.createDialogWithHandler("vnd.sun.star.script:gContactOOo.Dialog?location=application", self)
        self.dialog.getControl("AddressBook").addActionListener(self)
        self.dialog.getControl("Address").addItemListener(self)
        self.dialog.getControl("Recipient").addItemListener(self)
        self.dialog.getControl("Attachments").addItemListener(self)
        self.address = self.ctx.ServiceManager.createInstance("com.sun.star.sdb.RowSet")
        self.address.CommandType = uno.getConstantByName("com.sun.star.sdb.CommandType.TABLE")
        self.address.addRowSetListener(self)
        self.recipient = self.ctx.ServiceManager.createInstance("com.sun.star.sdb.RowSet")
        self.recipient.CommandType = uno.getConstantByName("com.sun.star.sdb.CommandType.QUERY")
        self.recipient.addRowSetListener(self)
        datasources = self._getDataSources()
        control = self.dialog.getControl("DataSource")
        control.addActionListener(self)
        control.Model.StringItemList = datasources
        datasource = self._getDocumentDataSource()
        if datasource in datasources:
            control.selectItem(datasource, True)
            self._setStep()
        elif control.ItemCount:
            control.selectItemPos(0, True)
            self._setStep()
        else:
            self._logMessage("TextMsg", "12.Dialog.TextMsg.Text")
        self._loadDialog()
        self.dialog.execute()
        self._saveDialog()
        self.dialog.dispose()
        self.dialog = None

    def _loadDialog(self):
        self.dialog.getControl("Subject").Text = self._getDocumentSubject()
        self.dialog.getControl("Description").Text = self._getDocumentDescription()
        self.dialog.getControl("SendAsHtml").Model.State = self._getDocumentUserProperty("SendAsHtml", False)
        self.dialog.getControl("SendAsPdf").Model.State = self._getDocumentUserProperty("SendAsPdf", True)
        self.dialog.getControl("Attachments").Model.StringItemList = self._getAttachmentsPath()

    def _getAttachments(self):
        attachments = self._getDocumentUserProperty("Attachments")
        attachments = attachments.split(self.attachmentsjoin) if attachments else []
        return attachments

    def _getAttachmentsPath(self):
        paths = []
        for url in self._getAttachments():
            paths.append(uno.fileUrlToSystemPath(url))
        return paths

    def _getAttachmentsString(self):
        urls = []
        for path in self.dialog.getControl("Attachments").Model.StringItemList:
            urls.append(uno.systemPathToFileUrl(path))
        return self.attachmentsjoin.join(urls)

    def _getDataSources(self, url="sdbc:address:thunderbird"):
        datasources = []
        context = self.ctx.ServiceManager.createInstance("com.sun.star.sdb.DatabaseContext")
        for datasource in context.ElementNames:
            if context.getByName(datasource).URL == url:
                id = "13.Dialog.TextMsg.Text"
                datasources.append(datasource)
            else:
                id = "14.Dialog.TextMsg.Text"
            self._logMessage("TextMsg", id, (datasource,))
        return datasources

    def _setDataSource(self, datasource):
        database = self._getDatabase(datasource)
        connection = self._getConnection(database)
        if connection is None:
            self._logMessage("TextMsg", "15.Dialog.TextMsg.Text", (datasource,))
        else:
            self._logMessage("TextMsg", "16.Dialog.TextMsg.Text", (datasource,))
            self.table = connection.Tables.getByIndex(self.tableindex)
            self.address.DataSourceName = datasource
            self.address.Filter = self._getQueryFilter()
            self.address.ApplyFilter = True
            self.address.Order = self._getQueryOrder()
            self.query = self._getQuery(database)
            self._setDocumentDataSource(datasource, self.query.Name)
            tables = connection.Tables.ElementNames
            control = self.dialog.getControl("AddressBook")
            control.Model.StringItemList = tables
            if self.query.UpdateTableName in tables:
                control.selectItem(self.query.UpdateTableName, True)
            elif control.ItemCount:
                control.selectItemPos(0, True)
            self.recipient.DataSourceName = datasource
            self.recipient.Command = self.query.Name
            self.recipient.Filter = self.query.Filter
            self.recipient.ApplyFilter = True
            self.recipient.Order = self.query.Order
            self.recipient.execute()
            self._closeConnection(connection)
            self._logMessage("TextMsg", "17.Dialog.TextMsg.Text")

    def _setAddressBook(self, table):
        self.query.UpdateTableName = table
        self.address.Command = table
        self.address.execute()

    def _getColumn(self, index=None):
        index = self.columnindex if index is None else index
        return self.table.Columns.getByIndex(index)

    def _getQuery(self, database, queryname="gContactOOo"):
        queries = database.QueryDefinitions
        if queries.hasByName(queryname):
            query = queries.getByName(queryname)
        else:
            query = self.ctx.ServiceManager.createInstance("com.sun.star.sdb.QueryDefinition")
            query.Command = self._getQueryCommand()
            query.Filter = self._getQueryFilter([])
            query.Order = self._getQueryOrder()
            query.UpdateTableName = self.table.Name
            query.ApplyFilter = True
            queries.insertByName(queryname, query)
            database.DatabaseDocument.store()
        return query

    def _getQueryCommand(self):
        command = "SELECT * FROM \"%s\"" % (self.table.Name)
        return command

    def _getQueryFilter(self, filters=None):
        f = []
        for column in self.columnfilters:
            f.append("\"%s\" IS NOT NULL" % (self._getColumn(column).Name))
        filter = " AND ".join(f)
        if filters is None:
            result = "(%s)" % (filter)
        elif len(filters):
            result = "(%s)" % (" OR ".join(filters))
        else:
            result = "(%s AND \"%s\" = '')" % (filter, self._getColumn().Name)
        return result

    def _getQueryOrder(self):
        order = "\"%s\"" % (self._getColumn().Name)
        return order

    def _getRowResult(self, rowset, column=None):
        column = self.columnindex + 1 if column is None else column
        result = []
        rowset.beforeFirst()
        while rowset.next():
            result.append(rowset.getString(column))
        return result

    def _getRecipientFilter(self, rows=[]):
        result = []
        self.recipient.beforeFirst()
        while self.recipient.next():
            row = self.recipient.Row -1
            if row not in rows:
                result.append(self._getFilter(self.recipient))
        return result

    def _getAddressFilter(self, rows, filters=[]):
        result = []
        self.address.beforeFirst()
        for row in rows:
            self.address.absolute(row +1)
            filter = self._getFilter(self.address)
            if filter not in filters:
                result.append(filter)
        return result

    def _getFilter(self, rowset):
        result = []
        for column in self.columnfilters:
            value = rowset.getString(column +1).replace("'", "''")
            result.append("\"%s\" = '%s'" % (self._getColumn(column).Name, value))
        return "(%s)" % (" AND ".join(result))

    def _updateAddress(self):
        self.dialog.getControl("ButtonAdd").Model.Enabled = False
        address = self.dialog.getControl("Address").Model
        address.StringItemList = self._getRowResult(self.address)
        self.dialog.getControl("ButtonAddAll").Model.Enabled = (self.address.RowCount != 0)

    def _updateRecipient(self):
        self.dialog.getControl("ButtonRemove").Model.Enabled = False
        recipient = self.dialog.getControl("Recipient")
        recipient.Model.StringItemList = self._getRowResult(self.recipient)
        if not len(recipient.Model.SelectedItems):
            if recipient.ItemCount:
                recipient.selectItemPos(0, True)
        self.dialog.getControl("ButtonRemoveAll").Model.Enabled = (self.recipient.RowCount != 0)
        if self.dialog.Model.Step == 2:
            self.dialog.getControl("ButtonNext").Model.Enabled = (self.recipient.RowCount != 0)

    def _getDocumentDataSource(self, document=None):
        document = self._getDocument() if document is None else document
        if document.supportsService("com.sun.star.text.TextDocument"):
            settings = document.createInstance("com.sun.star.document.Settings")
            return settings.CurrentDatabaseDataSource
        return None

    def _setDocumentDataSource(self, datasource, queryname, document=None):
        document = self._getDocument() if document is None else document
        if self._getDocumentDataSource(document) != datasource:
            if document.supportsService("com.sun.star.text.TextDocument"):
                settings = document.createInstance("com.sun.star.document.Settings")
                settings.CurrentDatabaseDataSource = datasource
                fields = document.TextFields.createEnumeration()
                while fields.hasMoreElements():
                    field = fields.nextElement()
                    master = field.TextFieldMaster
                    if master.supportsService("com.sun.star.text.fieldmaster.Database"):
                        master.DataBaseName = datasource
                        master.DataTableName = queryname

    def _getDocument(self):
        desktop = self.ctx.ServiceManager.createInstanceWithContext( "com.sun.star.frame.Desktop", self.ctx)
        return desktop.CurrentComponent

    def _checkMessages(self):
        if self._checkMailService() and self._checkAttachments():
            self._logMessage("TextMerge", "76.Dialog.TextMerge.Text", (self._getPageCount(), self.recipient.RowCount))
            return True
        return False
        
    def _checkMailService(self):
        try:
            self._logMessage("TextMerge", "69.Dialog.TextMerge.Text")
            service = self._getMailService()
            service.connect(self, self)
            if service.isConnected():
                service.disconnect()
                self._logMessage("TextMerge", "70.Dialog.TextMerge.Text")
                return True
            return False
        except Exception as e:
            self._logMessage("TextMerge", "71.Dialog.TextMerge.Text", (e,))
            return False

    def _getPageCount(self, document=None):
        document = self._getDocument() if document is None else document
        if document.supportsService("com.sun.star.text.TextDocument"):
            return document.CurrentController.PageCount
        elif document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
            return 1
        elif document.supportsService("com.sun.star.drawing.DrawingDocument"):
            return 1
        elif document.supportsService("com.sun.star.presentation.PresentationDocument"):
            return 1
        elif document.supportsService("com.sun.star.formula.FormulaProperties"):
            return 1

    def _checkAttachments(self):
        state = True
        service = self.ctx.ServiceManager.createInstance("com.sun.star.ucb.SimpleFileAccess")
        for url in self._getAttachments():
            state = state and self._checkAttachment(service, url)
        return state

    def _checkAttachment(self, service, url):
        self._logMessage("TextMerge", "72.Dialog.TextMerge.Text", (uno.fileUrlToSystemPath(url),))
        if service.exists(url):
            size = service.getSize(url)
            if size != 0 and size <= self.maxsize:
               self._logMessage("TextMerge", "73.Dialog.TextMerge.Text")
               return True
            else:
                self._logMessage("TextMerge", "74.Dialog.TextMerge.Text")
        else:
            self._logMessage("TextMerge", "75.Dialog.TextMerge.Text")
        return False

    def _setStep(self, step=2):
        self._saveDialog()
        self.step = step
        self.dialog.Model.Step = step if step < 6 else self.dialog.Model.Step
        self._initStep()

    def _initStep(self):
        resource = self._getStringResource()
        buttonNext = self.dialog.getControl("ButtonNext")
        if self.step == 1:
            self.dialog.Title = resource.resolveString("1.Dialog.Title")
            self.dialog.getControl("ButtonBack").Model.Enabled = False
            buttonNext.Model.Enabled = True
        elif self.step == 2:
            self.dialog.Title = resource.resolveString("2.Dialog.Title")
            self.dialog.getControl("ButtonBack").Model.Enabled = True
            buttonNext.Model.Enabled = (self.recipient.RowCount != 0)
        elif self.step == 3:
            self.dialog.Title = resource.resolveString("3.Dialog.Title")
        elif self.step == 4:
            self.dialog.Title = resource.resolveString("4.Dialog.Title")
            buttonNext.Model.Enabled = True
            buttonNext.Model.Label = resource.resolveString("21.Dialog.ButtonNext.Label")
        elif self.step == 5:
            self.dialog.Title = resource.resolveString("5.Dialog.Title")
            buttonNext.Model.Enabled = False
            buttonNext.Model.Label = resource.resolveString("22.Dialog.ButtonNext.Label")
            self.dialog.getControl("TextMerge").Text = ""
            buttonNext.Model.Enabled = self._checkMessages()
        elif self.step == 6:
            self.dialog.Title = resource.resolveString("6.Dialog.Title")
            buttonNext.Model.Enabled = False
            self._sendMessages()
            buttonNext.Model.Label = resource.resolveString("23.Dialog.ButtonNext.Label")
            buttonNext.Model.Enabled = True
        elif self.step == 7:
            self.dialog.Title = resource.resolveString("7.Dialog.Title")
            self.dialog.endExecute()

    def _saveDialog(self):
        if self.step == 2:
            if self.query is not None:
                self.recipient.ActiveConnection.Parent.DatabaseDocument.store()
        elif self.step == 3:
            self._setDocumentProperty()
        elif self.step == 4:
            self._setDocumentUserProperty("Attachments", self._getAttachmentsString())

    def _recipientAdd(self):
        recipients = self._getRecipientFilter()
        filters = self._getAddressFilter(self.dialog.getControl("Address").Model.SelectedItems, recipients)
        self._rowRecipientExecute(recipients + filters)

    def _recipientAddAll(self):
        recipients = self._getRecipientFilter()
        filters = self._getAddressFilter(range(self.address.RowCount), recipients)
        self._rowRecipientExecute(recipients + filters)
        
    def _recipientRemove(self):
        recipient = self.dialog.getControl("Recipient").Model
        recipients = self._getRecipientFilter(recipient.SelectedItems)
        self._rowRecipientExecute(recipients)

    def _recipientRemoveAll(self):
        self._rowRecipientExecute([])

    def _rowRecipientExecute(self, filters):
        self.query.ApplyFilter = False
        self.recipient.ApplyFilter = False
        self.query.Filter = self._getQueryFilter(filters)
        self.recipient.Filter = self.query.Filter
        self.recipient.ApplyFilter = True
        self.query.ApplyFilter = True
        self.recipient.execute()

    def _setAddress(self, position):
        self.dialog.getControl("ButtonAdd").Model.Enabled = (position != -1)

    def _setRecipient(self, position):
        self.dialog.getControl("ButtonRemove").Model.Enabled = (position != -1)
        if position != -1 and position != self.index:
            self._setDocumentRecord(position)

    def _setAttachments(self, position):
        state = (position != -1)
        self.dialog.getControl("ButtonRemoveAttachment").Model.Enabled = state
        self.dialog.getControl("ButtonViewAttachment").Model.Enabled = state

    def _saveDocumentAs(self, type, url=None):
        document = self._getDocument()
        if document.supportsService("com.sun.star.document.OfficeDocument"):
            url = self._getBaseUrl(document, type) if url is None else url
            args = []
            value = uno.Enum("com.sun.star.beans.PropertyState", "DIRECT_VALUE")
            args.append(PropertyValue("FilterName", -1, self._getDocumentFilter(document, type), value))
            args.append(PropertyValue("Overwrite", -1, True, value))
            document.storeToURL(url, args)
            return url
        return None

    def _addAttachments(self):
        control = self.dialog.getControl("Attachments")
        for url in self._getSelectedFiles():
            path = uno.fileUrlToSystemPath(url)
            if path not in control.Model.StringItemList:
                control.addItem(path, control.ItemCount)
        self._setAttachments(control.SelectedItemPos)

    def _removeAttachments(self):
        control = self.dialog.getControl("Attachments")
        for i in reversed(control.Model.SelectedItems):
            control.removeItems(i, 1)
        self._setAttachments(control.SelectedItemPos)

    def _viewAttachments(self):
        url = uno.systemPathToFileUrl(self.dialog.getControl("Attachments").SelectedItem)
        self._executeShell(url)

    def _getSelectedFiles(self, path=None):
        path = self._getWorkPath() if path is None else path
        dialog = self.ctx.ServiceManager.createInstance("com.sun.star.ui.dialogs.FilePicker")
        dialog.setDisplayDirectory(path)
        dialog.setMultiSelectionMode(True)
        if dialog.execute():
            return dialog.SelectedFiles
        else:
            return []

    def _getBaseUrl(self, document, extension):
        url = self._getUrl(self._getTempPath()).Main
        template = document.DocumentProperties.TemplateName
        name = template if template else document.Title
        url = "%s/%s.%s" % (url, name, extension)
        return self._getUrl(url).Complete

    def _getDocumentFilter(self, document, type):
        if document.supportsService("com.sun.star.text.TextDocument"):
            filter = {"pdf":"writer_pdf_Export", "html":"XHTML Writer File"}
            return filter[type]
        elif document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
            filter = {"pdf":"calc_pdf_Export", "html":"XHTML Calc File"}
            return filter[type]
        elif document.supportsService("com.sun.star.drawing.DrawingDocument"):
            filter = {"pdf":"draw_pdf_Export", "html":"draw_html_Export"} 
            return filter[type]
        elif document.supportsService("com.sun.star.presentation.PresentationDocument"):
            filter = {"pdf":"impress_pdf_Export", "html":"impress_html_Export"}
            return filter[type]
        elif document.supportsService("com.sun.star.formula.FormulaProperties"):
            filter = {"pdf":"math_pdf_Export", "html":""}
            return filter[type]
        return None

    def _getTempPath(self):
        paths = self.ctx.ServiceManager.createInstance("com.sun.star.util.PathSettings")
        return paths.Temp

    def _getWorkPath(self):
        paths = self.ctx.ServiceManager.createInstance("com.sun.star.util.PathSettings")
        return paths.Work

    def _setDocumentRecord(self, index):
        dispatch = None
        document = self._getDocument()
        frame = document.CurrentController.Frame
        if document.supportsService("com.sun.star.text.TextDocument"):
            url = self._getUrl(".uno:DataSourceBrowser/InsertContent")
            dispatch = frame.queryDispatch(url, "_self", uno.getConstantByName("com.sun.star.frame.FrameSearchFlag.SELF"))
        elif document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
            url = self._getUrl(".uno:DataSourceBrowser/InsertColumns")
            dispatch = frame.queryDispatch(url, "_self", uno.getConstantByName("com.sun.star.frame.FrameSearchFlag.SELF"))
        if dispatch is not None:
            dispatch.dispatch(url, self._getDataDescriptor(index + 1))
        self.index = index

    def _getUrl(self, complete):
        url = URL()
        url.Complete = complete
        dummy, url = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.util.URLTransformer", self.ctx).parseStrict(url)
        return url

    def _getDatabase(self, datasource):
        databases = self.ctx.ServiceManager.createInstance("com.sun.star.sdb.DatabaseContext")
        if databases.hasByName(datasource):
            return databases.getByName(datasource)
        return None

    def _getConnection(self, database):
        if not database.IsPasswordRequired:
            return database.getConnection("","")
        return None

    def _closeConnection(self, connection):
        if connection and not connection.isClosed():
            connection.close()
            connection.dispose()

    def _logMessage(self, name, id, messages=()):
        control = self.dialog.getControl(name)
        message = self._getStringResource().resolveString(id) % messages
        control.Text = "%s%s" % (control.Text, message)

    def _getDataDescriptor(self, row):
        args = []
        value = uno.Enum("com.sun.star.beans.PropertyState", "DIRECT_VALUE")
        args.append(PropertyValue("DataSourceName", -1, self.recipient.ActiveConnection.Parent.Name, value))
        args.append(PropertyValue("ActiveConnection", -1, self.recipient.ActiveConnection, value))
        args.append(PropertyValue("Command", -1, self.query.Name, value))
        args.append(PropertyValue("CommandType", -1, uno.getConstantByName("com.sun.star.sdb.CommandType.QUERY"), value))
        args.append(PropertyValue("Cursor", -1, self.recipient, value))
        args.append(PropertyValue("Selection", -1, [row], value))
        # We use record numbers in "Selection"
        args.append(PropertyValue("BookmarkSelection", -1, False, value))
        return args

    def _getConfiguration(self, nodepath, update=False):
        value = uno.Enum("com.sun.star.beans.PropertyState", "DIRECT_VALUE")
        config = self.ctx.ServiceManager.createInstance("com.sun.star.configuration.ConfigurationProvider")
        service = "com.sun.star.configuration.ConfigurationUpdateAccess" if update else "com.sun.star.configuration.ConfigurationAccess"
        access = config.createInstanceWithArguments(service, (PropertyValue("nodepath", -1, nodepath, value),))
        return access

    def _setDocumentUserProperty(self, property, value):
        document = self._getDocument()
        if document.supportsService("com.sun.star.document.OfficeDocument"):
            properties = document.DocumentProperties.UserDefinedProperties
            if properties.PropertySetInfo.hasPropertyByName(property):
                properties.setPropertyValue(property, value)
            else:
                properties.addProperty(property, \
                uno.getConstantByName("com.sun.star.beans.PropertyAttribute.MAYBEVOID") + \
                uno.getConstantByName("com.sun.star.beans.PropertyAttribute.BOUND") + \
                uno.getConstantByName("com.sun.star.beans.PropertyAttribute.REMOVABLE") + \
                uno.getConstantByName("com.sun.star.beans.PropertyAttribute.MAYBEDEFAULT"), \
                value)

    def _getDocumentUserProperty(self, property, default=None):
        document = self._getDocument()
        if document.supportsService("com.sun.star.document.OfficeDocument"):
            properties = document.DocumentProperties.UserDefinedProperties
            if properties.PropertySetInfo.hasPropertyByName(property):
                return properties.getPropertyValue(property)
            elif default is not None:
                self._setDocumentUserProperty(property, default)
            return default

    def _executeShell(self, url, option=""):
        shell = self.ctx.ServiceManager.createInstance("com.sun.star.system.SystemShellExecute")
        shell.execute(url, option, 0)

    def _setDocumentProperty(self):
        document = self._getDocument()
        if document.supportsService("com.sun.star.document.OfficeDocument"):
            document.DocumentProperties.Subject = self.dialog.getControl("Subject").Text
            document.DocumentProperties.Description =  self.dialog.getControl("Description").Text

    def _getDocumentSubject(self):
        document = self._getDocument()
        if document.supportsService("com.sun.star.document.OfficeDocument"):
            return document.DocumentProperties.Subject

    def _getDocumentDescription(self):
        document = self._getDocument()
        if document.supportsService("com.sun.star.document.OfficeDocument"):
            return  document.DocumentProperties.Description

    def _getUrlContent(self, url):
        dummy = None
        service = self.ctx.ServiceManager.createInstance("com.sun.star.ucb.SimpleFileAccess")
        file = service.openFileRead(url)
        length, content = file.readBytes(dummy, service.getSize(url))
        file.closeInput()
        return uno.ByteSequence(content)

    def _sendMessages(self):
        service = self._getMailService()
        service.connect(self, self)
        if not service.isConnected():
            self._logMessage("TextMerge", "71.Dialog.TextMerge.Text", ("",))
            return
        configuration = self._getConfiguration("/org.openoffice.Office.Writer/MailMergeWizard")
        frm = configuration.getByName("MailAddress")
        subject = self._getDocumentSubject()
        attachments = self._getAttachments()
        self.recipient.beforeFirst()
        while self.recipient.next():
            self._setDocumentRecord(self.recipient.Row -1)
            arguments = (self.recipient.getString(self.columnindex +1), frm, subject, self)
            self._sendMessage(service, arguments, attachments)
        service.disconnect()
 
    def _sendMessage(self, service, arguments, attachments=[]):
        try:
            self.transferable = ["body"]
            mail = self.ctx.ServiceManager.createInstanceWithArgumentsAndContext("com.sun.star.mail.MailMessage", arguments, self.ctx)
            if self._getDocumentUserProperty("SendAsPdf"):
                url = self._saveDocumentAs("pdf")
                self.transferable.append(url)
                mail.addAttachment(self._getAttachment(url))
            for url in attachments:
                self.transferable.append(url)
                mail.addAttachment(self._getAttachment(url))
            service.sendMailMessage(mail)
            self._logMessage("TextMerge", "77.Dialog.TextMerge.Text", (arguments[0],))
        except Exception as e:
            recipients = self._getRecipientFilter(range(self.recipient.Row))
            self._rowRecipientExecute(recipients)
            self._logMessage("TextMerge", "78.Dialog.TextMerge.Text", (arguments[0], e))

    def _getAttachment(self, url):
        attachment = MailAttachment()
        attachment.Data = self
        attachment.ReadableName = uno.fileUrlToSystemPath(self._getUrl(url).Name)
        return attachment

    def _getAttachmentType(self, url):
        detection = self.ctx.ServiceManager.createInstance("com.sun.star.document.TypeDetection")
        type = detection.queryTypeByURL(url)
        if detection.hasByName(type):
            types = detection.getByName(type)
            for type in types:
                if type.Name == "MediaType":
                    return type.Value
        return "application/octet-stream"

    def _getMailService(self, type=None):
        type = uno.Enum("com.sun.star.mail.MailServiceType", "SMTP") if type is None else type
        provider = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.mail.MailServiceProvider", self.ctx)
        return provider.create(type)

    def _getResourceLocation(self):
        identifier = "com.gmail.prrvchr.extensions.gContactOOo"
        provider = self.ctx.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
        return "%s/gContactOOo" % (provider.getPackageLocation(identifier))

    def _getCurrentLocale(self):
        parts = self._getConfiguration("/org.openoffice.Setup/L10N").getByName("ooLocale").split("-")
        locale = Locale(parts[0], "", "")
        if len(parts) == 2:
            locale.Country = parts[1]
        else:
            locale.Country = self._getLanguageCountry(locale)
        return locale

    def _getLanguageCountry(self, locale):
        service = self.ctx.ServiceManager.createInstance("com.sun.star.i18n.LocaleData")
        return service.getLanguageCountryInfo(locale).Country

    def _getStringResource(self):
        service = "com.sun.star.resource.StringResourceWithLocation"
        arguments = (self._getResourceLocation(), True, self._getCurrentLocale(), "DialogStrings", "", self)
        resource = self.ctx.ServiceManager.createInstanceWithArgumentsAndContext(service, arguments, self.ctx)
        return resource


g_ImplementationHelper.addImplementation( \
        PyDialog,                                                              # UNO object class
        g_ImplementationName,                                                  # Implementation name
        ("com.sun.star.lang.XServiceInfo",
        "com.sun.star.task.XJobExecutor",
        "com.sun.star.awt.XDialogEventHandler",
        "com.sun.star.awt.XActionListener",
        "com.sun.star.awt.XItemListener",
        "com.sun.star.sdbc.XRowSetListener",
        "com.sun.star.uno.XCurrentContext",
        "com.sun.star.mail.XAuthenticator",
        "com.sun.star.datatransfer.XTransferable",
        "com.sun.star.task.XInteractionHandler"), )                            # List of implemented services
