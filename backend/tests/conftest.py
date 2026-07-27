import sys
import os

# Ensure the backend root is in sys.path so we can import 'agents', 'shared', 'app'
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
