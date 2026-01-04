import os
import sys

# Fix for libsodium.dll loading on Windows
if sys.platform == 'win32':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    libsodium_path = os.path.join(script_dir, 'keri-env', 'Scripts', 'libsodium.dll')
    if os.path.exists(libsodium_path):
        os.add_dll_directory(os.path.dirname(libsodium_path))
        print(f"[OK] Added DLL directory: {os.path.dirname(libsodium_path)}")
    else:
        print(f"[ERROR] libsodium.dll not found at: {libsodium_path}")

try:
    import pysodium
    print("[OK] pysodium imported successfully!")
    
    import keri
    print("[OK] keri imported successfully!")
    
    from keri.app import habbing
    print("[OK] habbing imported successfully!")
    
    print("\n[SUCCESS] All imports working! Ready to run the scripts.")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

