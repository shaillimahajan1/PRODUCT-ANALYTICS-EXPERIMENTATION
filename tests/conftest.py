"""
Pytest configuration and pythonpath setup.
"""

from pathlib import Path
import sys

# Ensure project root is on sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
