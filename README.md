# ![gContactOOo logo][1] gContactOOo

**Ce [document][2] en français.**

**The use of this software subjects you to our** [**Terms Of Use**][3] **and** [**Data Protection Policy**][4]

# version [0.0.6][5]

## Introduction:

**gContactOOo** is part of a [Suite][6] of [LibreOffice][7] and/or [OpenOffice][8] extensions allowing to offer you innovative services in these office suites.  
This extension gives you access to your phone contacts in LibreOffice / OpenOffice (the contacts of your Android phone).

Being free software I encourage you:
- To duplicate its [source code][9].
- To make changes, corrections, improvements.
- To open [issue][10] if needed.

In short, to participate in the development of this extension.  
Because it is together that we can make Free Software smarter.

## Requirement:

gContactOOo uses a local [HsqlDB][11] database version 2.7.1.  
HsqlDB being a database written in Java, its use requires the [installation and configuration][12] in LibreOffice / OpenOffice of a **JRE version 11 or later**.  
I recommend [Adoptium][13] as your Java installation source.

If you are using **LibreOffice on Linux**, then you are subject to [bug 139538][14].  
To work around the problem, please uninstall the packages:
- libreoffice-sdbc-hsqldb
- libhsqldb1.8.0-java

If you still want to use the Embedded HsqlDB functionality provided by LibreOffice, then install the [HsqlDBembeddedOOo][15] extension.  
OpenOffice and LibreOffice on Windows are not subject to this malfunction.

## Installation:

It seems important that the file was not renamed when it was downloaded.
If necessary, rename it before installing it.

- Install ![OAuth2OOo logo][16] **[OAuth2OOo.oxt][17]** extension version 0.0.6.

You must install this extension, if it is not already installed.

- Install ![jdbcDriverOOo logo][18] **[jdbcDriverOOo.oxt][19]** extension version 0.0.4.

You must install this extension, if it is not already installed.

- Install ![gContactOOo logo][1] **[gContactOOo.oxt][20]** extension version 0.0.6.

Restart LibreOffice / OpenOffice after installation.

## Use:

In LibreOffice / OpenOffice go to File -> Wizards -> Address Data Source...:

![gContactOOo screenshot 1][21]

In step: 1. Address Book Type:
- select: Other external data source
- click on: Next(Button)

![gContactOOo screenshot 2][22]

In step: 2. Connection Settings:
- click on: Settings(Button)

![gContactOOo screenshot 3][23]

In Database type list:
- select: Google Contacts
- click on: Next(Button)

![gContactOOo screenshot 4][24]

In General: Datasource Url:
- put: your Google account (ie: your_account@gmail.com)

Then:
- click on: Test connection (button)

![gContactOOo screenshot 5][25]

After authorizing the [OAuth2OOo][26] application to access your Contacts, normally you should see: Connection Test: The connection was established successfully.

![gContactOOo screenshot 6][27]

Have fun...

## Has been tested with:

* LibreOffice 6.4.4.2 - Ubuntu 20.04 -  LxQt 0.14.1

* LibreOffice 7.0.0.0.alpha1 - Ubuntu 20.04 -  LxQt 0.14.1

* OpenOffice 4.1.8 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* OpenOffice 4.2.0.Build:9820 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* LibreOffice 6.1.5.2 - Raspbian 10 buster - Raspberry Pi 4 Model B

* LibreOffice 6.4.4.2 (x64) - Windows 7 SP1

I encourage you in case of problem :-(  
to create an [issue][10]  
I will try to solve it ;-)

## Historical:

### Introduction:

This extension was written in order to make usable in free software (LibreOffice or OpenOffice) your personal data (your address book) stored in your Android phone.

With the [smtpMailerOOo][28] extension, it can be the data source for [mail merge][29] by email, to your correspondents contained in your phone.

It will give you access to an information system that only larges companies are able, today, to implement.

### What has been done for version 0.0.5:

- Integration and use of the new Hsqldb v2.5.1.

- Writing of a new [Replicator][30] interface, launched in the background (python Thread) responsible for:

    - Perform the necessary procedures when creating a new user (initial Pull).

- Writing of a new [DataBase][31] interface, responsible for making all calls to the database.

- Many other fix...

### What has been done for version 0.0.6:

- Driver has a new name: **Google Contacts**

- Driver is now registred for a new protocol: **sdbc:address:google:your_account@gmail.com**

- The [jdbcDriverOOo][19] extension now provides the driver needed to access the HsqlDB database used by gContactOOo.

- Modifying the [Replicator][30] in order to: 
    - Open and close the database at each replication.
    - Go on hold after the last closing of the address book.
    - Unload when closing LibreOffice / OpenOffice.

- Possibility to open the local HsqlDB database by: **Tools -> Options -> Internet -> gContactOOo -> View DataBase**

- Many other fix...

### What remains to be done for version 0.0.6:

- Make the address book locally editable with replication of changes.

- Add new languages for internationalization...

- Anything welcome...

[1]: <img/gContactOOo.png>
[2]: <https://prrvchr.github.io/gContactOOo/README_fr>
[3]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/TermsOfUse_en>
[4]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/PrivacyPolicy_en>
[5]: <https://prrvchr.github.io/gContactOOo#historical>
[6]: <https://prrvchr.github.io/>
[7]: <https://www.libreoffice.org/download/download/>
[8]: <https://www.openoffice.org/download/index.html>
[9]: <https://github.com/prrvchr/gContactOOo>
[10]: <https://github.com/prrvchr/gContactOOo/issues/new>
[11]: <http://hsqldb.org/>
[12]: <https://wiki.documentfoundation.org/Documentation/HowTo/Install_the_correct_JRE_-_LibreOffice_on_Windows_10>
[13]: <https://adoptium.net/releases.html?variant=openjdk11>
[14]: <https://bugs.documentfoundation.org/show_bug.cgi?id=139538>
[15]: <https://prrvchr.github.io/HsqlDBembeddedOOo/>
[16]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.png>
[17]: <https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt>
[18]: <https://prrvchr.github.io/jdbcDriverOOo/img/jdbcDriverOOo.png>
[19]: <https://github.com/prrvchr/jdbcDriverOOo/raw/master/source/jdbcDriverOOo/dist/jdbcDriverOOo.oxt>
[20]: <https://github.com/prrvchr/gContactOOo/raw/master/source/gContactOOo/dist/gContactOOo.oxt>
[21]: <img/gContactOOo-1.png>
[22]: <img/gContactOOo-2.png>
[23]: <img/gContactOOo-3.png>
[24]: <img/gContactOOo-4.png>
[25]: <img/gContactOOo-5.png>
[26]: <https://prrvchr.github.io/OAuth2OOo>
[27]: <img/gContactOOo-6.png>
[28]: <https://github.com/prrvchr/smtpMailerOOo/blob/master/source/smtpMailerOOo/dist/smtpMailerOOo.oxt>
[29]: <https://en.wikipedia.org/wiki/Mail_merge>
[30]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/replicator.py>
[31]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/database.py>
