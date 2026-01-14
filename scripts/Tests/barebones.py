import os, shutil, uuid, json
from keri.app import habbing
from keri.core import serdering

# 1. SETUP: Unique path for this test
path = f"./keri_basic_test_{uuid.uuid4()}"
os.makedirs(path, exist_ok=True)

# 2. START: Initialize the Environment (Habery)
habery = habbing.Habery(name="drone_controller", base=path)

try:
    # 3. CREATE AID: The "Passport" Birth (Inception)
    sensor = habery.makeHab(name="alpha_sensor", isith="1", icount=1)
    print(f"--- SUCCESS ---")
    print(f"Sensor AID Created: {sensor.pre}")

    # 4. CREATE DATA: Add an entry to the "History Book" (Interaction)
    # This signs a Modbus-style payload: Package=Eggs, Zone=5
    sensor.interact(data=[{"pkg": "Eggs", "zone": 5, "status": "SAFE"}])
    print("Action recorded and signed in the KEL.\n")

    # 5. READ KEL: Extract the History before closing the DB
    print("--- READING KEL (Identity History) ---")
    
    # We convert the iterator to a LIST immediately so we don't 
    # hit the "Closed Object" error later.
    kel_events = list(sensor.db.clonePreIter(pre=sensor.pre, fn=0))
    
    for raw_msg in kel_events:
        # Load the event into a Serder (Serialization/Deserialization)
        evt = serdering.Serder(raw=bytearray(raw_msg))
        
        # We use a safer way to access the dictionary: .ked or .raw
        # In case .ked fails, we look at the raw content
        data = evt.ked if hasattr(evt, 'ked') else json.loads(evt.raw)
        
        sn = data.get('s', 'unknown')
        etype = data.get('t', 'unknown')
        
        print(f"Event #{sn} [{etype}] | Hash: {evt.said[:10]}...")
        
        # Linkage: This is the "Chain of Trust"
        if 'p' in data:
            print(f"   ↳ 🔗 Linked back to: {data['p'][:10]}...")
        
        # Payload: This is the SCADA data
        if 'a' in data:
            print(f"   ↳ 📦 Payload: {data['a']}")

finally:
    # 6. CLEANUP
    habery.db.close()
    if os.path.exists(path):
        shutil.rmtree(path)
    print("\nDatabase closed and environment cleaned.")