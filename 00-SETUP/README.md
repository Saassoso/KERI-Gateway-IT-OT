# KERI Setup (Windows)

This guide explains how to properly install and activate KERI (keripy) in a Python environment on Windows.

--- 
### Prerequisites

- Windows 10/11
- Python 3.13 installed (for KERI >= 1.0.4)
- Git installed
- PowerShell or Command Prompt
- Internet connection to download Python packages

## Step 1 - Checking python version 


## Step 2 — Create a Python Virtual Environment

## Step 3 — Install KERIPY from GitHub

## Step 4 — Install libsodium (Required for pysodium)
1. Download prebuilt DLL from libsodium releases:
- `libsodium-1.0.20-msvc.zip` or newer if it exist
2. Extract the zip and locate libsodium.dll (typically under `x64\Release\v143\dynamic\`)
3. Copy libsodium.dll to your virtual environment's Scripts folder:
```C:\Users\chari\Documents\GitHub\KERI-Blockchain-Anchored-IT-OT\keri-env\Scripts\```
4. Verify it’s visible to Python:
```python .\test_libsodium.py```
Expected output: path to libsodium.dll.

## Step 5 - Test KERI Import

Run :
python .\test_keri.py

Expected output:
![01-keri-tesr](./attachments/01-keri-tesr.png)
