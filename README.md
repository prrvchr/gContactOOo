[**Ce document en français**](https://prrvchr.github.io/gContactOOo/README_fr)

**The use of this software subjects you to our** [**Terms Of Use**](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/TermsOfUse_en) **and** [**Data Protection Policy**](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/PrivacyPolicy_en)

# version [0.0.5](https://prrvchr.github.io/gContactOOo#historical)

## Introduction:

**gContactOOo** is part of a [Suite](https://prrvchr.github.io/) of [LibreOffice](https://www.libreoffice.org/download/download/) and/or [OpenOffice](https://www.openoffice.org/download/index.html) extensions allowing to offer you innovative services in these office suites.  
This extension gives you access to your phone contacts in LibreOffice / OpenOffice (the contacts of your Android phone).

Being free software I encourage you:
- To duplicate its [source code](https://github.com/prrvchr/gContactOOo).
- To make changes, corrections, improvements.
- To open [issue](https://github.com/prrvchr/gContactOOo/issues/new) if needed.

In short, to participate in the development of this extension.
Because it is together that we can make Free Software smarter.

## Requirement:

gContactOOo uses a local Hsqldb database of version 2.5.1.  
The use of Hsqldb requires the installation and configuration within  
LibreOffice / OpenOffice of a **JRE version 1.8 minimum** (ie: Java version 8)

Sometimes it may be necessary for LibreOffice users must have no Hsqldb driver installed with LibreOffice  
(check your Installed Application under Windows or your Packet Manager under Linux)  
It seems that versions 6.4.x and 7.x of LibreOffice have fixed this problem and are able to work with different driver version of Hsqldb simultaneously.  
OpenOffice doesn't seem to need this workaround.

## Installation:

It seems important that the file was not renamed when it was downloaded.
If necessary, rename it before installing it.

- Install [OAuth2OOo.oxt](https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt) extension version 0.0.5.

You must first install this extension, if it is not already installed.

- Install [gContactOOo.oxt](https://github.com/prrvchr/gContactOOo/raw/master/gContactOOo.oxt) extension version 0.0.5.

Restart LibreOffice / OpenOffice after installation.

## Use:

In LibreOffice / OpenOffice go to File -> Wizards -> Address Data Source...:

![gContactOOo screenshot 1](gContactOOo-1.png)

In step: 1. Address Book Type:
- select: Other external data source
- click on: Next(Button)

![gContactOOo screenshot 2](gContactOOo-2.png)

In step: 2. Connection Settings:
- click on: Settings(Button)

![gContactOOo screenshot 3](gContactOOo-3.png)

In Database type list:
- select: Google People API
- click on: Next(Button)

![gContactOOo screenshot 4](gContactOOo-4.png)

In General: Datasource Url:
- put: people

In User Authentication: user name:
- put: your Google account (ie: your_account@gmail.com)

Then:
- click on: Test connection (button)

![gContactOOo screenshot 5](gContactOOo-5.png)

After authorizing the [OAuthOOo](https://prrvchr.github.io/OAuthOOo) application to access your Contacts, normally you should see: Connection Test: The connection was established successfully.

![gContactOOo screenshot 6](gContactOOo-6.png)

Have fun...

## Has been tested with:

* LibreOffice 6.4.4.2 - Ubuntu 20.04 -  LxQt 0.14.1

* LibreOffice 7.0.0.0.alpha1 - Ubuntu 20.04 -  LxQt 0.14.1

* OpenOffice 4.1.5 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* OpenOffice 4.2.0.Build:9820 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* LibreOffice 6.1.5.2 - Raspbian 10 buster - Raspberry Pi 4 Model B

* LibreOffice 6.4.4.2 (x64) - Windows 7 SP1

I encourage you in case of problem :-(  
to create an [issue](https://github.com/prrvchr/gContactOOo/issues/new)  
I will try to solve it ;-)

## Historical:

### What has been done for version 0.0.5:

- Integration and use of the new Hsqldb v2.5.1.

- Writing of a new [Replicator](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/replicator.py) interface, launched in the background (python Thread) responsible for:

    - Perform the necessary procedures when creating a new user (initial Pull).

- Writing of a new [DataBase](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/database.py) interface, responsible for making all calls to the database.

- Many other fix...

### What remains to be done for version 0.0.5:

- Write the implementation Pull Change and Push Change in the new [Replicator](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/replicator.py) interface.

- Add new language for internationalization...

- Anything welcome...
