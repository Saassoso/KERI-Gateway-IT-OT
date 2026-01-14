# scripts/utils.py
import os
import sys
import ctypes
import logging

def load_libsodium():
    """Handles the Windows-specific DLL loading for KERI."""
    if sys.platform == 'win32':
        # 1. Calculate the path to keri-env/Scripts/libsodium.dll relative to this file
        #    This file is in [ROOT]/scripts/utils.py
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        project_root = os.path.dirname(script_dir)              
        libsodium_dir = os.path.join(project_root, 'keri-env', 'Scripts')
        libsodium_path = os.path.join(libsodium_dir, 'libsodium.dll')
        
        # 2. Check if the DLL exists
        if os.path.exists(libsodium_path):
            # 3. CRITICAL: Add to System PATH so pysodium can find it automatically
            os.environ['PATH'] = libsodium_dir + os.pathsep + os.environ['PATH']
            
            try:
                # 4. Explicitly load it to be safe
                os.add_dll_directory(libsodium_dir)
                ctypes.CDLL(libsodium_path)
            except Exception as e:
                logging.warning(f"Could not explicitly load libsodium: {e}")
        else:
            logging.error(f"libsodium.dll NOT found at: {libsodium_path}")
            logging.error("Make sure you are running inside the keri-env virtual environment.")