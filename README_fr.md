<!--
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-25 https://prrvchr.github.io                                  ║
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
# Documentation

**This [document][3] in english.**

**L'utilisation de ce logiciel vous soumet à nos [Conditions d'Utilisation][4] et à notre [Politique de Protection des Données][5].**

# version [1.4.0][6]

## Introduction:

**gContactOOo** fait partie d'une [Suite][7] d'extensions [LibreOffice][8] ~~et/ou [OpenOffice][9]~~ permettant de vous offrir des services inovants dans ces suites bureautique.

Cette extension vous donne l'accès, dans LibreOffice, à vos contacts Google (les contacts de votre téléphone Android).  
Elle utilise [l'API Google People][10] pour synchroniser vos Contacts Google distant dans une base de données locale HsqlDB 2.7.4.  
Cette extension est vu par LibreOffice comme un [pilote de base de données][11] répondant à l'URL: `sdbc:address:google:*`.

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][12].
- A apporter des modifications, des corrections, des améliorations.
- D'ouvrir un [dysfonctionnement][13] si nécessaire.
- De [participer au frais][14] de la [certification CASA][15].

Bref, à participer au developpement de cette extension.  
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

___

## Certification CASA:

Afin de garantir l'interopérabilité avec **Google**, l'extension **gContactOOo** utilise l'extension **OAuth2OOo** qui nécessite la [certification CASA][15].  
Jusqu'à présent, cette certification était gratuite et réalisée par un partenaire de Google.  
L'application **OAuth2OOo** a obtenu sa [certification CASA][16] le 28/11/2023.

**Maintenant cette certification est devenue désormais payante et coûte 600$.**

Je n'avais jamais anticipé de tels frais et je compte sur votre contribution pour financer cette certification.

Merci pour votre aide. [![Sponsor][17]][14]

___

## Prérequis:

L'extension gContactOOo utilise l'extension OAuth2OOo pour fonctionner.  
Elle doit donc répondre aux [prérequis de l'extension OAuth2OOo][18].

L'extension gContactOOo utilise l'extension jdbcDriverOOo pour fonctionner.  
Elle doit donc répondre aux [prérequis de l'extension jdbcDriverOOo][19].  
De plus, gContactOOo nécessite que l'extension jdbcDriverOOo soit configurée pour fournir `com.sun.star.sdb` comme niveau d'API, qui est la configuration par défaut.

___

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- [![OAuth2OOo logo][20]][21] Installer l'extension **[OAuth2OOo.oxt][22]** [![Version][23]][22]

    Vous devez installer cette extension, si elle n'est pas déjà installée.

- [![jdbcDriverOOo logo][24]][25] Installer l'extension **[jdbcDriverOOo.oxt][26]** [![Version][27]][26]

    Vous devez installer cette extension, si elle n'est pas déjà installée.

- ![gContactOOo logo][28] Installer l'extension **[gContactOOo.oxt][29]** [![Version][30]][29]

Redémarrez LibreOffice après l'installation.  
**Attention, redémarrer LibreOffice peut ne pas suffire.**
- **Sous Windows** pour vous assurer que LibreOffice redémarre correctement, utilisez le Gestionnaire de tâche de Windows pour vérifier qu'aucun service LibreOffice n'est visible après l'arrêt de LibreOffice (et tuez-le si ç'est le cas).
- **Sous Linux ou macOS** vous pouvez également vous assurer que LibreOffice redémarre correctement, en le lançant depuis un terminal avec la commande `soffice` et en utilisant la combinaison de touches `Ctrl + C` si après l'arrêt de LibreOffice, le terminal n'est pas actif (pas d'invité de commande).

Après avoir redémarré LibreOffice, vous pouvez vous assurer que l'extension et son pilote sont correctement installés en vérifiant que le pilote `io.github.prrvchr.gContactOOo.Driver` est répertorié dans le **Pool de Connexions**, accessible via le menu: **Outils -> Options -> LibreOffice Base -> Connexions**. Il n'est pas nécessaire d'activer le pool de connexions.

Si le pilote n'est pas répertorié, la raison de l'échec du chargement du pilote peut être trouvée dans la journalisation de l'extension. Cette journalisation est accessible via le menu: **Outils -> Options -> LibreOffice Base -> Contacts Google -> Options de journalisation**.  
La journalisation `gContactLog` doit d'abord être activée, puis LibreOffice redémarré pour obtenir le message d'erreur dans le journal.

___

## Utilisation:

Dans LibreOffice / OpenOffice aller à: **Fichier -> Assistants -> Source de données des adresses...**

![gContactOOo screenshot 1][31]

L'**Assistant source de données du carnet d'adresses** s'ouvre.

À l'étape: **1.Type de carnet d'adresses**:
- Sélectionner: **Autre source de données externes**.
- Cliquez sur le bouton: **Suivant**.

![gContactOOo screenshot 2][32]

À l'étape: **2.Paramètres de Connexion**:
- Cliquez sur le bouton: **Paramètres**.

![gContactOOo screenshot 3][33]

Un nouvel assistant s'ouvre. **Propriétés de la source de données**.

A l'étape: **1.Propriétés avancées**.  
Dans Type de base de données:
- Sélectionner: **Contacts Google**.
- Cliquez sur le bouton: **Suivant**.

![gContactOOo screenshot 4][34]

A l'étape: **2.Paramètres de connexion**.  
Dans Général: Entrer ici la chaîne de connexion spécifique au SGDB / pilote.
- Mettre votre compte Google (ie: votre_compte@gmail.com)
- Cliquez sur le bouton: **Tester la connexion**.

![gContactOOo screenshot 5][35]

Après avoir autorisé l'application [OAuth2OOo][21] à accéder à vos contacts, normalement vous devez voir s'afficher: Test de connexion: Connexion établie.

![gContactOOo screenshot 6][36]

Si la connexion a été etablie, vous pouvez terminer cet assistant avec le bouton **Terminer**.

![gContactOOo screenshot 7][37]

A l'étape: **3.Sélection de table**.  
Si votre source de données comporte plusieurs tables, il vous sera demandé de sélectionner la table principale.  
Dans ce cas sélectionnez la table: **Tous mes contacts**. Si nécessaire et avant toute connexion il est possible de renommer le nom de la table principale dans: **Outils -> Options -> Internet -> gContactOOo -> Nom de la table principale**.

A l'étape: **4.Assignation de champ**.  
Si nécessaire il est possible de renommer les noms des colonnes de la source de données à l'aide du bouton: **Assignation de champ**.  
Veuillez poursuivre cet assistant par le bouton: **Suivant**.

![gContactOOo screenshot 8][38]

A l'étape: **5.Titre de la source de données**.

Il faut créer un fichier odb. Pour cela vous devez:
- **Décocher la case**: Intégrer cette définition du carnet d'adresses dans le document actuel.
- Nommer le fichier odb dans le champ: **Emplacement**.

Il faut également rendre accessible ce fichier odb. Pour cela vous devez:
- **Cocher la case**: Rendre ce carnet d'adresses accessible à tous les modules de LibreOffice
- Nommer le carnet d'adresses dans le champ: **Nom du carnet d'adresses**.

![gContactOOo screenshot 9][39]

Maintenant à vous d'en profiter...

___

## Comment créer l'extension:

Normalement, l'extension est créée avec Eclipse pour Java et [LOEclipse][40]. Pour contourner Eclipse, j'ai modifié LOEclipse afin de permettre la création de l'extension avec Apache Ant.  
Pour créer l'extension gContactOOo avec l'aide d'Apache Ant, vous devez:
- Installer le [SDK Java][41] version 8 ou supérieure.
- Installer [Apache Ant][42] version 1.10.0 ou supérieure.
- Installer [LibreOffice et son SDK][43] version 7.x ou supérieure.
- Cloner le dépôt [gContactOOo][44] sur GitHub dans un dossier.
- Depuis ce dossier, accédez au répertoire: `source/gContactOOo/`
- Dans ce répertoire, modifiez le fichier `build.properties` afin que les propriétés `office.install.dir` et `sdk.dir` pointent vers les dossiers d'installation de LibreOffice et de son SDK, respectivement.
- Lancez la création de l'archive avec la commande: `ant`
- Vous trouverez l'archive générée dans le sous-dossier: `dist/`

___

## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12 - OpenJDK-11-JRE (amd64)

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 - Adoptium JDK Hotspot 11.0.19 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15  - Adoptium JDK Hotspot 11.0.17 (x64) (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 24.8.0.3 (X86_64) - Windows 10(x64) - Python version 3.9.19 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice sous Windows** voir [dysfonctionnement 128569][45]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][13]  
J'essaierai de le résoudre :smile:

___

## Historique:

### Introduction:

Cette extension a été écrite afin de rendre utilisables dans un logiciel libre (LibreOffice ou OpenOffice) vos données personnelles (votre carnet d'adresses) stockées dans votre téléphone Android.

Avec l'extension [eMailerOOo][46], elle peut être la source de données pour des [publipostages][47] par courriel (email), à vos correspondants contenus dans votre téléphone.

Elle vous donnera accès à un système d'information que seules les grandes entreprises sont capables, aujourd'hui, de mettre en œuvre.

### Ce qui a été fait pour la version 0.0.5:

- Intégration et utilisation de la nouvelle version de Hsqldb 2.5.1.

- Ecriture d'une nouvelle interface [Replicator][48], lancé en arrière-plan (python Thread) responsable de:

    - Effectuer les procédures nécessaires lors de la création d'un nouvel utilisateur (Pull initial).

- Ecriture d'une nouvelle interface [DataBase][49], responsable de tous les appels à la base de données.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Le pilote a un nouveau nom: **Contacts Google**

- Le pilote est maintenant enregistré pour un nouveau protocole: **sdbc:address:google:votre_compte@gmail.com**

- L'extension [jdbcDriverOOo][26] fournit désormais le pilote nécessaire pour accéder à la base de données HsqlDB utilisée par gContactOOo.

- Modification du [Replicator][48] afin de:

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

### Ce qui a été fait pour la version 1.1.0:

- Tous les paquets Python nécessaires à l'extension sont désormais enregistrés dans un fichier [requirements.txt][50] suivant la [PEP 508][51].
- Désormais si vous n'êtes pas sous Windows alors les paquets Python nécessaires à l'extension peuvent être facilement installés avec la commande:  
  `pip install requirements.txt`
- Modification de la section [Prérequis][52].

### Ce qui a été fait pour la version 1.1.1:

- Utilisation du package Python `dateutil` pour convertir les chaînes d'horodatage en UNO DateTime.
- De nombreuses autres corrections...

### Ce qui a été fait pour la version 1.1.2:

- Intégration d'un correctif pour contourner le [dysfonctionnement #159988][53].

### Ce qui a été fait pour la version 1.1.3:

- La création de la base de données, lors de la première connexion, utilise l'API UNO proposée par l'extension jdbcDriverOOo depuis la version 1.3.2. Cela permet d'enregistrer toutes les informations nécessaires à la création de la base de données dans 9 tables texte qui sont en fait [9 fichiers csv][54].
- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.4 et 1.3.2 minimum.
- De nombreuses corrections.

### Ce qui a été fait pour la version 1.1.4:

- Mise à jour du paquet [Python python-dateutil][55] vers la version 2.9.0.post0.
- Mise à jour du paquet [Python decorator][56] vers la version 5.1.1.
- Mise à jour du paquet [Python ijson][57] vers la version 3.3.0.
- Mise à jour du paquet [Python packaging][58] vers la version 24.1.
- Mise à jour du paquet [Python setuptools][59] vers la version 72.1.0 afin de répondre à l'[alerte de sécurité Dependabot][60].
- Mise à jour du paquet [Python validators][61] vers la version 0.33.0.
- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.6 et 1.4.2 minimum.

### Ce qui a été fait pour la version 1.1.5:

- Mise à jour du paquet [Python setuptools][59] vers la version 73.0.1.
- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.7 et 1.4.5 minimum.
- Les modifications apportées aux options de l'extension, qui nécessitent un redémarrage de LibreOffice, entraîneront l'affichage d'un message.
- Support de LibreOffice version 24.8.x.

### Ce qui a été fait pour la version 1.1.6:

- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.8 et 1.4.6 minimum.
- Modification des options de l'extension accessibles via : **Outils -> Options... -> Internet -> gContactOOo** afin de respecter la nouvelle charte graphique.

### Ce qui a été fait pour la version 1.2.0:

- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.4.0 et 1.4.6 minimum.
- Il est possible de construire l'archive de l'extension (ie: le fichier oxt) avec l'utilitaire [Apache Ant][62] et le fichier script [build.xml][63].
- L'extension refusera de s'installer sous OpenOffice quelle que soit la version ou LibreOffice autre que 7.x ou supérieur.
- Ajout des fichiers binaires nécessaires aux bibliothèques Python pour fonctionner sous Linux et LibreOffice 24.8 (ie: Python 3.9).

### Ce qui a été fait pour la version 1.2.1:

- Mise à jour du paquet [Python packaging][58] vers la version 24.2.
- Mise à jour du paquet [Python setuptools][59] vers la version 75.8.0.
- Mise à jour du paquet [Python six][64] vers la version 1.17.0.
- Mise à jour du paquet [Python validators][61] vers la version 0.34.0.
- Support de Python version 3.13.

### Ce qui a été fait pour la version 1.3.0:

- Mise à jour du paquet [Python packaging][58] vers la version 25.0.
- Rétrogradage du paquet [Python setuptools][59] vers la version 75.3.2, afin d'assurer la prise en charge de Python 3.8.
- Déploiement de l'enregistrement passif permettant une installation beaucoup plus rapide des extensions et de différencier les services UNO enregistrés de ceux fournis par une implémentation Java ou Python. Cet enregistrement passif est assuré par l'extension [LOEclipse][40] via les [PR#152][65] et [PR#157][66].
- Modification de [LOEclipse][40] pour prendre en charge le nouveau format de fichier `rdb` produit par l'utilitaire de compilation `unoidl-write`. Les fichiers `idl` ont été mis à jour pour prendre en charge les deux outils de compilation disponibles: idlc et unoidl-write.
- Il est désormais possible de créer le fichier oxt de l'extension gContactOOo uniquement avec Apache Ant et une copie du dépôt GitHub. La section [Comment créer l'extension][67] a été ajoutée à la documentation.
- Implémentation de [PEP 570][68] dans la [journalisation][69] pour prendre en charge les arguments multiples uniques.
- Toute erreur survenant lors du chargement du pilote sera consignée dans le journal de l'extension si la journalisation a été préalablement activé. Cela facilite l'identification des problèmes d'installation sous Windows.
- Pour garantir la création correcte de la base de données gContactOOo, il sera vérifié que l'extension jdbcDriverOOo a `com.sun.star.sdb` comme niveau d'API.
- Nécessite l'extension **jdbcDriverOOo en version 1.5.0 minimum**.
- Nécessite l'extension **OAuth2OOo en version 1.5.0 minimum**.

### Ce qui a été fait pour la version 1.3.1:

- Support de LibreOffice 25.2.x et 25.8.x sous Windows 64 bits.
- Nécessite l'extension **jdbcDriverOOo en version 1.5.4 minimum**.
- Nécessite l'extension **OAuth2OOo en version 1.5.2 minimum**.

### Ce qui a été fait pour la version 1.4.0:

- Si l'extension jdbcDriverOOo fonctionne sans l'instrumentation Java, un message d'avertissement s'affichera dans les options de l'extension.
- Nécessite l'extension **jdbcDriverOOo en version 1.6.0 minimum**.
- Nécessite l'extension **OAuth2OOo en version 1.6.0 minimum**.
- A été testé sous LibreOfficeDev 26.2.

### Que reste-t-il à faire pour la version 1.4.0:

- Rendre le carnet d'adresses modifiable localement avec la réplication des modifications.

- Ajouter de nouvelles langues pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: </img/contact.svg#collapse>
[2]: <https://prrvchr.github.io/gContactOOo/>
[3]: <https://prrvchr.github.io/gContactOOo>
[4]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/TermsOfUse_fr>
[5]: <https://prrvchr.github.io/gContactOOo/source/gContactOOo/registration/PrivacyPolicy_fr>
[6]: <https://prrvchr.github.io/gContactOOo/README_fr#ce-qui-a-%C3%A9t%C3%A9-fait-pour-la-version-140>
[7]: <https://prrvchr.github.io/README_fr>
[8]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[9]: <https://www.openoffice.org/fr/Telecharger/>
[10]: <https://developers.google.com/people?hl=fr>
[11]: <https://wiki.openoffice.org/wiki/Documentation/DevGuide/Database/Driver_Service>
[12]: <https://github.com/prrvchr/gContactOOo>
[13]: <https://github.com/prrvchr/gContactOOo/issues/new>
[14]: <https://github.com/sponsors/prrvchr>
[15]: <https://appdefensealliance.dev/casa>
[16]: <https://github.com/prrvchr/OAuth2OOo/blob/master/LOV_OAuth2OOo.pdf>
[17]: <https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86#right>
[18]: <https://prrvchr.github.io/OAuth2OOo/README_fr#pr%C3%A9requis>
[19]: <https://prrvchr.github.io/jdbcDriverOOo/README_fr#pr%C3%A9requis>
[20]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[21]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[22]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[23]: <https://img.shields.io/github/v/tag/prrvchr/OAuth2OOo?label=latest#right>
[24]: <https://prrvchr.github.io/jdbcDriverOOo/img/jdbcDriverOOo.svg#middle>
[25]: <https://prrvchr.github.io/jdbcDriverOOo/README_fr>
[26]: <https://github.com/prrvchr/jdbcDriverOOo/releases/latest/download/jdbcDriverOOo.oxt>
[27]: <https://img.shields.io/github/v/tag/prrvchr/jdbcDriverOOo?label=latest#right>
[28]: <img/gContactOOo.svg#middle>
[29]: <https://github.com/prrvchr/gContactOOo/releases/latest/download/gContactOOo.oxt>
[30]: <https://img.shields.io/github/downloads/prrvchr/gContactOOo/latest/total?label=v1.4.0#right>
[31]: <img/gContactOOo-1_fr.png>
[32]: <img/gContactOOo-2_fr.png>
[33]: <img/gContactOOo-3_fr.png>
[34]: <img/gContactOOo-4_fr.png>
[35]: <img/gContactOOo-5_fr.png>
[36]: <img/gContactOOo-6_fr.png>
[37]: <img/gContactOOo-7_fr.png>
[38]: <img/gContactOOo-8_fr.png>
[39]: <img/gContactOOo-9_fr.png>
[40]: <https://github.com/LibreOffice/loeclipse>
[41]: <https://adoptium.net/temurin/releases/?version=8&package=jdk>
[42]: <https://ant.apache.org/manual/install.html>
[43]: <https://downloadarchive.documentfoundation.org/libreoffice/old/7.6.7.2/>
[44]: <https://github.com/prrvchr/gContactOOo.git>
[45]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[46]: <https://prrvchr.github.io/eMailerOOo/README_fr>
[47]: <https://en.wikipedia.org/wiki/Mail_merge>
[48]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/replicator.py>
[49]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/addressbook/database.py>
[50]: <https://github.com/prrvchr/gContactOOo/releases/latest/download/requirements.txt>
[51]: <https://peps.python.org/pep-0508/>
[52]: <https://prrvchr.github.io/gContactOOo/README_fr#pr%C3%A9requis>
[53]: <https://bugs.documentfoundation.org/show_bug.cgi?id=159988>
[54]: <https://github.com/prrvchr/gContactOOo/tree/main/source/gContactOOo/hsqldb>
[55]: <https://pypi.org/project/python-dateutil/>
[56]: <https://pypi.org/project/decorator/>
[57]: <https://pypi.org/project/ijson/>
[58]: <https://pypi.org/project/packaging/>
[59]: <https://pypi.org/project/setuptools/>
[60]: <https://github.com/prrvchr/gContactOOo/security/dependabot/1>
[61]: <https://pypi.org/project/validators/>
[62]: <https://ant.apache.org/>
[63]: <https://github.com/prrvchr/gContactOOo/blob/master/source/gContactOOo/build.xml>
[64]: <https://pypi.org/project/six/>
[65]: <https://github.com/LibreOffice/loeclipse/pull/152>
[66]: <https://github.com/LibreOffice/loeclipse/pull/157>
[67]: <https://prrvchr.github.io/gContactOOo/README_fr#comment-cr%C3%A9er-lextension>
[68]: <https://peps.python.org/pep-0570/>
[69]: <https://github.com/prrvchr/gContactOOo/blob/master/uno/lib/uno/logger/logwrapper.py#L109>
