# KERI Blockchain-Anchored IT/OT Security Gateway

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un système de démonstration pour sécuriser les données IoT industrielles (OT) en utilisant **KERI (Key Event Receipt Infrastructure)**. Ce projet établit une "Chaîne de Confiance" vérifiable cryptographiquement entre la génération de données de capteurs et l'ancrage blockchain, comblant efficacement le fossé IT-OT.

## 🎯 Vue d'ensemble

Ce système démontre comment :
- Attribuer des identités décentralisées (AIDs) à plusieurs capteurs de drones
- Signer cryptographiquement chaque charge utile de données
- Stocker les événements signés dans un Journal d'Événements KERI (KEL) partagé
- Vérifier l'intégrité des données en utilisant des liens cryptographiques
- Ancrer les hachages d'événements dans un registre blockchain (simulé)

## 🏗️ Architecture du Système

Le projet se compose de trois capteurs de drones indépendants et d'un système de vérification :

### 1. **Capteurs de Drones (Couche OT)**
- **Trois capteurs de drones indépendants** : `drone_sensor_1`, `drone_sensor_2`, `drone_sensor_3`
- Chaque capteur maintient sa propre identité KERI (AID)
- Tous les capteurs partagent une base de données LMDB unifiée (`keri_drones_db`)
- Les données sont isolées par AID dans la base de données partagée
- Chaque capteur signe les charges utiles de données et les commet dans le KEL
- Génère des fichiers d'ancrage pour la vérification

### 2. **Pont Blockchain (Couche Blockchain)**
- Surveille les fichiers d'ancrage pour les nouveaux événements signés
- Extrait les résumés cryptographiques (SAID)
- Soumet les résumés à un Smart Contract (simulé) pour l'immuabilité

### 3. **Vérificateur KEL (Couche IT/Audit)**
- Agit en tant qu'auditeur externe
- Accède directement à la base de données KERI partagée
- Vérifie les liens cryptographiques entre les événements
- Affiche les chaînes d'événements pour tous les capteurs avec isolation des données par AID

## 🔑 Fonctionnalités Principales

- ✅ **Support Multi-Capteurs** : Trois capteurs de drones indépendants
- ✅ **Base de Données Unifiée** : Base de données LMDB partagée avec isolation des données basée sur AID
- ✅ **Fonctionnement Indépendant** : Chaque capteur peut fonctionner indépendamment
- ✅ **Identités Persistantes** : Les capteurs maintiennent leur AID après redémarrage
- ✅ **Vérification Cryptographique** : Vérification complète de la chaîne d'événements KERI
- ✅ **Multi-Plateforme** : Fonctionne sur Windows, Linux et macOS

## 📋 Prérequis

- **Python 3.10+**
- **libsodium** (Requis pour la cryptographie KERI)
  - Windows : Inclus dans le dépôt
  - Linux : `sudo apt-get install libsodium-dev` (Ubuntu/Debian) ou `sudo yum install libsodium-devel` (RHEL/CentOS)
  - macOS : `brew install libsodium`

## 🚀 Installation

### 1. Cloner le Dépôt

```bash
git clone https://github.com/YourUsername/KERI-Blockchain-Anchored-IT-OT.git
cd KERI-Blockchain-Anchored-IT-OT
```

### 2. Créer un Environnement Virtuel

**Windows :**
```powershell
python -m venv keri-env
.\keri-env\Scripts\activate
```

**Linux/macOS :**
```bash
python3 -m venv keri-env
source keri-env/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

> **Note** : Le projet utilise `keripy` qui doit être installé depuis GitHub. Ceci est géré automatiquement par `requirements.txt`.

## 💻 Utilisation

### Exécution des Capteurs

Chaque capteur peut être exécuté indépendamment dans des fenêtres de terminal séparées :

#### Terminal 1 : Capteur de Drone 1
```bash
# Windows
.\keri-env\Scripts\python.exe scripts\drone_sensor_1.py

# Linux/macOS
python scripts/drone_sensor_1.py
```

#### Terminal 2 : Capteur de Drone 2
```bash
# Windows
.\keri-env\Scripts\python.exe scripts\drone_sensor_2.py

# Linux/macOS
python scripts/drone_sensor_2.py
```

#### Terminal 3 : Capteur de Drone 3
```bash
# Windows
.\keri-env\Scripts\python.exe scripts\drone_sensor_3.py

# Linux/macOS
python scripts/drone_sensor_3.py
```

**Ce qui se passe :**
- Chaque capteur crée ou charge son identité KERI (AID)
- Les capteurs génèrent des charges utiles de données toutes les 3 secondes
- Les données sont signées et commises dans la base de données KERI partagée
- Des fichiers d'ancrage sont créés/mis à jour : `blockchain_anchor_drone_sensor_1.json`, etc.
- Des fichiers de chemin de base de données sont créés : `current_db_path_drone_sensor_1.txt`, etc.

**Pour arrêter un capteur :** Appuyez sur `Ctrl+C`

### Exécution du Vérificateur

Exécutez le vérificateur pour vérifier l'intégrité des données de tous les capteurs :

```bash
# Windows
.\keri-env\Scripts\python.exe scripts\03_kel_verifier.py

# Linux/macOS
python scripts/03_kel_verifier.py
```

**Ce qui se passe :**
- Ouvre la base de données partagée (`keri_drones_db`)
- Lit les fichiers d'ancrage pour tous les capteurs disponibles
- Vérifie la chaîne d'événements de chaque capteur
- Affiche un tableau des événements pour chaque capteur (isolé par AID)
- Affiche un résumé de vérification


### Gestion des Identités
- Chaque capteur a un **Identificateur Autonome KERI (AID)** unique
- Les AIDs sont générés en utilisant la bibliothèque `keripy`
- Les identités persistent après les redémarrages des capteurs
- L'isolation des données est réalisée par des requêtes basées sur AID

### Base de Données
- **Stockage** : LMDB (Lightning Memory-Mapped Database)
- **Architecture** : Base de données partagée unique (`keri_drones_db`)
- **Isolation** : Données séparées par AID (les événements de chaque capteur sont isolés)
- **Persistance** : La base de données persiste après l'arrêt du capteur

### Sérialisation
- **Interne** : Sérialisation native KERI pour la signature
- **Externe** : JSON pour les fichiers d'ancrage et la configuration
- **Événements** : Stockés au format événement KERI avec liens cryptographiques

### Vérification
- Vérifie les liens cryptographiques (Numéro de Séquence et SAID)
- Assure que l'historique des événements ne peut pas être falsifié
- Vérifie tous les événements de la chaîne pour chaque capteur
- Affiche l'historique complet des événements avec les données de charge utile

## 📝 Fichiers Générés

### Fichiers dAncrage
- `blockchain_anchor_drone_sensor_1.json`
- `blockchain_anchor_drone_sensor_2.json`
- `blockchain_anchor_drone_sensor_3.json`


### Fichiers de Chemin de Base de Données
- `current_db_path_drone_sensor_1.txt`
- `current_db_path_drone_sensor_2.txt`
- `current_db_path_drone_sensor_3.txt`

Chaque fichier contient le chemin vers la base de données partagée : `keri_drones_db`




## ⚠️ Notes Importantes

### Persistance de la Base de Données
- La base de données (`keri_drones_db`) persiste après l'arrêt du capteur
- Les capteurs chargeront les identités existantes au redémarrage
- Pour recommencer à zéro, supprimez le répertoire `keri_drones_db`

### Indépendance des Capteurs
- Les capteurs peuvent fonctionner indépendamment (un, deux ou les trois)
- Chaque capteur maintient sa propre identité et son propre compteur de cycles
- Le vérificateur vérifiera uniquement les capteurs qui ont généré des fichiers d'ancrage

### Compatibilité Windows
- Inclut `libsodium.dll` dans `keri-env/Scripts/`
- Les scripts configurent automatiquement les chemins DLL sur Windows
- Aucune configuration supplémentaire nécessaire


