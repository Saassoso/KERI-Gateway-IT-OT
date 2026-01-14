# gateway/scripts/utils.py
import os
import sys
import ctypes
import logging

def load_libsodium():
    if sys.platform == 'win32':
        # Calculate path:
        # File is at: KERI-IT-OT-System/gateway/scripts/utils.py
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        gateway_dir = os.path.dirname(script_dir)     # .../gateway
        project_root = os.path.dirname(gateway_dir)   # .../KERI-IT-OT-System (ROOT)
        
        # Look for keri-env in the ROOT folder
        libsodium_dir = os.path.join(project_root, 'keri-env', 'Scripts')
        libsodium_path = os.path.join(libsodium_dir, 'libsodium.dll')
        
        if os.path.exists(libsodium_path):
            os.environ['PATH'] = libsodium_dir + os.pathsep + os.environ['PATH']
            try:
                os.add_dll_directory(libsodium_dir)
                ctypes.CDLL(libsodium_path)
            except Exception as e:
                logging.warning(f"Could not load libsodium: {e}")