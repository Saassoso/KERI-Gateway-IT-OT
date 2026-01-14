from keri.app import habbing

habery = habbing.Habery(name="test", base="./keri_data")
for name, hab in habery.habs.items():
    print(f"Hab name: {name}, AID: {hab.pre}")
