# Documentation

**This [document][1] in English.**

**L'utilisation de ce logiciel vous soumet à nos [Conditions d'utilisation][2] et à notre [Politique de protection des données][3].**

# version [1.0.3][4]

## Introduction:

**gContactOOo** fait partie d'une [Suite][5] d'extensions [LibreOffice][6] ~~et/ou [OpenOffice][7]~~ permettant de vous offrir des services inovants dans ces suites bureautique.  
Cette extension vous donne l'accès, dans LibreOffice, à vos contacts Google (les contacts de votre téléphone Android).

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][8].
- A apporter des modifications, des corrections, des améliorations.
- D'ouvrir un [dysfonctionnement][9] si nécessaire.

Bref, à participer au developpement de cette extension.  
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

___

## Prérequis:

Afin de profiter des dernières versions des bibliothèques Python utilisées dans gContactOOo, la version 2 de Python a été abandonnée au profit de **Python 3.8 minimum**.  
Cela signifie que **gContactOOo ne supporte plus OpenOffice et LibreOffice 6.x sous Windows depuis sa version 1.0.0**.
Je ne peux que vous conseiller **de migrer vers LibreOffice 7.x**.

gContactOOo utilise une base de données locale [HsqlDB][10] version 2.7.2.  
HsqlDB étant une base de données écrite en Java, son utilisation nécessite [l'installation et la configuration][11] dans LibreOffice / OpenOffice d'un **JRE version 11 ou ultérieure**.  
Je vous recommande [Adoptium][12] comme source d'installation de Java.

Si vous utilisez **LibreOffice sous Linux**, vous êtes sujet au [dysfonctionnement 139538][13]. Pour contourner le problème, veuillez **désinstaller les paquets** avec les commandes:
- `sudo apt remove libreoffice-sdbc-hsqldb` (pour désinstaller le paquet libreoffice-sdbc-hsqldb)
- `sudo apt remove libhsqldb1.8.0-java` (pour désinstaller le paquet libhsqldb1.8.0-java)

Si vous souhaitez quand même utiliser la fonctionnalité HsqlDB intégré fournie par LibreOffice, alors installez l'extension [HyperSQLOOo][14].

___

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- Installer l'extension ![OAuth2OOo logo][15] **[OAuth2OOo.oxt][16]** [![Version][17]][16]

    Vous devez installer cette extension, si elle n'est pas déjà installée.

- Installer l'extension ![jdbcDriverOOo logo][18] **[jdbcDriverOOo.oxt][19]** [![Version][20]][19]

    Vous devez installer cette extension, si elle n'est pas déjà installée.

- Installer l'extension ![gContactOOo logo][21] **[gContactOOo.oxt][22]** [![Version][23]][22]

Redémarrez LibreOffice / OpenOffice après l'installation.

___

## Utilisation:

Dans LibreOffice / OpenOffice aller à: Fichier -> Assistants -> Source de données des adresses...:

![gContactOOo screenshot 1][24]

À l'étape: 1. Type de carnet d'adresses:
- sélectionner: Autre source de données externes
- cliquez sur: Suivant (bouton)

![gContactOOo screenshot 2][25]

À l'étape: 2. Paramètres de Connexion:
- cliquez sur: Paramètres (bouton)

![gContactOOo screenshot 3][26]

Dans Type de base de données:
- sélectionner: Contacts Google
- cliquez sur: Suivant (bouton)

![gContactOOo screenshot 4][27]

Dans Général: URL de la source de données:
- mettre: votre compte Google (c'est-à-dire: votre_compte@gmail.com)

Puis:
- cliquez sur: Tester la connexion (bouton)

![gContactOOo screenshot 5][28]

Après avoir autorisé l'application [OAuth2OOo][29] à accéder à vos contacts, normalement vous devez voir s'afficher: Test de connexion: Connexion établie.

![gContactOOo screenshot 6][30]

Maintenant à vous d'en profiter...

___

## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12 - OpenJDK-11-JRE (amd64)

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 - Adoptium JDK Hotspot 11.0.19 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15  - Adoptium JDK Hotspot 11.0.17 (x64) (under Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice sous Windows** voir [dysfonctionnement 128569][31]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][9]  
J'essaierai de le résoudre :smile:

___

## Historique:

### Introduction:

Cette extension a été écrite afin de rendre utilisables dans un logiciel libre (LibreOffice ou OpenOffice) vos données personnelles (votre carnet d'adresses) stockées dans votre téléphone Android.

Avec l'extension [eMailerOOo][32], elle peut être la source de données pour des [publipostages][33] par courriel (email), à vos correspondants contenus dans votre téléphone.

Elle vous donnera accès à un système d'information que seules les grandes entreprises sont capables, aujourd'hui, de mettre en œuvre.

### Ce qui a été fait pour la version 0.0.5:

- Intégration et utilisation de la nouvelle version de Hsqldb 2.5.1.

- Ecriture d'une nouvelle interface [Replicator][34], lancé en arrière-plan (python Thread) responsable de:

    - Effectuer les procédures nécessaires lors de la création d'un nouvel utilisateur (Pull initial).

- Ecriture d'une nouvelle interface [DataBase][35], responsable de tous les appels à la base de données.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Le pilote a un nouveau nom: **Contacts Google**

- Le pilote est maintenant enregistré pour un nouveau protocole: **sdbc:address:google:votre_compte@gmail.com**

- L'extension [jdbcDriverOOo][36] fournit désormais le pilote nécessaire pour accéder à la base de données HsqlDB utilisée par gContactOOo.

- Modification du [Replicator][34] afin de:

    - Ouvrir et fermer la base de données à chaque réplication.
    - Se mettre en attente après la dernière fermeture du carnet d'adresses.
    - Se décharger lors de la fermeture de LibreOffice / OpenOffice.

- Possibilité d'ouvrir la base de données HsqlDB locale par: **Outils -> Options -> Internet -> gContactOOo -> Voir la base de données**

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 1.0.1:

- L'absence ou l'obsolescence des extensions **OAuth2OOo** et/ou **jdbcDriverOOo** nécessaires au bon fonctionnement de **gContactOOo** affiche désormais un message d'erreur.

- Encore plein d'autres choses...

### Ce qui a été fait pour la version 1.0.2:

- Prise en charge de la version 1.2.0 de l'extension **OAuth2OOo**. Les versions précédentes ne fonctionneront pas avec l'extension **OAuth2OOo** 1.2.0 ou ultérieure.

### Ce qui a été fait pour la version 1.0.3:

- Prise en charge de la version 1.2.1 de l'extension **OAuth2OOo**. Les versions précédentes ne fonctionneront pas avec l'extension **OAuth2OOo** 1.2.1 ou ultérieure.

### Que reste-t-il à faire pour la version 1.0.3:

- Rendre le carnet d'adresses modifiable localement avec la réplication des modifications.

- Ajouter de nouvelles langues pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: <https://prrvchr.github.io/gContactOOo>
[2]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/TermsOfUse_fr>
[3]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/PrivacyPolicy_fr>
[4]: <https://prrvchr.github.io/gContactOOo/README_fr#historique>
[5]: <https://prrvchr.github.io/README_fr>
[6]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[7]: <https://www.openoffice.org/fr/Telecharger/>
[8]: <https://github.com/prrvchr/gContactOOo>
[9]: <https://github.com/prrvchr/gContactOOo/issues/new>
[10]: <http://hsqldb.org/>
[11]: <https://wiki.documentfoundation.org/Documentation/HowTo/Install_the_correct_JRE_-_LibreOffice_on_Windows_10/fr>
[12]: <https://adoptium.net/releases.html?variant=openjdk11>
[13]: <https://bugs.documentfoundation.org/show_bug.cgi?id=139538>
[14]: <https://prrvchr.github.io/HyperSQLOOo/README_fr>
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
[29]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[30]: <img/gContactOOo-6.png>
[31]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[32]: <https://prrvchr.github.io/eMailerOOo/README_fr>
[33]: <https://en.wikipedia.org/wiki/Mail_merge>
[34]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/replicator.py>
[35]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/database.py>
[36]: <https://prrvchr.github.io/jdbcDriverOOo/README_fr>
