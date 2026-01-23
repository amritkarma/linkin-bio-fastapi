"""
FastAPI Link-in-Bio Application Package
"""
import sys
from pathlib import Path

# Ensure the parent directory is in the path for absolute imports
# This allows imports to work whether the module is run directly or imported as a package
_parent_dir = Path(__file__).parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

__version__ = "1.0.0"
