"""Compare candidate methods from app.domains on the same data and metrics; append one row per run to docs/06_experiments.md.
Replace the body for the task. Keep: same input, same metrics (incl. max/p95/mean), runtime, constraint violations.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    print("experiment: no domain candidates yet (add app/domains/<problem>/ and edit this script)")
