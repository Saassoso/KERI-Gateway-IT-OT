import os, shutil, uuid, json, time
from datetime import datetime
from keri.app import habbing
from keri.core import serdering

# --- MISSION CONFIG ---
DRONE_ID = "Heavy_Lift_Drone_01"
DATA_INTERVAL = 4 
base_path = f"./drone_data_{uuid.uuid4()}"
os.makedirs(base_path, exist_ok=True)

def run_drone_mission():
    habery = habbing.Habery(name=DRONE_ID, base=base_path)
    
    try:
        sensor_hab = habery.makeHab(name=DRONE_ID, isith="1", icount=1)
        print(f"🛰️  Industrial Drone Controller '{DRONE_ID}' Online.")
        print(f"🆔 AID: {sensor_hab.pre}\n")

        # Simulated Asset Delivery Missions
        missions = [
            {"pkg": 2, "zone": 45, "desc": "High-Value Electronics"},
            {"pkg": 1, "zone": 12, "desc": "Urgent Medical Supplies"},
            {"pkg": 0, "zone": 88, "desc": "Standard Logistics"}
        ]

        for i, mission in enumerate(missions):
            # --- FULL ICS MODBUS MAPPING ---
            ot_payload = {
                "timestamp": datetime.now().isoformat(),
                "modbus_map": {
                    "HR0_PackageType": mission["pkg"],
                    "HR1_DeliveryZone": mission["zone"],
                    "HR4_AssetID": f"ASSET-{uuid.uuid4().hex[:6].upper()}",
                    "C10_InventoryCheck": True,
                    "C11_SecurityLock": True,
                    "C15_SelfDestructArmed": False
                },
                "metadata": {
                    "description": mission["desc"],
                    "operator_id": "OP-99"
                }
            }

            # 1. KERI Signing (The Digital Seal)
            sensor_hab.interact(data=[ot_payload])
            
            # 2. Extract Event Data safely
            kel_events = list(sensor_hab.db.clonePreIter(pre=sensor_hab.pre, fn=0))
            evt = serdering.Serder(raw=bytearray(kel_events[-1]))
            event_dict = json.loads(evt.raw)
            
            # 3. Create the Blockchain Anchor
            anchor = {
                "drone_aid": sensor_hab.pre,
                "sn": event_dict.get('s'),
                "event_hash": evt.said,
                "mission_critical": {
                    "asset": ot_payload["modbus_map"]["HR4_AssetID"],
                    "target_zone": mission["zone"]
                }
            }

            with open("blockchain_anchor.json", "w") as f:
                json.dump(anchor, f, indent=4)

            print(f"✅ MISSION AUTHORIZED [SN {event_dict.get('s')}]")
            print(f"   Asset: {ot_payload['modbus_map']['HR4_AssetID']} -> Zone {mission['zone']}")
            print(f"   Blockchain Anchor Generated: {evt.said[:15]}...\n")
            
            time.sleep(DATA_INTERVAL)

    finally:
        habery.db.close()
        shutil.rmtree(base_path)

if __name__ == "__main__":
    run_drone_mission()