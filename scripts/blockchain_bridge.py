"""
Fixed Blockchain Bridge for KERI Drone Sensors
Compatible with Web3.py v6.x
"""

import os
import json
import time
import logging
from web3 import Web3
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [BRIDGE] - %(message)s',
    datefmt='%H:%M:%S'
)

# ============================================
# CONFIGURATION
# ============================================

# Your 3 drone sensors
SENSORS = ["drone_sensor_1", "drone_sensor_2", "drone_sensor_3"]

# Anchor files created by your drones
ANCHOR_FILES = {
    "drone_sensor_1": "blockchain_anchor_drone_sensor_1.json",
    "drone_sensor_2": "blockchain_anchor_drone_sensor_2.json",
    "drone_sensor_3": "blockchain_anchor_drone_sensor_3.json"
}

# Load from .env file
RPC_URL = os.getenv('RPC_URL', 'http://127.0.0.1:8545')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')

# Simple contract ABI (only 2 functions we need)
CONTRACT_ABI = [
    {
        "inputs": [
            {"name": "aid", "type": "string"},
            {"name": "sequence", "type": "uint256"},
            {"name": "hash", "type": "string"}
        ],
        "name": "registerAnchor",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "aid", "type": "string"},
            {"name": "sequence", "type": "uint256"}
        ],
        "name": "getAnchor",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "aid", "type": "string"},
            {"indexed": False, "name": "sequence", "type": "uint256"},
            {"indexed": False, "name": "hash", "type": "string"}
        ],
        "name": "AnchorRegistered",
        "type": "event"
    }
]


class BlockchainBridge:
    """
    Simple bridge: watches anchor files, sends to blockchain
    """
    
    def __init__(self):
        # Track last sequence we've seen for each drone
        self.last_sequences = {sensor: -1 for sensor in SENSORS}
        
        # Connect to Hardhat
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if not self.w3.is_connected():
            raise ConnectionError("Cannot connect to blockchain! Is Hardhat running?")
        
        # Load account from private key
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        
        # Load smart contract
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=CONTRACT_ABI
        )
        
        # Print status
        logging.info("="*60)
        logging.info("✅ Connected to blockchain")
        logging.info(f"   RPC: {RPC_URL}")
        logging.info(f"   Contract: {CONTRACT_ADDRESS}")
        logging.info(f"   Account: {self.account.address}")
        logging.info("="*60)
    
    def submit_anchor(self, sensor_name, data):
        """
        Send one anchor to blockchain
        """
        aid = data['aid']
        seq = data['seq']
        said = data['said']
        
        logging.info(f"[{sensor_name.upper()}] New event #{seq}")
        
        try:
            # Get nonce (transaction counter)
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Build transaction
            txn = self.contract.functions.registerAnchor(
                aid, seq, said
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
            
            # Send transaction (FIXED: use raw_transaction, not rawTransaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logging.info(f"[{sensor_name.upper()}] ✅ Anchored in block {receipt.blockNumber}")
            else:
                logging.error(f"[{sensor_name.upper()}] ❌ Transaction failed")
                
        except Exception as e:
            logging.error(f"[{sensor_name.upper()}] Error: {e}")
    
    def run(self):
        """
        Main loop: watch files, send transactions
        """
        logging.info("Monitoring drone sensors...")
        logging.info("Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Check each drone sensor
                for sensor_name in SENSORS:
                    anchor_file = ANCHOR_FILES[sensor_name]
                    
                    # Skip if file doesn't exist yet
                    if not os.path.exists(anchor_file):
                        continue
                    
                    # Read anchor file
                    try:
                        with open(anchor_file, "r") as f:
                            data = json.load(f)
                    except:
                        continue  # File might be mid-write
                    
                    # Get sequence number
                    seq = data.get('seq')
                    
                    # If new event, send to blockchain
                    if seq and seq > self.last_sequences[sensor_name]:
                        self.submit_anchor(sensor_name, data)
                        self.last_sequences[sensor_name] = seq
                
                # Sleep 1 second between checks
                time.sleep(1)
                
            except KeyboardInterrupt:
                logging.info("\n" + "="*60)
                logging.info("Stopping bridge...")
                logging.info("="*60)
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                time.sleep(1)


def main():
    # Check configuration
    if not PRIVATE_KEY:
        logging.error("❌ Missing PRIVATE_KEY in .env file!")
        logging.error("Create .env with:")
        logging.error("  RPC_URL=http://127.0.0.1:8545")
        logging.error("  PRIVATE_KEY=0x...")
        logging.error("  CONTRACT_ADDRESS=0x...")
        return
    
    if not CONTRACT_ADDRESS:
        logging.error("❌ Missing CONTRACT_ADDRESS in .env file!")
        logging.error("Deploy contract first:")
        logging.error("  cd blockchain")
        logging.error("  npx hardhat run scripts/deploy.js --network localhost")
        return
    
    # Create and run bridge
    try:
        bridge = BlockchainBridge()
        bridge.run()
    except Exception as e:
        logging.error(f"❌ Bridge failed to start: {e}")


if __name__ == "__main__":
    main()