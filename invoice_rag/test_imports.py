#!/usr/bin/env python3
"""
Minimal Processor Test
"""

print("Starting minimal processor...")

try:
    import os
    print("✓ os imported")
    
    import json  
    print("✓ json imported")
    
    from dotenv import load_dotenv
    print("✓ dotenv imported")
    load_dotenv()
    print("✓ dotenv loaded")
    
    from pydantic import BaseModel
    print("✓ pydantic imported")
    
    from groq import Groq
    print("✓ groq imported")
    
    print("All imports successful!")
    
    # Check API key
    api_key = os.environ.get("GROQ_API_KEY")
    print(f"API key exists: {bool(api_key)}")
    
    # Check for images
    if os.path.exists("invoices"):
        images = [f for f in os.listdir("invoices") if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"Found {len(images)} images: {images}")
    else:
        print("invoices directory not found")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    print("Main block executed!")
