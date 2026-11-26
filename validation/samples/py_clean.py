"""Secure counterparts of every vulnerable pattern: should produce no findings."""
import hashlib
import json
import os
import secrets
import sqlite3
import subprocess
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", "app.db")
API_KEY = os.getenv("API_KEY")


def find_user(name):
    """Return rows for a user using a parameterized query."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cur.fetchall()


def ping(host):
    """Ping a validated host without invoking a shell."""
    if not host.replace(".", "").replace("-", "").isalnum():
        raise ValueError("invalid host")
    return subprocess.run(["ping", "-c", "1", host], shell=False, check=True)


def new_token():
    """Create an unpredictable token."""
    return secrets.token_hex(16)


def hash_file(path):
    """Hash a file with SHA-256."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_config(text):
    """Parse configuration safely."""
    return json.loads(text)


def verify(stored_hash, supplied_hash):
    """Compare hashes in constant time."""
    return secrets.compare_digest(stored_hash, supplied_hash)


def classify(score):
    """Small, flat decision logic."""
    if score < 0:
        return "invalid"
    if score < 50:
        return "low"
    if score < 80:
        return "medium"
    return "high"
