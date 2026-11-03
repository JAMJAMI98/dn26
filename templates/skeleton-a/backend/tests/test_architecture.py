"""domains must stay pure: no imports of outer layers, web/DB frameworks, or file/env access helpers."""
import re
from pathlib import Path

FORBIDDEN = re.compile(r"^\s*(from|import)\s+(app\.infrastructure|app\.presentation|fastapi|sqlalchemy|starlette)\b", re.M)


def test_domains_are_pure():
    root = Path(__file__).resolve().parents[1] / "app" / "domains"
    bad = [f"{p.relative_to(root)}" for p in root.rglob("*.py") if FORBIDDEN.search(p.read_text(encoding="utf-8"))]
    assert not bad, f"domains import outer layers: {bad}"
