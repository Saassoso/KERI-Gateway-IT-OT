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
SENSORS = ["drone_sensor_1", "drone_sensor_2", "drone_sensor_3"]

def get_config():
    """Get configuration for all sensors from unified database."""
    configs = []
    unified_db_path = None
    
    # First, find the unified database path (all sensors use the same DB)
    for sensor_name in SENSORS:
        path_file = f"current_db_path_{sensor_name}.txt"
        if os.path.exists(path_file):
            try:
                with open(path_file, "r") as f:
                    unified_db_path = f.read().strip()
                break  # All sensors use the same DB, so we only need one path
            except Exception as e:
                logging.error(f"Error reading path file for {sensor_name}: {e}")
    
    if not unified_db_path:
        raise FileNotFoundError("Unified database path not found. Ensure at least one sensor is running.")
    
    # Now get AIDs for all sensors from their anchor files
    for sensor_name in SENSORS:
        anchor_file = f"blockchain_anchor_{sensor_name}.json"
        
        if not os.path.exists(anchor_file):
            logging.warning(f"Anchor file not found for {sensor_name}. Skipping...")
            continue
        
        try:
            with open(anchor_file, "r") as f:
                anchor_data = json.load(f)
            
            aid = anchor_data.get('aid')
            if not aid:
                logging.warning(f"AID not found in anchor file for {sensor_name}. Skipping...")
                continue
            
            configs.append({
                "sensor_name": sensor_name,
                "db_path": unified_db_path,  # All sensors use the same unified database
                "aid": aid,
                "anchor_file": anchor_file
            })
        except Exception as e:
            logging.error(f"Error reading anchor file for {sensor_name}: {e}")
            continue
    
    if not configs:
        raise FileNotFoundError("No sensor configuration found. Ensure at least one sensor is running.")
    
    logging.info(f"Unified database: {unified_db_path}")
    logging.info(f"Found {len(configs)} sensor(s) in unified database")
    
    return configs

def parse_event(raw_bytes):
    """Safely extracts JSON from KERI event bytes."""
    try:
        raw_str = bytes(raw_bytes).decode('utf-8')
        data, _ = json.JSONDecoder().raw_decode(raw_str)
        return data
    except Exception:
        return json.loads(bytes(raw_bytes))

def verify_sensor(config, hby):
    """Verify a single sensor's AID in the unified database."""
    sensor_name = config["sensor_name"]
    target_aid = config["aid"]
    
    try:
        logging.info(f"[{sensor_name.upper()}] Verifying AID: {target_aid}")

        if target_aid not in hby.kevers:
            logging.warning(f"[{sensor_name.upper()}] AID not found in unified database.")
            return False

        print("\n" + "="*80)
        print(f"SENSOR: {sensor_name.upper()}")
        print(f"AID: {target_aid}")
        print("="*80)
        print(f"{'SEQ':<6} | {'TYPE':<6} | {'DIGEST (SAID)':<48} | {'PAYLOAD'}")
        print("-" * 80)

        # Clone iterator for read-only access - data is isolated by AID
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
        
        return True

    except Exception as e:
        logging.error(f"[{sensor_name.upper()}] Verification failed: {e}")
        return False

def main():
    try:
        configs = get_config()
        
        if not configs:
            raise FileNotFoundError("No sensors to verify.")
        
        # Get unified database path (all sensors use the same DB)
        unified_db_path = configs[0]["db_path"]
        
        print("\n" + "="*80)
        print("KERI Multi-Sensor Verifier")
        print(f"Unified Database: {unified_db_path}")
        print(f"Verifying {len(configs)} sensor(s) (data isolated by AID)")
        print("="*80)
        
        # Open unified database once
        hby = habbing.Habery(name="controller", base=unified_db_path)
        
        try:
            success_count = 0
            for config in configs:
                if verify_sensor(config, hby):
                    success_count += 1
            
            print("\n" + "="*80)
            print(f"Verification Summary: {success_count}/{len(configs)} sensor(s) verified successfully")
            print("="*80 + "\n")
            
            if success_count == len(configs):
                logging.info("All sensors verified. Chain integrity confirmed.")
            else:
                logging.warning(f"Only {success_count} out of {len(configs)} sensors verified successfully.")
        
        finally:
            hby.close()

    except Exception as e:
        logging.error(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()