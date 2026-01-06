import os
import sys
import json
import time
import uuid
import logging

# Fix for libsodium.dll loading on Windows
if sys.platform == 'win32':
    import ctypes
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    libsodium_dir = os.path.join(project_root, 'keri-env', 'Scripts')
    libsodium_path = os.path.join(libsodium_dir, 'libsodium.dll')
    if os.path.exists(libsodium_path):
        # Add DLL directory to search path
        os.add_dll_directory(libsodium_dir)
        # Add to PATH environment variable (for ctypes.util.find_library)
        dll_dir = os.path.abspath(libsodium_dir)
        if dll_dir not in os.environ.get('PATH', ''):
            os.environ['PATH'] = dll_dir + os.pathsep + os.environ.get('PATH', '')
        # Load the DLL directly to ensure it's available
        try:
            ctypes.CDLL(libsodium_path)
        except OSError:
            pass  # DLL might already be loaded

from keri.app import habbing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DRONE_SENSOR_2] - %(message)s')

# Sensor configuration
SENSOR_NAME = "drone_sensor_2"
SECTOR_PREFIX = "DRONE"

# Shared database name (all sensors use the same database)
SHARED_DB_NAME = "keri_drones_db"

def main():
    # All sensors use the same shared database
    db_name = SHARED_DB_NAME
    anchor_file = f"blockchain_anchor_{SENSOR_NAME}.json"
    path_file = f"current_db_path_{SENSOR_NAME}.txt"
    
    logging.info("=" * 80)
    logging.info(f"Starting {SENSOR_NAME.upper()}")
    logging.info(f"Database: ./{db_name}")
    logging.info("=" * 80)
    
    logging.info(f"Initializing KERI environment: ./{db_name}")
    
    # Persist DB path for verifier
    with open(path_file, "w") as f:
        f.write(db_name)
    
    hby = habbing.Habery(name="controller", base=db_name)
    
    try:
        # Get or create Sensor Identity
        try:
            # Try to create new identity
            sensor = hby.makeHab(name=SENSOR_NAME, isith="1", icount=1)
            logging.info(f"Identity created. AID: {sensor.pre}")
        except ValueError as e:
            if "Already incepted" in str(e) or "already exists" in str(e).lower():
                # Identity already exists, load it
                sensor = hby.habByName(name=SENSOR_NAME)
                if sensor is None:
                    raise RuntimeError(f"Identity {SENSOR_NAME} should exist but could not be loaded")
                logging.info(f"Identity loaded. AID: {sensor.pre}")
            else:
                raise
        
        cycle = 0
        try:
            while True:
                cycle += 1
                payload = {
                    "status": "ACTIVE",
                    "cycle": cycle,
                    "temp": 45 + (cycle % 10),
                    "sector": f"{SECTOR_PREFIX}_{cycle}",
                    "sensor_type": SENSOR_NAME
                }
                
                # Sign data (commit to KEL)
                sensor.interact(data=[payload])
                
                # Retrieve latest event
                log = list(sensor.db.clonePreIter(pre=sensor.pre, fn=0))
                raw_bytes = bytes(log[-1])
                
                try:
                    raw_str = raw_bytes.decode('utf-8')
                    event_data, _ = json.JSONDecoder().raw_decode(raw_str)
                except Exception:
                    event_data = json.loads(raw_bytes)
                
                # Export Anchor
                anchor = {
                    "aid": sensor.pre,
                    "seq": int(event_data['s'], 16),
                    "said": event_data['d'],
                    "payload": payload
                }
                
                with open(anchor_file, "w") as f:
                    json.dump(anchor, f, indent=4)
                
                logging.info(f"Event #{anchor['seq']} committed. Hash: {anchor['said']}")
                time.sleep(3)
                
        except KeyboardInterrupt:
            logging.info("Stopping sensor...")
            
    except Exception as e:
        logging.error(f"Runtime error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        hby.close()
        logging.info(f"{SENSOR_NAME.upper()} stopped.")

if __name__ == "__main__":
    main()

