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
# [![gContactOOo logo][0]][-1] Documentation

**Ce [document][1] en français.**

**The use of this software subjects you to our [Terms Of Use][2] and [Data Protection Policy][3].**

# version [1.0.3][4]

## Introduction:

**gContactOOo** is part of a [Suite][5] of [LibreOffice][6] ~~and/or [OpenOffice][7]~~ extensions allowing to offer you innovative services in these office suites.  
This extension gives you access, in LibreOffice, to your phone contacts (the contacts of your Android phone).

Being free software I encourage you:
- To duplicate its [source code][8].
- To make changes, corrections, improvements.
- To open [issue][9] if needed.

In short, to participate in the development of this extension.  
Because it is together that we can make Free Software smarter.

___

## Requirement:

In order to take advantage of the latest versions of the Python libraries used in gContactOOo, version 2 of Python has been abandoned in favor of **Python 3.8 minimum**.  
This means that **gContactOOo no longer supports OpenOffice and LibreOffice 6.x on Windows since version 1.0.0**.
I can only advise you **to migrate to LibreOffice 7.x**.

gContactOOo uses a local [HsqlDB][10] database version 2.7.2.  
HsqlDB being a database written in Java, its use requires the [installation and configuration][11] in LibreOffice / OpenOffice of a **JRE version 11 or later**.  
I recommend [Adoptium][12] as your Java installation source.

If you are using **LibreOffice on Linux**, you are subject to [bug 139538][13]. To work around the problem, please **uninstall the packages** with commands:
- `sudo apt remove libreoffice-sdbc-hsqldb` (to uninstall the libreoffice-sdbc-hsqldb package)
- `sudo apt remove libhsqldb1.8.0-java` (to uninstall the libhsqldb1.8.0-java package)

If you still want to use the Embedded HsqlDB functionality provided by LibreOffice, then install the [HyperSQLOOo][14] extension.

___

## Installation:

It seems important that the file was not renamed when it was downloaded.
If necessary, rename it before installing it.

- [![OAuth2OOo logo][15]][16] Install **[OAuth2OOo.oxt][17]** extension [![Version][18]][17]

    You must install this extension, if it is not already installed.

- [![jdbcDriverOOo logo][19]][20] Install **[jdbcDriverOOo.oxt][21]** extension [![Version][22]][21]

    You must install this extension, if it is not already installed.

- ![gContactOOo logo][23] Install **[gContactOOo.oxt][24]** extension [![Version][25]][24]

Restart LibreOffice / OpenOffice after installation.

___

## Use:

In LibreOffice / OpenOffice go to: **File -> Wizards -> Address Data Source...**

![gContactOOo screenshot 1][26]

In step: 1. Address Book Type:
- select: Other external data source
- click on: Next(Button)

![gContactOOo screenshot 2][27]

In step: 2. Connection Settings:
- click on: Settings(Button)

![gContactOOo screenshot 3][28]

In Database type list:
- select: Google Contacts
- click on: Next(Button)

![gContactOOo screenshot 4][29]

In General: Datasource Url:
- put: your Google account (ie: your_account@gmail.com)

Then:
- click on: Test connection (button)

![gContactOOo screenshot 5][30]

After authorizing the [OAuth2OOo][16] application to access your Contacts, normally you should see: Connection Test: The connection was established successfully.

![gContactOOo screenshot 6][31]

If the connection has been established, you can complete this wizard with the Finish button

![gContactOOo screenshot 7][32]

If your data source has multiple tables, you will be asked to select the primary table.  
In this case select the table: **All my contacts**.

If necessary it is possible to rename the names of the columns of the data source using the button: **Field Assignment**.  
Please continue this wizard with the button: Next

![gContactOOo screenshot 8][33]

You must create an odb file. To do this you must:
- **Uncheck the box**: Embed this address book definition in the current document.
- Named the odb file in the field: **Location**.

This odb file must also be made accessible. To do this you must:
- **Check the box**: Make this address book available to all modules in LibreOffice
- Named the address book in the field: **Address book name**.

![gContactOOo screenshot 9][34]

Have fun...

___

## Has been tested with:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12 - OpenJDK-11-JRE (amd64)

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 - Adoptium JDK Hotspot 11.0.19 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15  - Adoptium JDK Hotspot 11.0.17 (x64) (under Lubuntu 22.04 / VirtualBox 6.1.38)

* **Does not work with OpenOffice on Windows** see [bug 128569][32]. Having no solution, I encourage you to install **LibreOffice**.

I encourage you in case of problem :confused:  
to create an [issue][9]  
I will try to solve it :smile:

___

## Historical:

### Introduction:

This extension was written in order to make usable in free software (LibreOffice or OpenOffice) your personal data (your address book) stored in your Android phone.

With the [eMailerOOo][33] extension, it can be the data source for [mail merge][34] by email, to your correspondents contained in your phone.

It will give you access to an information system that only larges companies are able, today, to implement.

### What has been done for version 0.0.5:

- Integration and use of the new Hsqldb v2.5.1.

- Writing of a new [Replicator][35] interface, launched in the background (python Thread) responsible for:

    - Perform the necessary procedures when creating a new user (initial Pull).

- Writing of a new [DataBase][36] interface, responsible for making all calls to the database.

- Many other fix...

### What has been done for version 0.0.6:

- Driver has a new name: **Google Contacts**

- Driver is now registred for a new protocol: **sdbc:address:google:your_account@gmail.com**

- The [jdbcDriverOOo][20] extension now provides the driver needed to access the HsqlDB database used by gContactOOo.

- Modifying the [Replicator][35] in order to: 

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

### What remains to be done for version 1.0.3:

- Make the address book locally editable with replication of changes.

- Add new languages for internationalization...

- Anything welcome...

[0]: </img/contact.svg#collapse>
[-1]: <https://prrvchr.github.io/gContactOOo/>
[1]: <https://prrvchr.github.io/gContactOOo/README_fr>
[2]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/TermsOfUse_en>
[3]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/PrivacyPolicy_en>
[4]: <https://prrvchr.github.io/gContactOOo#historical>
[5]: <https://prrvchr.github.io/>
[6]: <https://www.libreoffice.org/download/download/>
[7]: <https://www.openoffice.org/download/index.html>
[8]: <https://github.com/prrvchr/gContactOOo>
[9]: <https://github.com/prrvchr/gContactOOo/issues/new>
[10]: <http://hsqldb.org/>
[11]: <https://wiki.documentfoundation.org/Documentation/HowTo/Install_the_correct_JRE_-_LibreOffice_on_Windows_10>
[12]: <https://adoptium.net/releases.html?variant=openjdk11>
[13]: <https://bugs.documentfoundation.org/show_bug.cgi?id=139538>
[14]: <https://prrvchr.github.io/HyperSQLOOo/>
[15]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[16]: <https://prrvchr.github.io/OAuth2OOo>
[17]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[18]: <https://img.shields.io/github/v/tag/prrvchr/OAuth2OOo?label=latest#right>
[19]: <https://prrvchr.github.io/jdbcDriverOOo/img/jdbcDriverOOo.svg#middle>
[20]: <https://prrvchr.github.io/jdbcDriverOOo/>
[21]: <https://github.com/prrvchr/jdbcDriverOOo/releases/latest/download/jdbcDriverOOo.oxt>
[22]: <https://img.shields.io/github/v/tag/prrvchr/jdbcDriverOOo?label=latest#right>
[23]: <img/gContactOOo.svg#middle>
[24]: <https://github.com/prrvchr/gContactOOo/releases/latest/download/gContactOOo.oxt>
[25]: <https://img.shields.io/github/downloads/prrvchr/gContactOOo/latest/total?label=v1.0.3#right>
[26]: <img/gContactOOo-1.png>
[27]: <img/gContactOOo-2.png>
[28]: <img/gContactOOo-3.png>
[29]: <img/gContactOOo-4.png>
[30]: <img/gContactOOo-5.png>
[31]: <img/gContactOOo-6.png>
[32]: <img/gContactOOo-7.png>
[33]: <img/gContactOOo-8.png>
[34]: <img/gContactOOo-9.png>
[35]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[36]: <https://prrvchr.github.io/eMailerOOo>
[37]: <https://en.wikipedia.org/wiki/Mail_merge>
[38]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/replicator.py>
[39]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/database.py>
