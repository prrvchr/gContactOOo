# ![gContactOOo logo][1] gContactOOo

**This [document][2] in English.**

**L'utilisation de ce logiciel vous soumet à nos** [**Conditions d'utilisation**][3] **et à notre** [**Politique de protection des données**][4]

# version [1.0.0][5]

## Introduction:

**gContactOOo** fait partie d'une [Suite][6] d'extensions [LibreOffice][7] ~~et/ou [OpenOffice][8]~~ permettant de vous offrir des services inovants dans ces suites bureautique.  
Cette extension vous donne l'acces à vos contacts téléphonique dans LibreOffice / OpenOffice (les contacts de votre téléphone Android).

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][9].
- A apporter des modifications, des corrections, des améliorations.
- D'ouvrir un [dysfonctionnement][10] si nécessaire.

Bref, à participer au developpement de cette extension.  
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

## Prérequis:

Afin de profiter des dernières versions des bibliothèques Python utilisées dans gContactOOo, la version 2 de Python a été abandonnée au profit de **Python 3.8 minimum**.  
Cela signifie que **gContactOOo ne supporte plus OpenOffice et LibreOffice 6.x sous Windows depuis sa version 1.0.0**.
Je ne peux que vous conseiller **de migrer vers LibreOffice 7.x**.

gContactOOo utilise une base de données locale [HsqlDB][12] version 2.7.1.  
HsqlDB étant une base de données écrite en Java, son utilisation nécessite [l'installation et la configuration][13] dans LibreOffice / OpenOffice d'un **JRE version 11 ou ultérieure**.  
Je vous recommande [Adoptium][14] comme source d'installation de Java.

Si vous utilisez **LibreOffice sous Linux**, vous êtes sujet au [dysfonctionnement 139538][15]. Pour contourner le problème, veuillez **désinstaller les paquets** avec les commandes:
- `sudo apt remove libreoffice-sdbc-hsqldb` (pour désinstaller le paquet libreoffice-sdbc-hsqldb)
- `sudo apt remove libhsqldb1.8.0-java` (pour désinstaller le paquet libhsqldb1.8.0-java)

Si vous souhaitez quand même utiliser la fonctionnalité HsqlDB intégré fournie par LibreOffice, alors installez l'extension [HsqlDBembeddedOOo][16].  

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- Installer l'extension ![OAuth2OOo logo][17] **[OAuth2OOo.oxt][18]** version 1.1.0.

Vous devez installer cette extension, si elle n'est pas déjà installée.

- Installer l'extension ![jdbcDriverOOo logo][19] **[jdbcDriverOOo.oxt][20]** version 0.0.4.

Vous devez installer cette extension, si elle n'est pas déjà installée.

- Installer l'extension ![gContactOOo logo][1] **[gContactOOo.oxt][21]** version 1.0.0.

Redémarrez LibreOffice / OpenOffice après l'installation.

## Utilisation:

Dans LibreOffice / OpenOffice aller à: Fichier -> Assistants -> Source de données des adresses...:

![gContactOOo screenshot 1][22]

À l'étape: 1. Type de carnet d'adresses:
- sélectionner: Autre source de données externes
- cliquez sur: Suivant (bouton)

![gContactOOo screenshot 2][23]

À l'étape: 2. Paramètres de Connexion:
- cliquez sur: Paramètres (bouton)

![gContactOOo screenshot 3][24]

Dans Type de base de données:
- sélectionner: Contacts Google
- cliquez sur: Suivant (bouton)

![gContactOOo screenshot 4][25]

Dans Général: URL de la source de données:
- mettre: votre compte Google (c'est-à-dire: votre_compte@gmail.com)

Puis:
- cliquez sur: Tester la connexion (bouton)

![gContactOOo screenshot 5][26]

Après avoir autorisé l'application [OAuth2OOo][27] à accéder à vos contacts, normalement vous devez voir s'afficher: Test de connexion: Connexion établie.

![gContactOOo screenshot 6][28]

Maintenant à vous d'en profiter...

## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12 - OpenJDK-11-JRE (amd64)

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 - Adoptium JDK Hotspot 11.0.19 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15  - Adoptium JDK Hotspot 11.0.17 (x64) (under Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice sous Windows** voir [dysfonctionnement 128569][11]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :-(  
de créer un [dysfonctionnement][10]  
J'essaierai de le résoudre ;-)

## Historique:

### Introduction:

Cette extension a été écrite afin de rendre utilisables dans un logiciel libre (LibreOffice ou OpenOffice) vos données personnelles (votre carnet d'adresses) stockées dans votre téléphone Android.

Avec l'extension [smtpMailerOOo][29], elle peut être la source de données pour des [publipostages][30] par courriel (email), à vos correspondants contenus dans votre téléphone.

Elle vous donnera accès à un système d'information que seules les grandes entreprises sont capables, aujourd'hui, de mettre en œuvre.

### Ce qui a été fait pour la version 0.0.5:

- Intégration et utilisation de la nouvelle version de Hsqldb 2.5.1.

- Ecriture d'une nouvelle interface [Replicator][31], lancé en arrière-plan (python Thread) responsable de:

    - Effectuer les procédures nécessaires lors de la création d'un nouvel utilisateur (Pull initial).

- Ecriture d'une nouvelle interface [DataBase][32], responsable de tous les appels à la base de données.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Le pilote a un nouveau nom: **Contacts Google**

- Le pilote est maintenant enregistré pour un nouveau protocole: **sdbc:address:google:votre_compte@gmail.com**

- L'extension [jdbcDriverOOo][20] fournit désormais le pilote nécessaire pour accéder à la base de données HsqlDB utilisée par gContactOOo.

- Modification du [Replicator][31] afin de:
    - Ouvrir et fermer la base de données à chaque réplication.
    - Se mettre en attente après la dernière fermeture du carnet d'adresses.
    - Se décharger lors de la fermeture de LibreOffice / OpenOffice.

- Possibilité d'ouvrir la base de données HsqlDB locale par: **Outils -> Options -> Internet -> gContactOOo -> Voir la base de données**

- Beaucoup d'autres correctifs...

### Que reste-t-il à faire pour la version 0.0.6:

- Rendre le carnet d'adresses modifiable localement avec la réplication des modifications.

- Ajouter de nouvelles langues pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: <img/gContactOOo.png>
[2]: <https://prrvchr.github.io/gContactOOo>
[3]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/TermsOfUse_fr>
[4]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/PrivacyPolicy_fr>
[5]: <https://prrvchr.github.io/gContactOOo#historical>
[6]: <https://prrvchr.github.io/README_fr>
[7]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[8]: <https://www.openoffice.org/fr/Telecharger/>
[9]: <https://github.com/prrvchr/gContactOOo>
[10]: <https://github.com/prrvchr/gContactOOo/issues/new>
[11]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[12]: <http://hsqldb.org/>
[13]: <https://wiki.documentfoundation.org/Documentation/HowTo/Install_the_correct_JRE_-_LibreOffice_on_Windows_10/fr>
[14]: <https://adoptium.net/releases.html?variant=openjdk11>
[15]: <https://bugs.documentfoundation.org/show_bug.cgi?id=139538>
[16]: <https://prrvchr.github.io/HsqlDBembeddedOOo/README_fr>
[17]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.png>
[18]: <https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt>
[19]: <https://prrvchr.github.io/jdbcDriverOOo/img/jdbcDriverOOo.png>
[20]: <https://github.com/prrvchr/jdbcDriverOOo/raw/master/source/jdbcDriverOOo/dist/jdbcDriverOOo.oxt>
[21]: <https://github.com/prrvchr/gContactOOo/raw/master/source/gContactOOo/dist/gContactOOo.oxt>
[22]: <img/gContactOOo-1.png>
[23]: <img/gContactOOo-2.png>
[24]: <img/gContactOOo-3.png>
[25]: <img/gContactOOo-4.png>
[26]: <img/gContactOOo-5.png>
[27]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[28]: <img/gContactOOo-6.png>
[29]: <https://github.com/prrvchr/smtpMailerOOo/blob/master/source/smtpMailerOOo/dist/smtpMailerOOo.oxt>
[30]: <https://en.wikipedia.org/wiki/Mail_merge>
[31]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/replicator.py>
[32]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/database.py>
