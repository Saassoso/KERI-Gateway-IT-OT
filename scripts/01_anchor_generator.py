import os
import shutil
import json
import time
import uuid
import logging
from keri.app import habbing
from keri.core import serdering

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [GENERATOR] - %(message)s')

# Configuration
run_id = str(uuid.uuid4())[:8]
DB_NAME = f"keri_run_{run_id}"
ANCHOR_FILE = "blockchain_anchor.json"
PATH_FILE = "current_db_path.txt"

def main():
    logging.info(f"Initializing KERI environment: ./{DB_NAME}")
    
    # Persist DB path for verifier
    with open(PATH_FILE, "w") as f:
        f.write(DB_NAME)

    hby = habbing.Habery(name="controller", base=DB_NAME)

    try:
        # Create Sensor Identity
        sensor = hby.makeHab(name="drone_sensor", isith="1", icount=1)
        logging.info(f"Identity established. AID: {sensor.pre}")

        cycle = 0
        while True:
            cycle += 1
            payload = {
                "status": "ACTIVE",
                "cycle": cycle,
                "temp": 45 + (cycle % 10),
                "sector": f"SEC_{cycle}"
            }

            # Sign data (commit to KEL)
            sensor.interact(data=[payload])

            # Retrieve latest event
            # Use raw_decode to handle appended signatures safely
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

            with open(ANCHOR_FILE, "w") as f:
                json.dump(anchor, f, indent=4)

            logging.info(f"Event #{anchor['seq']} committed. Hash: {anchor['said']}")
            time.sleep(3)

    except KeyboardInterrupt:
        logging.info("Stopping generator...")
    except Exception as e:
        logging.error(f"Runtime error: {e}")
    finally:
        hby.close()
        cleanup_db()

def cleanup_db():
    if os.path.exists(DB_NAME):
        try:
            shutil.rmtree(DB_NAME)
            logging.info("Database cleaned up.")
        except PermissionError:
            logging.warning("Could not delete database (file lock active).")

if __name__ == "__main__":
    main()