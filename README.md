[Ce document en français](https://prrvchr.github.io/gContactOOo/README_fr)

**The use of this software subjects you to our** [Terms Of Use](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/TermsOfUse_en) **and** [Data Protection Policy](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/PrivacyPolicy_en)

## gContactOOo v0.0.5

### What has been done for version 0.0.5

- Integration and use of the new Hsqldb v2.5.1.

- Writing of a new [Replicator](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/replicator.py) interface, launched in the background (python Thread) responsible for:

    - Perform the necessary procedures when creating a new user (initial Pull).

- Writing of a new [DataBase](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/database.py) interface, responsible for making all calls to the database.

- Many other fix...

### What remains to be done for version 0.0.5

- Write the implementation Pull Change and Push Change in the new [Replicator](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/replicator.py) interface.

- Add new language for internationalization...

- Anything welcome...

### Integration of your Google Contacts in LibreOffice / OpenOffice.

### Use:

#### Install [OAuth2OOo](https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt) extention v 0.0.5.

You must install this extention first!!!

Restart LibreOffice / OpenOffice after installation.

#### Install [gContactOOo](https://github.com/prrvchr/gContactOOo/raw/master/gContactOOo.oxt) extention v 0.0.5.

Restart LibreOffice / OpenOffice after installation.

### Requirement:

gContactOOo uses a local Hsqldb database of version 2.5.1.  
The use of Hsqldb requires the installation and configuration within  
LibreOffice / OpenOffice of a **JRE version 1.8 minimum** (ie: Java version 8)

Sometimes it may be necessary for LibreOffice users must have no Hsqldb driver installed with LibreOffice  
(check your Installed Application under Windows or your Packet Manager under Linux)  
It seems that version 7.x of LibreOffice has fixed this problem and is able to work with different driver version of Hsqldb simultaneously.  
OpenOffice doesn't seem to need this workaround.

### Configuration:

In LibreOffice / OpenOffice go to File -> Wizards -> Address Data Source...:

![gContactOOo screenshot 1](gContactOOo-1.png)

In step: 1. Address Book Type:
- select: Other external data source
- click: Next(Button)

![gContactOOo screenshot 2](gContactOOo-2.png)

In step: 2. Connection Settings:
- click: Settings(Button)

![gContactOOo screenshot 3](gContactOOo-3.png)

In Database type list:
- select: Google People API
- click: Next(Button)

![gContactOOo screenshot 4](gContactOOo-4.png)

In General: Datasource Url:
- put: people

In User Authentication: user name:
- put: your Google account (ie: your_account@gmail.com)

![gContactOOo screenshot 5](gContactOOo-5.png)

Go back and normally you can test the connection. It must operate...

![gContactOOo screenshot 6](gContactOOo-6.png)

Have fun...

### Has been tested with:

* LibreOffice 6.4.4.2 - Ubuntu 20.04 -  LxQt 0.14.1

* LibreOffice 7.0.0.0.alpha1 - Ubuntu 20.04 -  LxQt 0.14.1

* OpenOffice 4.1.5 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* OpenOffice 4.2.0.Build:9820 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* LibreOffice 6.1.5.2 - Raspbian 10 buster - Raspberry Pi 4 Model B

* LibreOffice 6.4.4.2 (x64) - Windows 7 SP1

I encourage you in case of problem :-(  
to create an [issue](https://github.com/prrvchr/gContactOOo/issues/new)  
I will try to solve it ;-)

