# 00_bridge.py (Debug Version)
import os
import json
import time
import logging
from web3 import Web3
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BRIDGE] - %(message)s')

def get_abi_from_build():
    # Adjusted path for your folder structure
    artifact_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'Keri-Anchor-Contract', 
        'artifacts', 
        'contracts', 
        'KERIAnchor.sol', 
        'KERIAnchor.json'
    )
    try:
        with open(artifact_path, "r") as f:
            data = json.load(f)
            return data["abi"]
    except FileNotFoundError:
        logging.error(f"❌ ABI Not Found at: {artifact_path}")
        return None

def main():
    if not PRIVATE_KEY or not CONTRACT_ADDRESS:
        logging.error("❌ Config Missing in .env")
        return

    abi = get_abi_from_build()
    if not abi:
        return

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        logging.error("❌ No Blockchain Connection")
        return

    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
        
        logging.info("="*60)
        logging.info("🌉 DEBUG BRIDGE ACTIVE")
        logging.info(f"   Contract: {CONTRACT_ADDRESS}")
        logging.info("="*60)
        
        last_seq = -1
        anchor_file = "blockchain_anchor_drone_sensor_1.json"

        while True:
            # DEBUG 1: Does file exist?
            if os.path.exists(anchor_file):
                try:
                    with open(anchor_file, "r") as f:
                        data = json.load(f)
                    
                    current_seq = data.get('seq')
                    
                    # DEBUG 2: What did we read?
                    # (Uncomment this if you want to see every read, but it will be spammy)
                    # print(f"\rReading Seq: {current_seq} (Last: {last_seq})", end="")

                    if current_seq is not None and current_seq > last_seq:
                        logging.info(f"\n⚡ Processing Event #{current_seq}...")
                        
                        tx = contract.functions.registerAnchor(
                            data['aid'],
                            data['seq'],
                            data['said']
                        ).build_transaction({
                            'from': account.address,
                            'nonce': w3.eth.get_transaction_count(account.address),
                            'gas': 500000,
                            'gasPrice': w3.eth.gas_price
                        })
                        
                        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                        
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                        logging.info(f"✅ Confirmed in Block {receipt.blockNumber}")
                        
                        last_seq = current_seq
                    
                    elif current_seq <= last_seq:
                         # Tell us why we are waiting
                         print(f"\r⏳ Waiting... (Current File Seq: {current_seq} <= Processed: {last_seq})", end="", flush=True)

                except json.JSONDecodeError:
                    print("\r⚠️ File read error (writing in progress?)", end="", flush=True)
                except Exception as e:
                    logging.error(f"\n❌ Loop Error: {e}")
            else:
                print(f"\r❌ File not found: {anchor_file}", end="", flush=True)
            
            time.sleep(1)

    except Exception as e:
        logging.error(f"Critical Error: {e}")

if __name__ == "__main__":
    main()