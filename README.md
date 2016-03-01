# GContactOOo
Google Contact to OpenOffice to Pdf Mail merge

Requirement:


GMail https://myaccount.google.com/security?utm_source=OGB#connectedapps

  enable less secured application. Needed but apparently the connection is under SSL...


Mozilla Thunderbird 38.5.1 or higher: www.mozilla.org/thunderbird/
  You need gContactSync 2.0.10, you can install in the Thunderbird extention manager.


Libre Office 5.0.5 or higher: www.libreoffice.org/download/libreoffice-fresh/

  You need the ORB (Oracle Report Builder) and may be, must be installed separately... (like this on Lubuntu...)

  You need to copy this file: mailmerge.py to /usr/lib/libreoffice/program (on Linux)
  or C:\Programmes\LibreOffice 5\program (on Windows).
  Make backup copy of your file but it's necessary for connecting at GMail!!! No SSL without...
  (After an OOo update you need to apply this procedure again!!!) 

  In Writer -> Tools -> Options -> LibreOffice Writer -> MailMerge:
  put your Name, your email address, server name (ie: smtp.gmail.com), port (465) and enable SSL
  In Server Authentication put your email address again and your password.
  Go back and normally you can test the connection. It must operate...
  
  In Writer -> Tools -> AddressBook Source -> AddressBook Source(Button) -> Thunderbird/icedove -> Next(Button) -> CollectedAddressBook -> Next(Button):
  Give a name to your AddressBook (ie: Addresses) and -> Finish(Button)
  
  In Writer -> Tools -> Options -> LibreOffice Base -> Database:
  Register GContactOOo.odb with the same name as the file (ie: GContactOOo).
  Check the presence of the AddressBook (ie:Addresses) 

Load GContactOOo.odt chose the conresponding database to your AddressBook (ie:Addresses)
Change the path of template file (ie:model.odt) with the directory where it is located...
and have fun...
