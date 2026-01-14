import os
import shutil
import uuid
from keri.app import habbing
from keri.core import eventing, parsing

# 1. Setup a clean environment
base_folder = f"./keri_data_run_{uuid.uuid4()}"
os.makedirs(base_folder, exist_ok=True)

def introduce_identities(hab, receiver_kevery):
    """
    Exchanges the 'Passport' (Inception Event).
    """
    # --- READ STEP ---
    # 1. Get the iterator from the database
    kel_iter = hab.db.clonePreIter(pre=hab.pre, fn=0)
    
    # 2. Extract the raw bytes of the Inception Event
    icp_raw = bytearray(next(kel_iter))
    
    # 3. Release the Read Lock
    del kel_iter 
    
    print(f"\n[Intro] Introducing {hab.name} to receiver...")
    
    # --- WRITE STEP ---
    # 4. Parse and Process
    parser = parsing.Parser(kvy=receiver_kevery)
    
    # FIX: Just call .parse(). Do not wrap in list().
    # The parser automatically feeds the Kevery.
    parser.parse(ims=icp_raw)


# 2. Initialize the "Habery" (Key Store Manager)
habery = habbing.Habery(name="test_controller", base=base_folder)

# 3. Create two Sensors (Identities/Habs)
print("Creating Identities...")
sensor_a = habery.makeHab(name="sensor_a", isith="1", icount=1)
sensor_b = habery.makeHab(name="sensor_b", isith="1", icount=1)

print(f"Sensor A AID: {sensor_a.pre}")
print(f"Sensor B AID: {sensor_b.pre}")

# 4. Create "Kevery" instances (The Validators)
kevery_a = eventing.Kevery(db=sensor_a.db)
kevery_b = eventing.Kevery(db=sensor_b.db)

# Simple Simulator Queue
queue = []

def create_and_send(sender_hab, receiver_kevery, payload: dict):
    """
    Generates data, signs it (Interaction Event), and puts it in the network queue.
    """
    # interact() creates the event and signs it
    msg = sender_hab.interact(data=[payload])
    
    print(f"\n[Network] {sender_hab.name} sending packet: {payload}")
    queue.append((receiver_kevery, msg))

def process_queue():
    """
    Simulates the network delivering messages.
    """
    print("\n--- Processing Network Queue ---")
    while queue:
        r_kevery, msg_stream = queue.pop(0)
        
        # FIX: Just call .parse(). Do not wrap in list().
        parser = parsing.Parser(kvy=r_kevery)
        parser.parse(ims=msg_stream)

# --- SIMULATION START ---

try:
    # Step 1: Introduction (The Handshake)
    introduce_identities(sensor_a, kevery_b)
    introduce_identities(sensor_b, kevery_a)

    # Step 2: Sensor A sends telemetry to Sensor B
    create_and_send(sensor_a, kevery_b, {"temp": "22C", "status": "OK"})

    # Step 3: Sensor B sends an ACK back to Sensor A
    create_and_send(sensor_b, kevery_a, {"cmd": "ACK", "timestamp": "1200"})

    # Step 4: Process the traffic
    process_queue()

    # --- VERIFICATION ---
    print("\n--- Verifying KELs (History) ---")

    print(f"\nView from {sensor_b.name}'s Database (What B knows):")
    if sensor_a.pre in sensor_b.db.kevers:
        print(f"SUCCESS: {sensor_b.name} verified {sensor_a.name}!")
        
        # Retrieve the latest state of A from B's database
        kever = sensor_b.db.kevers[sensor_a.pre]
        
        # Check the payload of the last event
        # 'a' is the field for anchored data (seals)
        print(f"Latest Event from A: sn={kever.sn}, payload={kever.serder.ked['a']}")
    else:
        print(f"FAILURE: {sensor_b.name} does not know {sensor_a.name}")

finally:
    # Always clean up
    habery.db.close()
    if os.path.exists(base_folder):
        shutil.rmtree(base_folder)