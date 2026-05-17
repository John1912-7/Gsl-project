import re
import pandas as pd
from models import Status

CODE_PATTERN = re.compile(r"^\d{12}$")


def scan_ticket(code: str, df: pd.DataFrame) -> dict:
    """
    Validates and processes a single ticket scan.
    Returns a result dict with decision and reason.
    """

    # --- Check code format ---
    if not CODE_PATTERN.match(code):
        return {
            "code": code,
            "decision": "REJECTED",
            "reason": "Invalid code format (must be 12 digits)"
        }

    # --- Check if code exists ---
    row = df[df["code"] == code]
    if row.empty:
        return {
            "code": code,
            "decision": "REJECTED",
            "reason": "Code not found in database"
        }

    # --- Check ticket status ---
    status = row.iloc[0]["status"]
    category = row.iloc[0]["category"]

    if status == Status.USED.value:
        return {
            "code": code,
            "decision": "REJECTED",
            "reason": "Ticket already used",
            "category": category
        }

    if status == Status.EXPIRED.value:
        return {
            "code": code,
            "decision": "REJECTED",
            "reason": "Ticket has expired",
            "category": category
        }

    if status == Status.VALID.value:
        # Update status to Used
        df.loc[df["code"] == code, "status"] = Status.USED.value
        return {
            "code": code,
            "decision": "ACCEPTED",
            "reason": None,
            "category": category
        }

    return {
        "code": code,
        "decision": "REJECTED",
        "reason": f"Unknown status: {status}"
    }


def print_result(result: dict):
    """Prints the scan result to the terminal."""
    print()
    if result["decision"] == "ACCEPTED":
        print(f"  >> [DECISION] : ACCEPTED ✓")
        print(f"  >> [CATEGORY] : {result.get('category', 'N/A')}")
    else:
        print(f"  >> [DECISION] : REJECTED ✗")
        print(f"  >> [REASON]   : {result['reason']}")


def interactive_scanning_mode(df: pd.DataFrame, csv_path: str) -> list:
    """
    Runs the interactive scanning loop.
    Returns session history as a list of scan results.
    """
    session_history = []

    print("\n" + "=" * 40)
    print("   INTERACTIVE SCANNING MODE")
    print("=" * 40)
    print("Type 'exit' to return to main menu.\n")

    while True:
        code = input("Enter ticket code: ").strip()

        if code.lower() == "exit":
            print("\nExiting scanning mode...")
            break

        if not code:
            print("  >> Error: Input cannot be empty.")
            continue

        result = scan_ticket(code, df)
        print_result(result)
        session_history.append(result)

    # Save updated statuses back to CSV
    df.to_csv(csv_path, index=False)

    return session_history
