import os, shutil, uuid
import json
from keri.app import habbing
from keri.core import eventing, parsing

# 1. SETUP: Unique path
path = f"./keri_verification_{uuid.uuid4()}"
os.makedirs(path, exist_ok=True)

# 2. START: The Environment
habery = habbing.Habery(name="industrial_network", base=path)

try:
    # --- THE SENDER (Sensor Alpha) ---
    sensor = habery.makeHab(name="alpha", isith="1", icount=1)
    
    # Sensor generates the Inception Event (Passport)
    icp_event = next(sensor.db.clonePreIter(pre=sensor.pre, fn=0))
    
    # Sensor generates an Interaction Event (Signed Command)
    msg = sensor.interact(data=[{"command": "START_DRONE", "speed": 50}])
    
    print(f"Sensor {sensor.name} created and signed a command.")

    # --- THE RECEIVER (Controller Beta) ---
    # The Controller has its own database and validator (Kevery)
    controller_db = habery.db # In this demo they share the DB, but usually they are separate
    controller_kevery = eventing.Kevery(db=controller_db)
    
    # To process raw bytes, we need a Parser
    parser = parsing.Parser(kvy=controller_kevery)

    print("\n--- CONTROLLER VERIFICATION ---")
    
    # Step A: Controller receives the 'Passport' (Inception)
    parser.parse(ims=bytearray(icp_event))
    print("1. Sensor Identity (Passport) Verified.")

    # Step B: Controller receives the 'Command' (Interaction)
    parser.parse(ims=bytearray(msg))
    
    # Check if the Controller now has the sensor in its 'Trusted List'
    if sensor.pre in controller_kevery.db.kevers:
        kever = controller_kevery.db.kevers[sensor.pre]
        print(f"2. Command Verified! Sequence: {kever.sn}")
        print(f"3. Executing: {kever.serder.ked['a']}")
    else:
        print("Verification Failed: Unknown Sensor!")
    # 4. PREPARE FOR BLOCKCHAIN
    anchor_data = {
     "aid": sensor.pre,
     "sn": kever.sn,
     "event_hash": kever.serder.said,  # The unique fingerprint of this event
     "timestamp": "2024-05-20T12:00:00Z" # You can use datetime.now()
    }

    with open("blockchain_anchor.json", "w") as f:
        json.dump(anchor_data, f, indent=4)

    print(f"\n4. Anchor file created: blockchain_anchor.json")
    print(f"   Ready to send Hash {kever.serder.said[:10]} to Smart Contract.")

finally:
    habery.db.close()
    shutil.rmtree(path)