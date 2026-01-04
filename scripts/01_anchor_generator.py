import os
import sys
import shutil
import json
import time
import uuid
import logging
import threading

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
from keri.core import serdering

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [GENERATOR] - %(message)s')

# Sensor configuration
SENSORS = [
    {"name": "drone_sensor", "sector_prefix": "DRONE"},
    {"name": "plc_sensor", "sector_prefix": "PLC"},
    {"name": "iot_sensor", "sector_prefix": "IOT"}
]

# Global run ID for this session
run_id = str(uuid.uuid4())[:8]

def sensor_worker(sensor_config, stop_event):
    """
    Worker function for each sensor. Each sensor runs in its own thread
    with its own database and files.
    """
    sensor_name = sensor_config["name"]
    sector_prefix = sensor_config["sector_prefix"]
    
    # Each sensor has its own database
    db_name = f"keri_run_{run_id}_{sensor_name}"
    anchor_file = f"blockchain_anchor_{sensor_name}.json"
    path_file = f"current_db_path_{sensor_name}.txt"
    
    logging.info(f"[{sensor_name.upper()}] Initializing KERI environment: ./{db_name}")
    
    # Persist DB path for verifier
    with open(path_file, "w") as f:
        f.write(db_name)
    
    hby = habbing.Habery(name="controller", base=db_name)
    
    try:
        # Create Sensor Identity
        sensor = hby.makeHab(name=sensor_name, isith="1", icount=1)
        logging.info(f"[{sensor_name.upper()}] Identity established. AID: {sensor.pre}")
        
        cycle = 0
        while not stop_event.is_set():
            cycle += 1
            payload = {
                "status": "ACTIVE",
                "cycle": cycle,
                "temp": 45 + (cycle % 10),
                "sector": f"{sector_prefix}_{cycle}",
                "sensor_type": sensor_name
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
            
            logging.info(f"[{sensor_name.upper()}] Event #{anchor['seq']} committed. Hash: {anchor['said']}")
            time.sleep(3)
            
    except Exception as e:
        logging.error(f"[{sensor_name.upper()}] Runtime error: {e}")
    finally:
        hby.close()
        cleanup_db(db_name, sensor_name)

def cleanup_db(db_name, sensor_name):
    """Clean up database for a specific sensor."""
    if os.path.exists(db_name):
        try:
            shutil.rmtree(db_name)
            logging.info(f"[{sensor_name.upper()}] Database cleaned up.")
        except PermissionError:
            logging.warning(f"[{sensor_name.upper()}] Could not delete database (file lock active).")

def main():
    logging.info("=" * 80)
    logging.info("Starting Multi-Sensor KERI Generator")
    logging.info(f"Run ID: {run_id}")
    logging.info(f"Number of sensors: {len(SENSORS)}")
    logging.info("=" * 80)
    
    # Create stop event for graceful shutdown
    stop_event = threading.Event()
    
    # Start a thread for each sensor
    threads = []
    for sensor_config in SENSORS:
        thread = threading.Thread(
            target=sensor_worker,
            args=(sensor_config, stop_event),
            name=f"Thread-{sensor_config['name']}",
            daemon=True
        )
        thread.start()
        threads.append(thread)
        logging.info(f"Started thread for {sensor_config['name']}")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
            # Check if all threads are still alive
            if not any(t.is_alive() for t in threads):
                logging.warning("All sensor threads have stopped unexpectedly.")
                break
                
    except KeyboardInterrupt:
        logging.info("Stopping all sensors...")
        stop_event.set()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join(timeout=5)
            if thread.is_alive():
                logging.warning(f"Thread {thread.name} did not stop gracefully.")
        
        logging.info("All sensors stopped.")

if __name__ == "__main__":
    main()