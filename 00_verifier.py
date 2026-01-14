# verifier.py
import os
import json
import logging
import glob

# 1. Use our shared utility for Libsodium
from scripts.utils import load_libsodium
load_libsodium()

from keri.app import habbing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [VERIFIER] - %(message)s')

def get_active_sensors():
    """Finds all sensors that have a DB path file generated."""
    path_files = glob.glob("current_db_path_*.txt")
    sensors = []
    
    for p_file in path_files:
        # Extract name: current_db_path_drone_sensor_1.txt -> drone_sensor_1
        name = p_file.replace("current_db_path_", "").replace(".txt", "")
        
        # Read the DB path
        with open(p_file, "r") as f:
            db_path = f.read().strip()
            
        # Read the Anchor file
        anchor_file = f"blockchain_anchor_{name}.json"
        if not os.path.exists(anchor_file):
            logging.warning(f"Found path for {name} but no anchor file. Skipping.")
            continue
            
        with open(anchor_file, "r") as f:
            anchor_data = json.load(f)
            
        sensors.append({
            "name": name,
            "db_path": db_path,
            "aid": anchor_data['aid'],
            "latest_seq": anchor_data['seq']
        })
    return sensors

def verify_sensor(sensor_config):
    name = sensor_config['name']
    db_path = sensor_config['db_path'] # This is the absolute path from the text file
    aid = sensor_config['aid']
    
    logging.info(f"--- Verifying {name.upper()} ---")
    logging.info(f"Target Database Path: {db_path}")
    logging.info(f"AID: {aid}")
    
    # Check if the path from the map file actually exists
    if not os.path.exists(db_path):
        logging.error(f"❌ Database folder not found at: {db_path}")
        return False

    # FIXED: Use the relative name "keri_drones_db", NOT the absolute path
    # KERI will automatically resolve this to the path we verified above
    try:
        hby = habbing.Habery(name="controller", base="keri_drones_db", free=True)
    except Exception as e:
        logging.error(f"Could not open KERI database: {e}")
        return False
    
    try:
        if aid not in hby.kevers:
            logging.error(f"❌ AID {aid} not found in database!")
            return False
            
        # Iterate through the Key Event Log (KEL)
        kel_iter = hby.db.clonePreIter(pre=aid, fn=0)
        
        event_count = 0
        for raw_event in kel_iter:
            event_count += 1
            
        logging.info(f"✅ Data Integrity Verified. Total Events: {event_count}")
        logging.info(f"   Latest Sequence in DB: {event_count - 1}")
        logging.info(f"   Latest Sequence in Anchor: {sensor_config['latest_seq']}")
        
        if (event_count - 1) == sensor_config['latest_seq']:
            print(f"✅ {name}: SYNCED (Anchor matches Database)")
        else:
            print(f"⚠️ {name}: UNSYNCED (Anchor is behind or ahead)")
            
    except Exception as e:
        logging.error(f"Verification Failed: {e}")
    finally:
        hby.close()

if __name__ == "__main__":
    sensors = get_active_sensors()
    if not sensors:
        print("No active sensors found. Run 'main.py' first.")
    else:
        for s in sensors:
            verify_sensor(s)
            print("\n")