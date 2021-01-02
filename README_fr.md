**This [document](https://prrvchr.github.io/gContactOOo) in English.**

**L'utilisation de ce logiciel vous soumet à nos** [**Conditions d'utilisation**](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/TermsOfUse_fr) **et à notre** [**Politique de protection des données**](https://prrvchr.github.io/gContactOOo/gContactOOo/registration/PrivacyPolicy_fr)

# version [0.0.6](https://prrvchr.github.io/gContactOOo/README_fr#historique)

## Introduction:

**gContactOOo** fait partie d'une [Suite](https://prrvchr.github.io/README_fr) d'extensions [LibreOffice](https://fr.libreoffice.org/download/telecharger-libreoffice/) et/ou [OpenOffice](https://www.openoffice.org/fr/Telecharger/) permettant de vous offrir des services inovants dans ces suites bureautique.  
Cette extension vous donne l'acces à vos contacts téléphonique dans LibreOffice / OpenOffice (les contacts de votre téléphone Android).

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source](https://github.com/prrvchr/gContactOOo).
- A apporter des modifications, des corrections, des ameliorations.
- D'ouvrir un [disfonctionnement](https://github.com/prrvchr/gContactOOo/issues/new) si nécessaire.

Bref, à participer au developpement de cette extension.
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

## Prérequis:

gContactOOo utilise une base de données locale HsqlDB version 2.5.1.  
L'utilisation de HsqlDB nécessite l'installation et la configuration dans
LibreOffice / OpenOffice d'un **JRE version 1.8 minimum** (c'est-à-dire: Java version 8)

Parfois, il peut être nécessaire pour les utilisateurs de LibreOffice de ne pas avoir de pilote HsqlDB installé avec LibreOffice  
(vérifiez vos applications installées sous Windows ou votre gestionnaire de paquets sous Linux)  
~~Il semble que les versions 6.4.x et 7.x de LibreOffice aient résolu ce problème et sont capables de fonctionner simultanément avec différentes versions de pilote de HsqlDB.~~  
Après de nombreux tests, il semble que LibreOffice (6.4.x et 7.x) ne puisse pas charger un pilote HsqlDB fourni (hsqldb.jar v2.5.1), si le pilote HsqlDB intégré est installé (et même la solution est parfois de renommer le fichier hsqldb.jar dans /usr/share/java, la désinstallation du paquet libreoffice-sdbc-hsqldb ne semble pas suffisante...)  
Pour surmonter cette limitation et si vous souhaitez utiliser HsqlDB intégré, supprimez le pilote HsqlDB intégré (hsqldb.jar v1.8.0) et installez cette extension: [HsqlDBembeddedOOo](https://prrvchr.github.io/HsqlDBembeddedOOo/) pour remplacer le pilote HsqlDB intégré disfonctionnant de LibreOffice.  
OpenOffice ne semble pas avoir besoin de cette solution de contournement.

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- Installer l'extension [OAuth2OOo.oxt](https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt) version 0.0.5.

Vous devez d'abord installer cette extension, si elle n'est pas déjà installée.

- Installer l'extension [gContactOOo.oxt](https://github.com/prrvchr/gContactOOo/raw/master/gContactOOo.oxt) version 0.0.5.

Redémarrez LibreOffice / OpenOffice après l'installation.

## Utilisation:

Dans LibreOffice / OpenOffice aller à: Fichier -> Assistants -> Source de données des adresses...:

![gContactOOo screenshot 1](gContactOOo-1.png)

À l'étape: 1. Type de carnet d'adresses:
- sélectionner: Autre source de données externes
- cliquez sur: Suivant (bouton)

![gContactOOo screenshot 2](gContactOOo-2.png)

À l'étape: 2. Paramètres de Connexion:
- cliquez sur: Paramètres (bouton)

![gContactOOo screenshot 3](gContactOOo-3.png)

Dans Type de base de données:
- sélectionner: Contacts Google
- cliquez sur: Suivant (bouton)

![gContactOOo screenshot 4](gContactOOo-4.png)

Dans Général: URL de la source de données:
- mettre: votre compte Google (c'est-à-dire: votre_compte@gmail.com)

Puis:
- cliquez sur: Tester la connexion (bouton)

![gContactOOo screenshot 5](gContactOOo-5.png)

Après avoir autorisé l'application [OAuth2OOo](https://prrvchr.github.io/OAuth2OOo/README_fr) à accéder à vos contacts, normalement vous devez voir s'afficher: Test de connexion: Connexion établie.

![gContactOOo screenshot 6](gContactOOo-6.png)

Maintenant à vous d'en profiter...

## A été testé avec:

* LibreOffice 6.4.4.2 - Ubuntu 20.04 -  LxQt 0.14.1

* LibreOffice 7.0.0.0.alpha1 - Ubuntu 20.04 -  LxQt 0.14.1

* OpenOffice 4.1.5 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* OpenOffice 4.2.0.Build:9820 x86_64 - Ubuntu 20.04 - LxQt 0.14.1

* LibreOffice 6.1.5.2 - Raspbian 10 buster - Raspberry Pi 4 Model B

* LibreOffice 6.4.4.2 (x64) - Windows 7 SP1

Je vous encourage en cas de problème :-(  
de créer un [disfonctionnement](https://github.com/prrvchr/gContactOOo/issues/new)  
J'essaierai de le résoudre ;-)

## Historique:

### Ce qui a été fait pour la version 0.0.5:

- Intégration et utilisation de la nouvelle version de Hsqldb 2.5.1.

- Ecriture d'une nouvelle interface [Replicator](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/replicator.py), lancé en arrière-plan (python Thread) responsable de:

    - Effectuer les procédures nécessaires lors de la création d'un nouvel utilisateur (Pull initial).

- Ecriture d'une nouvelle interface [DataBase](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/database.py), responsable de tous les appels à la base de données.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Le pilote a un nouveau nom: **Contacts Google**

- Le pilote est maintenant enregistré pour un nouveau protocole: **sdbc:address:google:votre_compte@gmail.com**

- Beaucoup d'autres correctifs...

### Que reste-t-il à faire pour la version 0.0.6:

- Écriture de l'implémentation des changements Pull et Push dans la nouvelle interface [Replicator](https://github.com/prrvchr/gContactOOo/blob/master/CloudContactOOo/python/cloudcontact/replicator.py)

- Ajouter de nouvelles langue pour l'internationalisation...

- Tout ce qui est bienvenu...
