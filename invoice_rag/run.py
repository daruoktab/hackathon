#!/usr/bin/env python3
"""
Invoice Processor Runner - Simple script to run the invoice processor
"""

import sys
import os
import subprocess

def main():
    """Main runner function."""
    processor_path = os.path.join(os.path.dirname(__file__), 'src', 'processor.py')
    
    if not os.path.exists(processor_path):
        print(f"Error: processor.py not found at {processor_path}")
        print("Make sure you're running this from the invoice_rag directory")
        sys.exit(1)
    
    # Run the processor as a subprocess
    try:
        result = subprocess.run([sys.executable, processor_path], 
                              cwd=os.path.dirname(__file__),
                              check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error running processor: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
