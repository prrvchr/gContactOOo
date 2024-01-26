<!--
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
-->
# [![gContactOOo logo][1]][2] Documentation

**Ce [document][3] en français.**

**The use of this software subjects you to our [Terms Of Use][4] and [Data Protection Policy][5].**

# version [1.1.1][6]

## Introduction:

**gContactOOo** is part of a [Suite][7] of [LibreOffice][8] ~~and/or [OpenOffice][9]~~ extensions allowing to offer you innovative services in these office suites.

This extension gives you access, in LibreOffice, to your phone contacts (the contacts of your Android phone).  
It uses [Google People API][10] to synchronize your remote Google Contacts into a local HsqlDB 2.7.2 database.  
This extension is seen by LibreOffice as a [database driver][11] responding to the URL: `sdbc:address:google:*`.

Being free software I encourage you:
- To duplicate its [source code][12].
- To make changes, corrections, improvements.
- To open [issue][13] if needed.

In short, to participate in the development of this extension.  
Because it is together that we can make Free Software smarter.

___

## Requirement:

The gContactOOo extension uses the OAuth2OOo extension to work.  
It must therefore meet the [requirement of the OAuth2OOo extension][14].

The gContactOOo extension uses the jdbcDriverOOo extension to work.  
It must therefore meet the [requirement of the jdbcDriverOOo extension][15].

**On Linux and macOS the Python packages** used by the extension, if already installed, may come from the system and therefore **may not be up to date**.  
To ensure that your Python packages are up to date it is recommended to use the **System Info** option in the extension Options accessible by:  
**Tools -> Options -> Internet -> gContactOOo -> View log -> System Info**  
If outdated packages appear, you can update them with the command:  
`pip install --upgrade <package-name>`

For more information see: [What has been done for version 1.1.0][16].

___

## Installation:

It seems important that the file was not renamed when it was downloaded.
If necessary, rename it before installing it.

- [![OAuth2OOo logo][17]][18] Install **[OAuth2OOo.oxt][19]** extension [![Version][20]][19]

    You must install this extension, if it is not already installed.

- [![jdbcDriverOOo logo][21]][22] Install **[jdbcDriverOOo.oxt][23]** extension [![Version][24]][23]

    You must install this extension, if it is not already installed.

- ![gContactOOo logo][25] Install **[gContactOOo.oxt][26]** extension [![Version][27]][26]

Restart LibreOffice after installation.  
**Be careful, restarting LibreOffice may not be enough.**
- **On Windows** to ensure that LibreOffice restarts correctly, use Windows Task Manager to verify that no LibreOffice services are visible after LibreOffice shuts down (and kill it if so).
- **Under Linux or macOS** you can also ensure that LibreOffice restarts correctly, by launching it from a terminal with the command `soffice` and using the key combination `Ctrl + C` if after stopping LibreOffice, the terminal is not active (no command prompt).

___

## Use:

In LibreOffice / OpenOffice go to: **File -> Wizards -> Address Data Source...**

![gContactOOo screenshot 1][28]

The **Address Book Datasource Wizard** open.

In step: **1.Address Book Type**:
- Select: **Other external data source**.
- Click button: **Next**.

![gContactOOo screenshot 2][29]

In step: **2.Connection Settings**:
- Click button: **Settings**.

![gContactOOo screenshot 3][30]

A new wizard opens. **Data source properties**.

In step: **1.Advanced Properties**.  
In Database type list:
- Select: **Google Contacts**.
- Click button: **Next**.

![gContactOOo screenshot 4][31]

In step: **2.Connection Settings**.  
In General: Enter the DBMS/driver-specific connection string here.
- Put your Google account (ie: your_account@gmail.com)
- Click button: **Test connection**.

![gContactOOo screenshot 5][32]

After authorizing the [OAuth2OOo][18] application to access your Contacts, normally you should see: Connection Test: The connection was established successfully.

![gContactOOo screenshot 6][33]

If the connection has been established, you can complete this wizard with the **Finish** button.

![gContactOOo screenshot 7][34]

In step: **3.Table Selection**.  
If your data source has multiple tables, you will be asked to select the primary table.  
In this case select the table: **All my contacts**. If necessary and before any connection it is possible to rename the main table name in: **Tools -> Options -> Internet -> gContactOOo -> Main table name**.

In step: **4.Field Assignment**.  
If necessary it is possible to rename the names of the columns of the data source using the button: **Field Assignment**.  
Please continue this wizard with the button: **Next**.

![gContactOOo screenshot 8][35]

In step: **5.Data Source Title**.

You must create an odb file. To do this you must:
- **Uncheck the box**: Embed this address book definition in the current document.
- Named the odb file in the field: **Location**.

This odb file must also be made accessible. To do this you must:
- **Check the box**: Make this address book available to all modules in LibreOffice
- Named the address book in the field: **Address book name**.

![gContactOOo screenshot 9][36]

Have fun...

___

## Has been tested with:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12 - OpenJDK-11-JRE (amd64)

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 - Adoptium JDK Hotspot 11.0.19 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15  - Adoptium JDK Hotspot 11.0.17 (x64) (under Lubuntu 22.04 / VirtualBox 6.1.38)

* **Does not work with OpenOffice on Windows** see [bug 128569][37]. Having no solution, I encourage you to install **LibreOffice**.

I encourage you in case of problem :confused:  
to create an [issue][13]  
I will try to solve it :smile:

___

## Historical:

### Introduction:

This extension was written in order to make usable in free software (LibreOffice or OpenOffice) your personal data (your address book) stored in your Android phone.

With the [eMailerOOo][38] extension, it can be the data source for [mail merge][39] by email, to your correspondents contained in your phone.

It will give you access to an information system that only larges companies are able, today, to implement.

### What has been done for version 0.0.5:

- Integration and use of the new Hsqldb v2.5.1.

- Writing of a new [Replicator][40] interface, launched in the background (python Thread) responsible for:

    - Perform the necessary procedures when creating a new user (initial Pull).

- Writing of a new [DataBase][41] interface, responsible for making all calls to the database.

- Many other fix...

### What has been done for version 0.0.6:

- Driver has a new name: **Google Contacts**

- Driver is now registred for a new protocol: **sdbc:address:google:your_account@gmail.com**

- The [jdbcDriverOOo][22] extension now provides the driver needed to access the HsqlDB database used by gContactOOo.

- Modifying the [Replicator][40] in order to: 

    - Open and close the database at each replication.
    - Go on hold after the last closing of the address book.
    - Unload when closing LibreOffice / OpenOffice.

- Possibility to open the local HsqlDB database by: **Tools -> Options -> Internet -> gContactOOo -> View DataBase**

- Many other fix...

### What has been done for version 1.0.1:

- The absence or obsolescence of the **OAuth2OOo** and/or **jdbcDriverOOo** extensions necessary for the proper functioning of **gContactOOo** now displays an error message.

- Many other things...

### What has been done for version 1.0.2:

- Support for version **1.2.0** of the **OAuth2OOo** extension. Previous versions will not work with **OAuth2OOo** extension 1.2.0 or higher.

### What has been done for version 1.0.3:

- Support for version **1.2.1** of the **OAuth2OOo** extension. Previous versions will not work with **OAuth2OOo** extension 1.2.1 or higher.

### What has been done for version 1.1.0:

- All Python packages necessary for the extension are now recorded in a [requirements.txt][42] file following [PEP 508][43].
- Now if you are not on Windows then the Python packages necessary for the extension can be easily installed with the command:  
  `pip install requirements.txt`
- Modification of the [Requirement][44] section.

### What has been done for version 1.1.1:

- Using Python package `dateutil` to convert timestamp strings to UNO DateTime.
- Many other fixes...

### What remains to be done for version 1.1.1:

- Make the address book locally editable with replication of changes.

- Add new languages for internationalization...

- Anything welcome...

[1]: </img/contact.svg#collapse>
[2]: <https://prrvchr.github.io/gContactOOo/>
[3]: <https://prrvchr.github.io/gContactOOo/README_fr>
[4]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/TermsOfUse_en>
[5]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/PrivacyPolicy_en>
[6]: <https://prrvchr.github.io/gContactOOo#historical>
[7]: <https://prrvchr.github.io/>
[8]: <https://www.libreoffice.org/download/download/>
[9]: <https://www.openoffice.org/download/index.html>
[10]: <https://developers.google.com/people?hl=en>
[11]: <https://wiki.openoffice.org/wiki/Documentation/DevGuide/Database/Driver_Service>
[12]: <https://github.com/prrvchr/gContactOOo>
[13]: <https://github.com/prrvchr/gContactOOo/issues/new>
[14]: <https://prrvchr.github.io/OAuth2OOo/#requirement>
[15]: <https://prrvchr.github.io/jdbcDriverOOo/#requirement>
[16]: <https://prrvchr.github.io/gContactOOo/#what-has-been-done-for-version-110>
[17]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[18]: <https://prrvchr.github.io/OAuth2OOo>
[19]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[20]: <https://img.shields.io/github/v/tag/prrvchr/OAuth2OOo?label=latest#right>
[21]: <https://prrvchr.github.io/jdbcDriverOOo/img/jdbcDriverOOo.svg#middle>
[22]: <https://prrvchr.github.io/jdbcDriverOOo/>
[23]: <https://github.com/prrvchr/jdbcDriverOOo/releases/latest/download/jdbcDriverOOo.oxt>
[24]: <https://img.shields.io/github/v/tag/prrvchr/jdbcDriverOOo?label=latest#right>
[25]: <img/gContactOOo.svg#middle>
[26]: <https://github.com/prrvchr/gContactOOo/releases/latest/download/gContactOOo.oxt>
[27]: <https://img.shields.io/github/downloads/prrvchr/gContactOOo/latest/total?label=v1.1.1#right>
[28]: <img/gContactOOo-1.png>
[29]: <img/gContactOOo-2.png>
[30]: <img/gContactOOo-3.png>
[31]: <img/gContactOOo-4.png>
[32]: <img/gContactOOo-5.png>
[33]: <img/gContactOOo-6.png>
[34]: <img/gContactOOo-7.png>
[35]: <img/gContactOOo-8.png>
[36]: <img/gContactOOo-9.png>
[37]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[38]: <https://prrvchr.github.io/eMailerOOo>
[39]: <https://en.wikipedia.org/wiki/Mail_merge>
[40]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/replicator.py>
[41]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/database.py>
[42]: <https://github.com/prrvchr/gContactOOo/tree/master/source/gContactOOo/requirements.txt>
[43]: <https://peps.python.org/pep-0508/>
[44]: <https://prrvchr.github.io/gContactOOo/#requirement>
