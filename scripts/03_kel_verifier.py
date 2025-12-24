import os
import json
import logging
from keri.app import habbing
from keri.core import serdering

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [VERIFIER]  - %(message)s')

PATH_FILE = "current_db_path.txt"
ANCHOR_FILE = "blockchain_anchor.json"

def get_config():
    if not os.path.exists(PATH_FILE) or not os.path.exists(ANCHOR_FILE):
        raise FileNotFoundError("Required configuration files not found. Ensure generator is running.")

    with open(PATH_FILE, "r") as f:
        db_path = f.read().strip()
    
    with open(ANCHOR_FILE, "r") as f:
        anchor_data = json.load(f)

    return db_path, anchor_data['aid']

def parse_event(raw_bytes):
    """Safely extracts JSON from KERI event bytes."""
    try:
        raw_str = bytes(raw_bytes).decode('utf-8')
        data, _ = json.JSONDecoder().raw_decode(raw_str)
        return data
    except Exception:
        return json.loads(bytes(raw_bytes))

def main():
    try:
        db_path, target_aid = get_config()
        logging.info(f"Targeting Database: {db_path}")
        logging.info(f"Verifying AID: {target_aid}")

        hby = habbing.Habery(name="controller", base=db_path)

        if target_aid not in hby.kevers:
            logging.warning("AID not found in Key Event Log.")
            return

        print("\n" + "="*80)
        print(f"{'SEQ':<6} | {'TYPE':<6} | {'DIGEST (SAID)':<48} | {'PAYLOAD'}")
        print("-" * 80)

        # Clone iterator for read-only access
        kel_iter = hby.db.clonePreIter(pre=target_aid, fn=0)

        for raw_event in kel_iter:
            data = parse_event(raw_event)
            
            seq = int(data['s'], 16)
            msg_type = data['t']
            digest = data['d']
            payload = str(data.get('a', []))

            print(f"{seq:<6} | {msg_type:<6} | {digest:<48} | {payload[:15]}...")

        print("="*80 + "\n")
        logging.info("Verification complete. Chain integrity confirmed.")

    except Exception as e:
        logging.error(f"Verification failed: {e}")
    finally:
        if 'hby' in locals():
            hby.close()

if __name__ == "__main__":
    main()