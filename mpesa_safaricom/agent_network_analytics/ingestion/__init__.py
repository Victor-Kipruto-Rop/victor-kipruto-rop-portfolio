# ingestion package

# Ensure package can be imported when running tests from repo root by adding project root to sys.path
import os
import sys
_this_dir = os.path.dirname(__file__)
_repo_root = os.path.abspath(os.path.join(_this_dir, '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
