# Documentation des Modifications - KERI Multi-Sensor System

## 📋 Vue d'ensemble

Ce document explique les modifications apportées aux scripts `01_anchor_generator.py` et `03_kel_verifier.py` pour supporter un système multi-capteurs (3 capteurs indépendants).

---

## 🔧 Modifications du Générateur (`01_anchor_generator.py`)

### Objectif

Transformer le générateur d'un système à **un seul capteur** vers un système à **trois capteurs indépendants** fonctionnant en parallèle.

### Changements Principaux

#### 1. **Architecture Multi-Threading**

Le générateur utilise maintenant le module `threading` pour exécuter chaque capteur dans un thread séparé :

```python
import threading
```

**Avant** : Un seul capteur dans le thread principal  
**Maintenant** : Trois capteurs, chacun dans son propre thread

#### 2. **Configuration des Capteurs**

```python
SENSORS = [
    {"name": "drone_sensor", "sector_prefix": "DRONE"},
    {"name": "plc_sensor", "sector_prefix": "PLC"},
    {"name": "iot_sensor", "sector_prefix": "IOT"}
]
```

Chaque capteur a :
- Un nom unique (`drone_sensor`, `plc_sensor`, `iot_sensor`)
- Un préfixe de secteur (`DRONE_`, `PLC_`, `IOT_`)

#### 3. **Fonction `sensor_worker()`**

Nouvelle fonction qui gère chaque capteur indépendamment :

**Caractéristiques** :
- Chaque capteur a sa propre base de données : `keri_run_{run_id}_{sensor_name}/`
- Chaque capteur génère son propre fichier anchor : `blockchain_anchor_{sensor_name}.json`
- Chaque capteur génère son propre fichier path : `current_db_path_{sensor_name}.txt`
- Chaque capteur a sa propre identité KERI (AID) unique
- Chaque capteur maintient son propre compteur de cycle

**Fichiers générés par capteur** :
- `blockchain_anchor_drone_sensor.json`
- `blockchain_anchor_plc_sensor.json`
- `blockchain_anchor_iot_sensor.json`
- `current_db_path_drone_sensor.txt`
- `current_db_path_plc_sensor.txt`
- `current_db_path_iot_sensor.txt`

#### 4. **Fonction `main()` Modifiée**

La fonction `main()` :
- Crée un `stop_event` pour l'arrêt propre de tous les threads
- Démarre un thread pour chaque capteur
- Surveille les threads pour détecter les arrêts inattendus
- Gère l'arrêt propre avec `Ctrl+C`

**Arrêt propre** :
- Envoie le signal `stop_event.set()` à tous les threads
- Attend que tous les threads se terminent (`thread.join()`)
- Ferme toutes les bases de données proprement

#### 5. **Isolation Complète**

Chaque capteur est complètement isolé :
- Base de données séparée
- Fichiers séparés
- Identité KERI séparée
- Cycle de données indépendant

---

## 🔍 Modifications du Vérificateur (`03_kel_verifier.py`)

### Objectif

Adapter le vérificateur pour lire et vérifier les trois bases de données des trois capteurs.

### Changements Principaux

#### 1. **Configuration Multi-Capteurs**

```python
SENSORS = ["drone_sensor", "plc_sensor", "iot_sensor"]
```

#### 2. **Fonction `get_config()` Modifiée**

**Avant** : Lisait un seul fichier path et un seul fichier anchor  
**Maintenant** : Lit trois fichiers path et trois fichiers anchor

**Nouvelle logique** :
- Parcourt tous les capteurs
- Pour chaque capteur, lit `current_db_path_{sensor_name}.txt` et `blockchain_anchor_{sensor_name}.json`
- Retourne une liste de configurations pour tous les capteurs trouvés
- Ignore les capteurs dont les fichiers sont manquants (avec avertissement)

#### 3. **Nouvelle Fonction `verify_sensor()`**

Fonction dédiée pour vérifier un seul capteur :

**Fonctionnalités** :
- Ouvre la base de données du capteur
- Vérifie que l'AID existe dans la base de données
- Affiche un tableau avec tous les événements
- Affiche le nombre total d'événements vérifiés
- Retourne `True` si la vérification réussit, `False` sinon

**Affichage** :
- En-tête avec le nom du capteur, la base de données et l'AID
- Tableau des événements (SEQ, TYPE, SAID, PAYLOAD)
- Résumé avec le nombre d'événements vérifiés

#### 4. **Fonction `main()` Modifiée**

**Nouvelle logique** :
- Récupère les configurations de tous les capteurs
- Vérifie chaque capteur séparément
- Affiche les résultats pour chaque capteur
- Affiche un résumé final avec le nombre de capteurs vérifiés avec succès

**Résumé final** :
- Affiche : `Verification Summary: X/3 sensor(s) verified successfully`
- Affiche un message de succès si tous les capteurs sont vérifiés
- Affiche un avertissement si certains capteurs ont échoué

---

## 🚀 Commandes pour Exécuter les Programmes

### Prérequis

1. **Environnement virtuel activé** :
   ```powershell
   .\keri-env\Scripts\activate.bat
   ```

   Ou utiliser Python directement (sans activer) :
   ```powershell
   .\keri-env\Scripts\python.exe
   ```

2. **Bibliothèques installées** :
   ```powershell
   .\keri-env\Scripts\python.exe -m pip install -r requirements.txt
   ```

---

### 1. Génération des Données (`01_anchor_generator.py`)

#### Commande de base :
```powershell
.\keri-env\Scripts\python.exe scripts\01_anchor_generator.py
```

#### Ce qui se passe :
1. **Initialisation** :
   - Création d'un `run_id` unique pour cette session
   - Démarrage de 3 threads (un pour chaque capteur)

2. **Pour chaque capteur** :
   - Création de la base de données : `keri_run_{run_id}_{sensor_name}/`
   - Création de l'identité KERI (AID)
   - Génération de données toutes les 3 secondes
   - Signature cryptographique des données
   - Mise à jour du fichier anchor

3. **Fichiers créés** :
   - `blockchain_anchor_drone_sensor.json`
   - `blockchain_anchor_plc_sensor.json`
   - `blockchain_anchor_iot_sensor.json`
   - `current_db_path_drone_sensor.txt`
   - `current_db_path_plc_sensor.txt`
   - `current_db_path_iot_sensor.txt`
   - `keri_run_{run_id}_drone_sensor/` (base de données)
   - `keri_run_{run_id}_plc_sensor/` (base de données)
   - `keri_run_{run_id}_iot_sensor/` (base de données)

#### Arrêt du programme :
- Appuyez sur `Ctrl+C`
- Tous les threads s'arrêtent proprement
- Toutes les bases de données sont fermées
- Les bases de données sont supprimées (mode temporaire)

---

### 2. Vérification des Données (`03_kel_verifier.py`)

#### Commande de base :
```powershell
.\keri-env\Scripts\python.exe scripts\03_kel_verifier.py
```

#### Prérequis :
- Le générateur doit avoir été exécuté (même s'il est arrêté maintenant)
- Les fichiers path et anchor doivent exister

#### Ce qui se passe :
1. **Lecture des configurations** :
   - Lit les fichiers `current_db_path_*.txt` pour tous les capteurs
   - Lit les fichiers `blockchain_anchor_*.json` pour tous les capteurs
   - Ignore les capteurs dont les fichiers sont manquants

2. **Pour chaque capteur trouvé** :
   - Ouvre la base de données correspondante
   - Vérifie que l'AID existe
   - Lit tous les événements depuis le KEL (Key Event Log)
   - Affiche un tableau avec tous les événements


   - Un tableau séparé pour chaque capteur
   - Colonnes : SEQ (séquence), TYPE (type d'événement), SAID (hash), PAYLOAD (données)
   - Résumé avec le nombre d'événements par capteur







## 📝 Notes Importantes

### Bases de Données Temporaires

- Les bases de données sont **temporaires** par défaut
- Elles sont supprimées lorsque le générateur s'arrête
- Pour la production, modifier le code pour utiliser des bases de données persistantes

### Fichiers Générés

- Les fichiers anchor (`blockchain_anchor_*.json`) contiennent seulement le **dernier événement**
- Les bases de données LMDB contiennent **tous les événements**
- Le vérificateur lit depuis les bases de données (source de vérité)

### Performance

- Les trois capteurs fonctionnent en parallèle (multithreading)
- Chaque capteur génère un événement toutes les 3 secondes
- Le système peut facilement supporter plus de capteurs
