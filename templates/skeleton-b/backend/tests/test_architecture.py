"""domains must stay pure: no imports of outer layers, DB, HTTP server."""
import re
import unittest
from pathlib import Path

FORBIDDEN = re.compile(r"^\s*(from|import)\s+(app\.infrastructure|app\.presentation|sqlite3|http\.server)\b", re.M)


class ArchitectureTest(unittest.TestCase):
    def test_domains_are_pure(self):
        root = Path(__file__).resolve().parents[1] / "app" / "domains"
        bad = [str(p.relative_to(root)) for p in root.rglob("*.py") if FORBIDDEN.search(p.read_text(encoding="utf-8"))]
        self.assertFalse(bad, f"domains import outer layers: {bad}")


if __name__ == "__main__":
    unittest.main()
