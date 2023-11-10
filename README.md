# Documentation

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

- Install ![OAuth2OOo logo][15] **[OAuth2OOo.oxt][16]** extension [![Version][17]][16]

    You must install this extension, if it is not already installed.

- Install ![jdbcDriverOOo logo][18] **[jdbcDriverOOo.oxt][19]** extension [![Version][20]][19]

    You must install this extension, if it is not already installed.

- Install ![gContactOOo logo][21] **[gContactOOo.oxt][22]** extension [![Version][23]][22]

Restart LibreOffice / OpenOffice after installation.

___

## Use:

In LibreOffice / OpenOffice go to File -> Wizards -> Address Data Source...:

![gContactOOo screenshot 1][24]

In step: 1. Address Book Type:
- select: Other external data source
- click on: Next(Button)

![gContactOOo screenshot 2][25]

In step: 2. Connection Settings:
- click on: Settings(Button)

![gContactOOo screenshot 3][26]

In Database type list:
- select: Google Contacts
- click on: Next(Button)

![gContactOOo screenshot 4][27]

In General: Datasource Url:
- put: your Google account (ie: your_account@gmail.com)

Then:
- click on: Test connection (button)

![gContactOOo screenshot 5][28]

After authorizing the [OAuth2OOo][29] application to access your Contacts, normally you should see: Connection Test: The connection was established successfully.

![gContactOOo screenshot 6][30]

Have fun...

___

## Has been tested with:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12 - OpenJDK-11-JRE (amd64)

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 - Adoptium JDK Hotspot 11.0.19 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15  - Adoptium JDK Hotspot 11.0.17 (x64) (under Lubuntu 22.04 / VirtualBox 6.1.38)

* **Does not work with OpenOffice on Windows** see [bug 128569][31]. Having no solution, I encourage you to install **LibreOffice**.

I encourage you in case of problem :confused:  
to create an [issue][9]  
I will try to solve it :smile:

___

## Historical:

### Introduction:

This extension was written in order to make usable in free software (LibreOffice or OpenOffice) your personal data (your address book) stored in your Android phone.

With the [eMailerOOo][32] extension, it can be the data source for [mail merge][33] by email, to your correspondents contained in your phone.

It will give you access to an information system that only larges companies are able, today, to implement.

### What has been done for version 0.0.5:

- Integration and use of the new Hsqldb v2.5.1.

- Writing of a new [Replicator][34] interface, launched in the background (python Thread) responsible for:

    - Perform the necessary procedures when creating a new user (initial Pull).

- Writing of a new [DataBase][35] interface, responsible for making all calls to the database.

- Many other fix...

### What has been done for version 0.0.6:

- Driver has a new name: **Google Contacts**

- Driver is now registred for a new protocol: **sdbc:address:google:your_account@gmail.com**

- The [jdbcDriverOOo][36] extension now provides the driver needed to access the HsqlDB database used by gContactOOo.

- Modifying the [Replicator][34] in order to: 

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
[16]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[17]: <https://img.shields.io/github/downloads/prrvchr/OAuth2OOo/latest/total?label=v1.2.1#right>
[18]: <https://prrvchr.github.io/jdbcDriverOOo/img/jdbcDriverOOo.svg#middle>
[19]: <https://github.com/prrvchr/jdbcDriverOOo/releases/latest/download/jdbcDriverOOo.oxt>
[20]: <https://img.shields.io/github/downloads/prrvchr/jdbcDriverOOo/latest/total?label=v1.0.5#right>
[21]: <img/gContactOOo.svg#middle>
[22]: <https://github.com/prrvchr/gContactOOo/releases/latest/download/gContactOOo.oxt>
[23]: <https://img.shields.io/github/downloads/prrvchr/gContactOOo/latest/total?label=v1.0.3#right>
[24]: <img/gContactOOo-1.png>
[25]: <img/gContactOOo-2.png>
[26]: <img/gContactOOo-3.png>
[27]: <img/gContactOOo-4.png>
[28]: <img/gContactOOo-5.png>
[29]: <https://prrvchr.github.io/OAuth2OOo>
[30]: <img/gContactOOo-6.png>
[31]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[32]: <https://prrvchr.github.io/eMailerOOo>
[33]: <https://en.wikipedia.org/wiki/Mail_merge>
[34]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/replicator.py>
[35]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/database.py>
[36]: <https://prrvchr.github.io/jdbcDriverOOo/>
