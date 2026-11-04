"""Run: cd backend && python3 -m app  (binds 0.0.0.0:PORT, default 3000). Standard library only."""
from app.main import serve

if __name__ == "__main__":
    serve()
