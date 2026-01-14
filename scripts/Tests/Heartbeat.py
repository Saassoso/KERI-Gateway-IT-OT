import os, json, time, multiprocessing
from datetime import datetime
from keri.app import habbing
from keri.core import serdering

# --- CONFIGURATION ---
DATA_INTERVAL = 5 
DRONE_FLEET = ["Heavy_Lift_Drone_01", "Scout_Drone_02", "Emergency_Med_03"]

def run_virtual_drone(drone_name):
    relative_base = f"db_{drone_name}"

    try:
        # 1. Initialize the Habery
        hby = habbing.Habery(name=drone_name, base=relative_base)
        
        # 2. PERSISTENCE LOGIC: Check the database directly
        # We look for any existing Hab (Habitat) in this database
        existing_habs = hby.db.habs.getItemIter()
        hab = None
        
        # Try to find the hab that matches our drone name in the local DB
        for name, hab_info in existing_habs:
            if name == drone_name:
                hab = hby.setupHab(name=drone_name) # This is the internal way to reload
                break
        
        if hab:
            print(f"🔄 [{drone_name}] RESUMING | AID: {hab.pre}")
        else:
            # If not found, create a brand new one
            hab = hby.makeHab(name=drone_name, isith="1", icount=1)
            print(f"✅ [{drone_name}] NEW IDENTITY | AID: {hab.pre}")

        while True:
            # 3. Maintain History Continuity
            kel_all = list(hab.db.clonePreIter(pre=hab.pre, fn=0))
            current_sn = len(kel_all)
            
            # --- MISSION DATA (SCADA MODBUS) ---
            ot_payload = {
                "timestamp": datetime.now().isoformat(),
                "modbus_map": {
                    "HR0_Pkg": current_sn % 3, 
                    "HR1_Zone": 10 + current_sn,
                    "C11_Secure": True
                },
                "telemetry": {"battery": max(0, 100 - current_sn)}
            }

            # 4. SIGNING: Create Interaction Event
            hab.interact(data=[ot_payload])
            
            # 5. GET THE LATEST SAID
            kel_all = list(hab.db.clonePreIter(pre=hab.pre, fn=0))
            evt = serdering.Serder(raw=bytearray(kel_all[-1]))
            event_dict = json.loads(evt.raw)
            
            # 6. GENERATE THE ANCHOR FILE
            anchor = {
                "drone": drone_name,
                "aid": hab.pre,
                "sn": event_dict.get('s'),
                "said": evt.said,
                "payload": ot_payload["modbus_map"]
            }

            with open(f"anchor_{drone_name}.json", "w") as f:
                json.dump(anchor, f, indent=4)

            print(f"📡 [{drone_name}] Event #{event_dict.get('s')} | SAID: {evt.said[:12]}...")
            
            time.sleep(DATA_INTERVAL)

    except Exception as e:
        # Detailed error printing to catch any library changes
        import traceback
        print(f"❌ [{drone_name}] Error: {str(e)}")
        # traceback.print_exc() # Uncomment this if you need deep debugging
    finally:
        if 'hby' in locals():
            hby.close()

if __name__ == "__main__":
    print("🛸 KERI-Anchored Drone Fleet Simulator")
    print("--- Fully Persistent Identity Mode ---")
    
    processes = []
    for name in DRONE_FLEET:
        p = multiprocessing.Process(target=run_virtual_drone, args=(name,))
        p.start()
        processes.append(p)

    try:
        for p in processes: p.join()
    except KeyboardInterrupt:
        print("\n🛑 Grounding drones. Identities remain in db_* folders.")
        for p in processes: p.terminate()