import sys
from pathlib import Path

# Ensure src is importable for all tests
SRC = Path(__file__).parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Prevent pytest from trying to collect the E2E script as tests
collect_ignore = [
    "test_e2e.py",
]
