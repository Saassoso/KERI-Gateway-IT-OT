import os, shutil
import json
from keri.app import habbing

DB_NAME = "keri_data"
if os.path.exists(f"./{DB_NAME}"):
    shutil.rmtree(f"./{DB_NAME}")

try:
    # 2. INITIALIZE: Use Habery (The Manager)
    # This automatically creates the 'db' and 'ks' (keystore) in the background
    hby = habbing.Habery(name="my_controller", base=DB_NAME)

    # 3. CREATE IDENTITY (Make a Habitat)
    # makeHab creates the identifier (AID) and keys
    hab = hby.makeHab(name="my_user", isith="1", icount=1)

    print(f"Environment Initialized.")
    print(f"dentity Created. Name: {hab.name}")
    print(f"AID (Prefix): {hab.pre}")

    # 4. LIST IDENTIFIERS
    print("\nCurrent Identifiers in Database:")
    # We look at the Habery's dictionary of habitats
    for name, habitat in hby.habs.items():
        print(f"- {name}: {habitat.pre}")

finally:
# 5. CLEANUP
    # Always close the database to prevent corruption
    if 'hby' in locals():
        hby.close()
    
    # Optional: Delete the folder
    if os.path.exists(f"./{DB_NAME}"):
        shutil.rmtree(f"./{DB_NAME}")
    print("\n🧹 Database closed and cleaned up.")