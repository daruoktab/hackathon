"""
pytest configuration file for the test suite.

This configuration ensures that the src/ module can be properly imported
in all test files without needing to modify sys.path in each test file.
"""

import sys
from pathlib import Path

# Add the parent directory (invoice_rag/) to the Python path
# This allows imports like 'from src.database import ...'
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
