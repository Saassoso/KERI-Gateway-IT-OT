from keri.app import habbing
from keri.core import eventing

# Create a Habery (local KERI identity manager)
# This manages your KERI identities (AIDs)
habery = habbing.Habery(name="test", base="./keri_data")

# Create a new local KERI identity (Hab)
hab = habery.makeHab(name="alic")

print("Hab created!")
print("AID:", hab.pre)          # public identifier