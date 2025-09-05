#!/usr/bin/env python3
"""Test processor execution"""

print("=== TESTING PROCESSOR ===")

# Test 1: Check if __name__ is working
print(f"Running as: {__name__}")

# Test 2: Import and check
try:
    print("Importing processor...")
    import src.processor as processor
    print("Import successful!")
    
    print("Calling main() directly...")
    processor.main()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
