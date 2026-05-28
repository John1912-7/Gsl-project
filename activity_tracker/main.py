import argparse
import json
import os
from datetime import datetime, timedelta

My_Data = "data.json"
Config_File = "config.json"
Status = ["completed", "skipped", "progress"]

DEFAULT_CONFIG = {
    "default_range_days": 7,
    "default_display_mode": "enabled_only"
}


def load_config() -> dict:
    if not os.path.exists(Config_File):
        return DEFAULT_CONFIG.copy()
    try:
        with open(Config_File, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Fill missing keys with defaults
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except json.JSONDecodeError:
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    with open(Config_File, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def set_config(key: str, value: str):
    allowed_keys = list(DEFAULT_CONFIG.keys())
    if key not in allowed_keys:
        print(f"Unknown config key '{key}'. Allowed: {allowed_keys}")
        return

    config = load_config()

    if key == "default_range_days":
        try:
            config[key] = int(value)
            print(f"Set '{key}' to {value}")
        except ValueError:
            print("Value must be an integer.")
            return

    elif key == "default_display_mode":
        if value not in ("enabled_only", "all"):
            print("Value must be 'enabled_only' or 'all'.")
            return
        config[key] = value
        print(f"Set '{key}' to '{value}'")

    save_config(config)


def show_config():
    config = load_config()
    print("\n--- Configuration ---")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()


def load_data():
    if not os.path.exists(My_Data):
        return {"activities": [], "checkins": []}
    try:
        with open(My_Data, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"activities": [], "checkins": []}


def save_data(data):
    with open(My_Data, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def generate_id(activities):
    if not activities:
        return 1
    return max(activity["id"] for activity in activities) + 1


def add(name):
    data = load_data()
    for activity in data["activities"]:
        if activity["name"].lower() == name.lower():
            print("Activity already exists.")
            return
    activity = {
        "id": generate_id(data["activities"]),
        "name": name,
        "enabled": True
    }
    data["activities"].append(activity)
    save_data(data)
    print(f"Added activity [{activity['id']}] {activity['name']}")


def list_activities():
    data = load_data()
    if not data["activities"]:
        print("No activities found.")
        return
    print("\nActivities:")
    for activity in data["activities"]:
        status = "Enabled" if activity.get("enabled", True) else "Disabled"
        print(f"{activity['id']}: {activity['name']} ({status})")


def remove(activity_id):
    data = load_data()
    original_count = len(data["activities"])
    data["activities"] = [
        a for a in data["activities"] if a["id"] != activity_id
    ]
    if len(data["activities"]) == original_count:
        print("Activity not found.")
        return
    save_data(data)
    print(f"Removed activity {activity_id}")


def rename(activity_id, new_name):
    data = load_data()
    for activity in data["activities"]:
        if activity["name"].lower() == new_name.lower():
            print("Activity name already exists.")
            return
    found = False
    for activity in data["activities"]:
        if activity["id"] == activity_id:
            activity["name"] = new_name
            found = True
    if not found:
        print("Activity not found.")
        return
    for checkin in data["checkins"]:
        for activity in checkin["activities"]:
            if activity["id"] == activity_id:
                activity["name"] = new_name
    save_data(data)
    print(f"Renamed activity {activity_id} to '{new_name}'")


def disable(activity_id):
    data = load_data()
    for activity in data["activities"]:
        if activity["id"] == activity_id:
            if not activity.get("enabled", True):
                print("Activity already disabled.")
                return
            activity["enabled"] = False
            save_data(data)
            print(f"Disabled activity {activity_id}")
            return
    print("Activity not found.")


def enable(activity_id):
    data = load_data()
    for activity in data["activities"]:
        if activity["id"] == activity_id:
            if activity.get("enabled", True):
                print("Activity already enabled.")
                return
            activity["enabled"] = True
            save_data(data)
            print(f"Enabled activity {activity_id}")
            return
    print("Activity not found.")


def status_valid(status):
    return status in Status


def progress_valid(progress):
    return 0 <= progress <= 100


def daily_checkin():
    data = load_data()
    if not data["activities"]:
        print("No activities available.")
        return
    today = datetime.now().strftime("%Y-%m-%d")
    for checkin in data["checkins"]:
        if checkin["date"] == today:
            print("Check-in for today already exists.")
            return
    session = {"date": today, "activities": []}
    print(f"\nDaily Check-in ({today})")
    for activity in data["activities"]:
        if not activity.get("enabled", True):
            continue
        print(f"\nActivity: {activity['name']}")
        status = input("Enter status (completed/skipped/progress): ").strip().lower()
        while not status_valid(status):
            print("Invalid status.")
            status = input("Enter valid status: ").strip().lower()
        if status == "completed":
            progress = 100
        elif status == "skipped":
            progress = 0
        else:
            while True:
                try:
                    progress = int(input("Enter progress (0-100): "))
                    if progress_valid(progress):
                        break
                    print("Progress must be between 0 and 100.")
                except ValueError:
                    print("Invalid number.")
        session["activities"].append({
            "id": activity["id"],
            "name": activity["name"],
            "status": status,
            "progress": progress
        })
    data["checkins"].append(session)
    note = input("\nAdd a note for today (press Enter to skip): ").strip()
    if note:
        data["checkins"][-1]["note"] = note
    save_data(data)
    print("\nDaily check-in saved successfully.")


# TASK 8: filter_ids and only_enabled params
def daily_sum(filter_ids=None, only_enabled=True):
    data = load_data()
    if not data["checkins"]:
        print("No check-ins found.")
        return
    latest = data["checkins"][-1]
    print(f"\nDaily Summary ({latest['date']})")
    total_progress = 0
    total_activities = 0
    enabled_ids = {
        a["id"] for a in data["activities"] if a.get("enabled", True)
    }
    for activity in latest["activities"]:
        if only_enabled and activity["id"] not in enabled_ids:
            continue
        if filter_ids and activity["id"] not in filter_ids:
            continue
        print(
            f"{activity['name']} | "
            f"Status: {activity['status']} | "
            f"Progress: {activity['progress']}%"
        )
        total_progress += activity["progress"]
        total_activities += 1
    if total_activities == 0:
        print("\nNo activities match the filter.")
        return
    average = total_progress / total_activities
    print(f"\nDaily Completion: {average:.2f}%")


# TASK 8: filter_ids and only_enabled params
def weekly_sum(filter_ids=None, only_enabled=None):
    config = load_config()

    if only_enabled is None:
        only_enabled = config["default_display_mode"] == "enabled_only"

    range_days = config["default_range_days"]

    data = load_data()
    if not data["checkins"]:
        print("No check-ins found.")
        return
    today = datetime.now()
    cutoff = today - timedelta(days=range_days)
    weekly_checkins = [
        c for c in data["checkins"]
        if datetime.strptime(c["date"], "%Y-%m-%d") >= cutoff
    ]
    if not weekly_checkins:
        print(f"No check-ins for the last {range_days} days.")
        return
    print(f"\nSummary (last {range_days} days)")
    total_progress = 0
    total_activities = 0
    enabled_ids = {
        a["id"] for a in data["activities"] if a.get("enabled", True)
    }
    for checkin in weekly_checkins:
        print(f"\nDate: {checkin['date']}")
        for activity in checkin["activities"]:
            if only_enabled and activity["id"] not in enabled_ids:
                continue
            if filter_ids and activity["id"] not in filter_ids:
                continue
            print(
                f"{activity['name']} | "
                f"{activity['status']} | "
                f"{activity['progress']}%"
            )
            total_progress += activity["progress"]
            total_activities += 1
    if total_activities == 0:
        print("\nNo activities match the filter.")
        return
    average = total_progress / total_activities
    print(f"\nAverage Completion: {average:.2f}%")


def progress_table():
    data = load_data()
    if not data["checkins"]:
        print("No check-ins found.")
        return
    all_dates = sorted(set(c["date"] for c in data["checkins"]))[-7:]
    enabled_activities = [
        a for a in data["activities"] if a.get("enabled", True)
    ]
    if not enabled_activities:
        print("No enabled activities found.")
        return
    lookup = {}
    for checkin in data["checkins"]:
        if checkin["date"] in all_dates:
            lookup[checkin["date"]] = {
                a["id"]: a["progress"] for a in checkin["activities"]
            }
    col_w = 10
    name_w = 16
    header = f"{'Date':<{name_w}}"
    for activity in enabled_activities:
        header += f"{activity['name'][:col_w]:^{col_w}}"
    print("\n" + header)
    print("-" * (name_w + col_w * len(enabled_activities)))
    for date in all_dates:
        row = f"{date:<{name_w}}"
        day_data = lookup.get(date, {})
        for activity in enabled_activities:
            value = day_data.get(activity["id"], None)
            cell = f"{value}%" if value is not None else "-"
            row += f"{cell:^{col_w}}"
        print(row)
    print()


# TASK 7: daily recap
def daily_recap(date: str):
    data = load_data()
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return
    checkin = next(
        (c for c in data["checkins"] if c["date"] == date), None
    )
    if not checkin:
        print(f"No check-in found for {date}.")
        return
    print(f"\n{'=' * 40}")
    print(f"  DAILY RECAP — {date}")
    print(f"{'=' * 40}")
    if not checkin["activities"]:
        print("No activities recorded.")
    else:
        for activity in checkin["activities"]:
            print(
                f"  {activity['name']:<16} | "
                f"{activity['status']:<10} | "
                f"{activity['progress']}%"
            )
    note = checkin.get("note", "")
    print(f"\n  Note: {note if note else '—'}")
    print(f"{'=' * 40}\n")


# TASK 5: report
def generate_report(date_from: str, date_to: str):
    data = load_data()
    try:
        from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        to_dt = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return
    if from_dt > to_dt:
        print("Start date must be before end date.")
        return
    filtered = [
        c for c in data["checkins"]
        if date_from <= c["date"] <= date_to
    ]
    if not filtered:
        print(f"No check-ins found between {date_from} and {date_to}.")
        return
    total_scans = 0
    total_progress = 0
    activity_stats = {}
    enabled_ids = {
        a["id"] for a in data["activities"] if a.get("enabled", True)
    }
    for checkin in filtered:
        for activity in checkin["activities"]:
            if activity["id"] not in enabled_ids:
                continue
            aid = activity["id"]
            if aid not in activity_stats:
                activity_stats[aid] = {
                    "name": activity["name"],
                    "total_progress": 0,
                    "count": 0,
                    "statuses": []
                }
            activity_stats[aid]["total_progress"] += activity["progress"]
            activity_stats[aid]["count"] += 1
            activity_stats[aid]["statuses"].append(activity["status"])
            total_progress += activity["progress"]
            total_scans += 1
    average = total_progress / total_scans if total_scans > 0 else 0
    report = {
        "generated_at": datetime.now().isoformat(),
        "range": {"from": date_from, "to": date_to},
        "total_checkins": len(filtered),
        "overall_average_progress": round(average, 2),
        "activities": [
            {
                "id": aid,
                "name": stats["name"],
                "average_progress": round(stats["total_progress"] / stats["count"], 2),
                "checkin_count": stats["count"],
                "statuses": stats["statuses"]
            }
            for aid, stats in activity_stats.items()
        ],
        "daily_notes": [
            {"date": c["date"], "note": c.get("note", "")}
            for c in filtered if c.get("note")
        ]
    }
    filename = f"report_{date_from}_{date_to}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    print(f"\nReport saved to '{filename}'")
    print(f"Range          : {date_from} → {date_to}")
    print(f"Total check-ins: {len(filtered)}")
    print(f"Overall average: {average:.2f}%")


# TASK 6: add note
def add_note(date: str, note: str):
    data = load_data()
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return
    for checkin in data["checkins"]:
        if checkin["date"] == date:
            checkin["note"] = note
            save_data(data)
            print(f"Note added to check-in on {date}.")
            return
    print(f"No check-in found for {date}.")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("name")

    subparsers.add_parser("list")

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("id", type=int)

    rename_parser = subparsers.add_parser("rename")
    rename_parser.add_argument("id", type=int)
    rename_parser.add_argument("new_name")

    disable_parser = subparsers.add_parser("disable")
    disable_parser.add_argument("id", type=int)

    enable_parser = subparsers.add_parser("enable")
    enable_parser.add_argument("id", type=int)

    subparsers.add_parser("checkin")

    daily_parser = subparsers.add_parser("daily")
    daily_parser.add_argument("--ids", nargs="+", type=int)
    daily_parser.add_argument("--all", dest="all_activities", action="store_true")

    weekly_parser = subparsers.add_parser("weekly")
    weekly_parser.add_argument("--ids", nargs="+", type=int)
    weekly_parser.add_argument("--all", dest="all_activities", action="store_true")

    subparsers.add_parser("table")

    recap_parser = subparsers.add_parser("recap")
    recap_parser.add_argument("date")

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--from", dest="date_from", required=True)
    report_parser.add_argument("--to", dest="date_to", required=True)

    note_parser = subparsers.add_parser("note")
    note_parser.add_argument("date")
    note_parser.add_argument("note")

    config_parser = subparsers.add_parser("config")
    config_parser.add_argument("--set-key", dest="key")
    config_parser.add_argument("--set-value", dest="value")
    config_parser.add_argument("--show", action="store_true")

    args = parser.parse_args()

    if args.command is None:
        args.command = "list"

    if args.command == "add":
        add(args.name)
    elif args.command == "list":
        list_activities()
    elif args.command == "remove":
        remove(args.id)
    elif args.command == "rename":
        rename(args.id, args.new_name)
    elif args.command == "disable":
        disable(args.id)
    elif args.command == "enable":
        enable(args.id)
    elif args.command == "checkin":
        daily_checkin()
    elif args.command == "daily":
        filter_ids = set(args.ids) if args.ids else None
        daily_sum(filter_ids=filter_ids, only_enabled=not args.all_activities)
    elif args.command == "weekly":
        filter_ids = set(args.ids) if args.ids else None
        weekly_sum(filter_ids=filter_ids, only_enabled=not args.all_activities)
    elif args.command == "table":
        progress_table()
    elif args.command == "recap":
        daily_recap(args.date)
    elif args.command == "report":
        generate_report(args.date_from, args.date_to)
    elif args.command == "note":
        add_note(args.date, args.note)
    elif args.command == "config":
        if args.show:
            show_config()
        elif args.key and args.value:
            set_config(args.key, args.value)
        else:
            show_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
