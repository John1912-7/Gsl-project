import json
from datetime import datetime
from pathlib import Path

SESSION_FILE = "scan_session.json"


def create_session_entry(result: dict) -> dict:
    """
    Creates a single session history entry from a scan result.
    Includes timestamp, code, decision, and reason if applicable.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "code": result.get("code"),
        "decision": result.get("decision"),
        "reason": result.get("reason") or ""
    }


def load_session() -> list:
    """
    Loads existing session history from JSON file.
    Returns empty list if file does not exist.
    """
    if not Path(SESSION_FILE).exists():
        return []

    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def save_session(session: list):
    """
    Saves full session history to JSON file.
    """
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)


def append_to_session(result: dict):
    """
    Adds a single scan result to the session history file.
    """
    session = load_session()
    entry = create_session_entry(result)
    session.append(entry)
    save_session(session)


def reset_session():
    """
    Clears the session history file.
    """
    save_session([])
    print("\n[OK] Session history has been reset.")
