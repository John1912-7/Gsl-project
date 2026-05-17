import argparse
import sys
from validator import validate_csv
from scanner import interactive_scanning_mode


def main():
    parser = argparse.ArgumentParser(
        description="Concert Ticket Scanner System",
        add_help=True
    )

    parser.add_argument(
        "--file",
        type=str,
        default="tickets.csv",
        help="Path to the ticket list CSV file"
    )

    # Subcommands (hidden from swap team documentation)
    subparsers = parser.add_subparsers(dest="mode")
    subparsers.add_parser("mode1")   # Interactive scanning
    subparsers.add_parser("mode2")   # Summary / report
    subparsers.add_parser("mode3")   # Reset session

    args = parser.parse_args()

    # --- Load and validate CSV ---
    try:
        df = validate_csv(args.file)
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    print(f"\n[OK] Loaded {len(df)} tickets from '{args.file}'")

    # --- Route to correct mode ---
    if args.mode == "mode1":
        session = interactive_scanning_mode(df, args.file)
        print(f"\nSession ended. Total scans: {len(session)}")

    elif args.mode == "mode2":
        # Task 9 — will be implemented in reports.py
        print("\n[Summary mode - coming soon]")

    elif args.mode == "mode3":
        # Task 8 — will be implemented in session.py
        print("\n[Reset mode - coming soon]")

    else:
        # No mode selected — show interactive menu
        print("\n--- TICKET SYSTEM CONTROL PANEL ---")
        print("1) Entry Scanning Mode")
        print("2) View Session Summary")
        print("3) Reset Session Data")
        print("4) Exit")

        while True:
            choice = input("\nSelect mode (1-4): ").strip()

            if choice == "1":
                session = interactive_scanning_mode(df, args.file)
                print(f"\nSession ended. Total scans: {len(session)}")
            elif choice == "2":
                print("\n[Summary mode - coming soon]")
            elif choice == "3":
                print("\n[Reset mode - coming soon]")
            elif choice == "4":
                print("Shutting down system...")
                break
            else:
                print("Invalid selection. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
