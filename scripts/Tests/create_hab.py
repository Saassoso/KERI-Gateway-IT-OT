from keri.app import habbing
import os

base_folder = "./keri_data"
os.makedirs(base_folder, exist_ok=True)

# Create Habery
habery = habbing.Habery(name="test", base=base_folder)

# Create a new Hab
hab = habery.makeHab(name="almen", isith="1", icount=1)
print("New Hab created!")
print("AID:", hab.pre)
print("Signing key:", hab.kever.verfers[0].qb64)
# Close to persist
habery.db.close()
print("Hab saved to disk.")
