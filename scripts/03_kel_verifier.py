import os
import sys
import json
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
from keri.core import serdering

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [VERIFIER]  - %(message)s')

# Sensor configuration
SENSORS = ["drone_sensor", "plc_sensor", "iot_sensor"]

def get_config():
    """Get configuration for all sensors."""
    configs = []
    
    for sensor_name in SENSORS:
        path_file = f"current_db_path_{sensor_name}.txt"
        anchor_file = f"blockchain_anchor_{sensor_name}.json"
        
        if not os.path.exists(path_file) or not os.path.exists(anchor_file):
            logging.warning(f"Configuration files not found for {sensor_name}. Skipping...")
            continue
        
        try:
            with open(path_file, "r") as f:
                db_path = f.read().strip()
            
            with open(anchor_file, "r") as f:
                anchor_data = json.load(f)
            
            configs.append({
                "sensor_name": sensor_name,
                "db_path": db_path,
                "aid": anchor_data.get('aid'),
                "anchor_file": anchor_file
            })
        except Exception as e:
            logging.error(f"Error reading config for {sensor_name}: {e}")
            continue
    
    if not configs:
        raise FileNotFoundError("No sensor configuration files found. Ensure generator is running.")
    
    return configs

def parse_event(raw_bytes):
    """Safely extracts JSON from KERI event bytes."""
    try:
        raw_str = bytes(raw_bytes).decode('utf-8')
        data, _ = json.JSONDecoder().raw_decode(raw_str)
        return data
    except Exception:
        return json.loads(bytes(raw_bytes))

def verify_sensor(config):
    """Verify a single sensor's database."""
    sensor_name = config["sensor_name"]
    db_path = config["db_path"]
    target_aid = config["aid"]
    
    try:
        logging.info(f"[{sensor_name.upper()}] Targeting Database: {db_path}")
        logging.info(f"[{sensor_name.upper()}] Verifying AID: {target_aid}")

        hby = habbing.Habery(name="controller", base=db_path)

        if target_aid not in hby.kevers:
            logging.warning(f"[{sensor_name.upper()}] AID not found in Key Event Log.")
            hby.close()
            return False

        print("\n" + "="*80)
        print(f"SENSOR: {sensor_name.upper()}")
        print(f"Database: {db_path}")
        print(f"AID: {target_aid}")
        print("="*80)
        print(f"{'SEQ':<6} | {'TYPE':<6} | {'DIGEST (SAID)':<48} | {'PAYLOAD'}")
        print("-" * 80)

        # Clone iterator for read-only access
        kel_iter = hby.db.clonePreIter(pre=target_aid, fn=0)
        events = list(kel_iter)
        
        for raw_event in events:
            data = parse_event(raw_event)
            
            seq = int(data.get('s', '0'), 16) if isinstance(data.get('s'), str) else data.get('s', 0)
            msg_type = data.get('t', 'unknown')
            digest = data.get('d', 'N/A')
            payload_data = data.get('a', [])
            
            if isinstance(payload_data, list) and len(payload_data) > 0:
                payload = str(payload_data[0])[:15] + "..." if len(str(payload_data[0])) > 15 else str(payload_data[0])
            else:
                payload = "[]"

            print(f"{seq:<6} | {msg_type:<6} | {digest:<48} | {payload}")

        print("="*80)
        print(f"✅ {sensor_name.upper()}: {len(events)} events verified")
        print("="*80 + "\n")
        
        hby.close()
        return True

    except Exception as e:
        logging.error(f"[{sensor_name.upper()}] Verification failed: {e}")
        if 'hby' in locals():
            hby.close()
        return False

def main():
    try:
        configs = get_config()
        logging.info(f"Found {len(configs)} sensor(s) to verify")
        
        print("\n" + "="*80)
        print("KERI Multi-Sensor Verifier")
        print(f"Verifying {len(configs)} sensor(s)")
        print("="*80)
        
        success_count = 0
        for config in configs:
            if verify_sensor(config):
                success_count += 1
        
        print("\n" + "="*80)
        print(f"Verification Summary: {success_count}/{len(configs)} sensor(s) verified successfully")
        print("="*80 + "\n")
        
        if success_count == len(configs):
            logging.info("All sensors verified. Chain integrity confirmed.")
        else:
            logging.warning(f"Only {success_count} out of {len(configs)} sensors verified successfully.")

    except Exception as e:
        logging.error(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()