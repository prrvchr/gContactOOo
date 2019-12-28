**The use of this software subjects you to our** [Terms Of Use](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/TermsOfUse_en) **and** [Data Protection Policy](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/PrivacyPolicy_en)

## gContactOOo v0.0.3

### Integration of your Google Contacts in LibreOffice / OpenOffice.

### Use:

#### Install [OAuth2OOo](https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt) extention v 0.0.4.

You must install this extention first!!!

Restart LibreOffice / OpenOffice after installation.

#### Install [gContactOOo](https://github.com/prrvchr/gContactOOo/raw/master/gContactOOo.oxt) extention v 0.0.3.

Restart LibreOffice / OpenOffice after installation.

### Requirement:

gContactOOo uses a local Hsqldb database of version 2.5.x.  
The use of Hsqldb requires the installation and configuration within LibreOffice / OpenOffice  
of a **JRE version 1.8 minimum** (ie: Java version 8)

Sometimes it may be necessary for LibreOffice users must have no Hsqldb driver installed with LibreOffice  
(check your Installed Application under Windows or your Packet Manager under Linux)  
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
- select: Google REST API
- click: Next(Button)

![gContactOOo screenshot 4](gContactOOo-4.png)

In General: Datasource Url:
- put: peoples (or people))

In User Authentication: user name:
- put: your Google account (ie: your_account@gmail.com)

![gContactOOo screenshot 5](gContactOOo-5.png)

Go back and normally you can test the connection. It must operate...

![gContactOOo screenshot 6](gContactOOo-6.png)

Have fun...

### Has been tested with:

* LibreOffice 6.3.2.2 - Lubuntu 18.04 -  LxQt 0.12.0.4

I encourage you in case of problem to create an [issue](https://github.com/prrvchr/gContactOOo/issues/new)
I will try to solve it :-)

