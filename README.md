# KERI IT-OT Security Gateway 🛡️

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![KERI](https://img.shields.io/badge/KERI-2.0-orange)

This is the **OT & IT Layer** of the system. It simulates industrial drone sensors that generate data, sign it using **KERI (Key Event Receipt Infrastructure)**, and anchor the cryptographic proofs to a blockchain bridge.

## 📂 Project Structure

- `main.py`: **The Drone Sensor**. Generates temperature data and signs it (OT Layer).
- `bridge.py`: **The Bridge**. Watches for new events and sends them to the Blockchain (IT Layer).
- `verifier.py`: **The Auditor**. Verifies that the local database matches the Blockchain records.
- `keri_drones_db/`: The tamper-proof local ledger (LMDB).

## 🚀 Setup Guide

### 1. Prerequisites
- Python 3.10 or higher
- Git Bash (recommended for Windows)

### 2. Create Environment
```bash
# Create virtual environment
python -m venv keri-env

# Activate it (Windows Git Bash)
source keri-env/Scripts/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install web3 python-dotenv

```

### 4. Configuration

Create a `.env` file in the root folder with your blockchain details:

```ini
RPC_URL=[http://127.0.0.1:8545](http://127.0.0.1:8545)
PRIVATE_KEY=0x... (Your Hardhat Account #0 Key)
CONTRACT_ADDRESS=0x... (Deploy the contract to get this)

```

---

## 🎮 How to Run

You will need **3 Terminal Windows** open simultaneously.

### Terminal 1: The Drone (OT)

Simulates a sensor generating data every 3 seconds.

```bash
source keri-env/Scripts/activate
python main.py --id 1

```

### Terminal 2: The Bridge (IT)

Listens for new data and anchors it to Ethereum.

```bash
source keri-env/Scripts/activate
python bridge.py

```

*Note: Ensure the blockchain is running in the `contract` folder first!*

### Terminal 3: The Auditor (Verification)

Run this anytime to prove the system's integrity.

```bash
source keri-env/Scripts/activate
python verifier.py

```

---

## 🔍 Troubleshooting

* **"Module not found 'keri'"**: Ensure you activated the environment with `source keri-env/Scripts/activate`.
* **"Bridge is frozen"**: The bridge waits for *new* events. Ensure the Drone is running in another window.
* **"libsodium.dll not found"**: The `scripts/utils.py` file handles this automatically. Ensure you are running commands from the root folder.

