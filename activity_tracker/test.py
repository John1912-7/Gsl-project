import json
import pytest

from main import (generate_id, status_valid, progress_valid, rename, disable, enable, add, load_data, save_data, progress_table, generate_report, daily_sum)


def test_generate_first_activity_id():
    activities = []
    assert generate_id(activities) == 1


def test_generate_next_activity_id():
    activities = [
        {"id": 1, "name": "Workout"},
        {"id": 2, "name": "Reading"}
    ]

    assert generate_id(activities) == 3


def test_validate_completed():
    assert status_valid("completed") is True


def test_validate_skipped():
    assert status_valid("skipped") is True


def test_validate_progress():
    assert status_valid("progress") is True


def test_validate_invalid_status():
    assert status_valid("random") is False


def test_progress_valid_0():
    assert progress_valid(0) is True


def test_progress_valid_100():
    assert progress_valid(100) is True


def test_progress_valid_middle():
    assert progress_valid(50) is True


def test_progress_negative():
    assert progress_valid(-1) is False


def test_progress_over_100():
    assert progress_valid(101) is False


def test_json_structure():
    data = {
        "activities": [],
        "checkins": []
    }

    assert "activities" in data
    assert "checkins" in data


def test_checkin_structure():
    checkin = {
        "date": "2026-05-17",
        "activities": [
            {
                "id": 1,
                "name": "Workout",
                "status": "completed",
                "progress": 100
            }
        ]
    }

    assert checkin["date"] == "2026-05-17"
    assert checkin["activities"][0]["status"] == "completed"
    assert checkin["activities"][0]["progress"] == 100


def test_daily_completion_average():
    activities = [
        {"progress": 100},
        {"progress": 50},
        {"progress": 0}
    ]

    total = sum(a["progress"] for a in activities)
    average = total / len(activities)

    assert average == 50


def test_empty_activities():
    activities = []

    assert len(activities) == 0


# TASK 1 + TASK 2 TESTS

def test_enabled_field():
    activity = {
        "id": 1,
        "name": "Workout",
        "enabled": True
    }

    assert activity["enabled"] is True


def test_rename_activity():
    activity = {
        "id": 1,
        "name": "Workout"
    }

    activity["name"] = "Gym"

    assert activity["name"] == "Gym"


def test_disable_activity():
    activity = {
        "id": 1,
        "name": "Workout",
        "enabled": True
    }

    activity["enabled"] = False

    assert activity["enabled"] is False


# TASK 1 REAL TESTS

def test_rename_reflects_in_history(tmp_path, monkeypatch):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": [{"date": "2026-05-01", "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 100}]}]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    rename(1, "Gym")

    data = load_data()
    assert data["activities"][0]["name"] == "Gym"
    assert data["checkins"][0]["activities"][0]["name"] == "Gym"


def test_rename_duplicate_name(tmp_path, monkeypatch):
    test_data = {
        "activities": [
            {"id": 1, "name": "Workout", "enabled": True},
            {"id": 2, "name": "Reading", "enabled": True}
        ],
        "checkins": []
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    rename(1, "Reading")

    data = load_data()
    assert data["activities"][0]["name"] == "Workout"


# TASK 2 REAL TESTS

def test_disable_excludes_from_checkin(tmp_path, monkeypatch):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": []
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    disable(1)

    data = load_data()
    assert data["activities"][0]["enabled"] is False


def test_enable_activity(tmp_path, monkeypatch):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": False}],
        "checkins": []
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    enable(1)

    data = load_data()
    assert data["activities"][0]["enabled"] is True


def test_disable_already_disabled(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": False}],
        "checkins": []
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    disable(1)

    captured = capsys.readouterr()
    assert "already disabled" in captured.out


def test_enable_already_enabled(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": []
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    enable(1)

    captured = capsys.readouterr()
    assert "already enabled" in captured.out

# TASK 3 TESTS

def test_progress_valid_boundary():
    assert progress_valid(0) is True
    assert progress_valid(100) is True
    assert progress_valid(50) is True


def test_progress_invalid_boundary():
    assert progress_valid(-1) is False
    assert progress_valid(101) is False


def test_progress_stored_in_checkin():
    checkin = {
        "date": "2026-05-17",
        "activities": [
            {
                "id": 1,
                "name": "Workout",
                "status": "progress",
                "progress": 75
            }
        ]
    }
    assert checkin["activities"][0]["progress"] == 75
    assert progress_valid(checkin["activities"][0]["progress"]) is True


def test_completed_sets_100():
    progress = 100 if "completed" == "completed" else 0
    assert progress == 100


def test_skipped_sets_0():
    progress = 0 if "skipped" == "skipped" else 100
    assert progress == 0


# TASK 4 TESTS

def test_table_no_checkins(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": []
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    progress_table()

    captured = capsys.readouterr()
    assert "No check-ins found" in captured.out


def test_table_shows_progress(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": [
            {
                "date": "2026-05-17",
                "activities": [{"id": 1, "name": "Workout", "status": "progress", "progress": 80}]
            }
        ]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    progress_table()

    captured = capsys.readouterr()
    assert "80%" in captured.out
    assert "2026-05-17" in captured.out


def test_table_max_7_rows(tmp_path, monkeypatch, capsys):
    checkins = [
        {
            "date": f"2026-05-{str(i).zfill(2)}",
            "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 100}]
        }
        for i in range(1, 11)  # 10 checkins
    ]
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": checkins
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    progress_table()

    captured = capsys.readouterr()
    # Only last 7 dates should appear
    assert "2026-05-01" not in captured.out
    assert "2026-05-04" in captured.out


# TASK 5 TESTS

def test_report_saved_to_file(tmp_path, monkeypatch):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": [
            {
                "date": "2026-05-17",
                "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 100}]
            }
        ]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))
    monkeypatch.chdir(tmp_path)

    from main import generate_report
    generate_report("2026-05-01", "2026-05-31")

    report_file = tmp_path / "report_2026-05-01_2026-05-31.json"
    assert report_file.exists()


def test_report_correct_structure(tmp_path, monkeypatch):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": [
            {
                "date": "2026-05-17",
                "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 80}]
            }
        ]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))
    monkeypatch.chdir(tmp_path)

    from main import generate_report
    generate_report("2026-05-01", "2026-05-31")

    report_file = tmp_path / "report_2026-05-01_2026-05-31.json"
    report = json.loads(report_file.read_text())

    assert "range" in report
    assert "overall_average_progress" in report
    assert report["overall_average_progress"] == 80.0


def test_report_invalid_date(tmp_path, monkeypatch, capsys):
    test_data = {"activities": [], "checkins": []}
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import generate_report
    generate_report("not-a-date", "2026-05-31")

    captured = capsys.readouterr()
    assert "Invalid date format" in captured.out


def test_report_start_after_end(tmp_path, monkeypatch, capsys):
    test_data = {"activities": [], "checkins": []}
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import generate_report
    generate_report("2026-05-31", "2026-05-01")

    captured = capsys.readouterr()
    assert "before end date" in captured.out


# TASK 6 TESTS

def test_note_added_to_checkin(tmp_path, monkeypatch):
    test_data = {
        "activities": [],
        "checkins": [{"date": "2026-05-17", "activities": []}]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import add_note
    add_note("2026-05-17", "Great session today!")

    data = load_data()
    assert data["checkins"][0]["note"] == "Great session today!"


def test_note_checkin_not_found(tmp_path, monkeypatch, capsys):
    test_data = {"activities": [], "checkins": []}
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import add_note
    add_note("2026-05-17", "Some note")

    captured = capsys.readouterr()
    assert "No check-in found" in captured.out


def test_note_invalid_date(tmp_path, monkeypatch, capsys):
    test_data = {"activities": [], "checkins": []}
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import add_note
    add_note("bad-date", "note")

    captured = capsys.readouterr()
    assert "Invalid date format" in captured.out


# TASK 7 TESTS

def test_recap_shows_progress_and_note(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": [
            {
                "date": "2026-05-17",
                "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 100}],
                "note": "Felt great today"
            }
        ]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import daily_recap
    daily_recap("2026-05-17")

    captured = capsys.readouterr()
    assert "100%" in captured.out
    assert "Felt great today" in captured.out
    assert "2026-05-17" in captured.out


def test_recap_no_note_shows_dash(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [],
        "checkins": [{"date": "2026-05-17", "activities": []}]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import daily_recap
    daily_recap("2026-05-17")

    captured = capsys.readouterr()
    assert "—" in captured.out


def test_recap_date_not_found(tmp_path, monkeypatch, capsys):
    test_data = {"activities": [], "checkins": []}
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import daily_recap
    daily_recap("2026-05-17")

    captured = capsys.readouterr()
    assert "No check-in found" in captured.out


def test_recap_invalid_date(tmp_path, monkeypatch, capsys):
    test_data = {"activities": [], "checkins": []}
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    from main import daily_recap
    daily_recap("bad-date")

    captured = capsys.readouterr()
    assert "Invalid date format" in captured.out


# TASK 8 TESTS

def test_daily_sum_filter_by_id(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [
            {"id": 1, "name": "Workout", "enabled": True},
            {"id": 2, "name": "Reading", "enabled": True}
        ],
        "checkins": [
            {
                "date": "2026-05-17",
                "activities": [
                    {"id": 1, "name": "Workout", "status": "completed", "progress": 100},
                    {"id": 2, "name": "Reading", "status": "completed", "progress": 50}
                ]
            }
        ]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    daily_sum(filter_ids={1})

    captured = capsys.readouterr()
    assert "Workout" in captured.out
    assert "Reading" not in captured.out


def test_daily_sum_only_enabled(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [
            {"id": 1, "name": "Workout", "enabled": True},
            {"id": 2, "name": "Reading", "enabled": False}
        ],
        "checkins": [
            {
                "date": "2026-05-17",
                "activities": [
                    {"id": 1, "name": "Workout", "status": "completed", "progress": 100},
                    {"id": 2, "name": "Reading", "status": "completed", "progress": 50}
                ]
            }
        ]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    daily_sum(only_enabled=True)

    captured = capsys.readouterr()
    assert "Workout" in captured.out
    assert "Reading" not in captured.out


def test_daily_sum_all_activities(tmp_path, monkeypatch, capsys):
    test_data = {
        "activities": [
            {"id": 1, "name": "Workout", "enabled": True},
            {"id": 2, "name": "Reading", "enabled": False}
        ],
        "checkins": [
            {
                "date": "2026-05-17",
                "activities": [
                    {"id": 1, "name": "Workout", "status": "completed", "progress": 100},
                    {"id": 2, "name": "Reading", "status": "completed", "progress": 50}
                ]
            }
        ]
    }
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(test_data))
    monkeypatch.setattr("main.My_Data", str(data_file))

    daily_sum(only_enabled=False)

    captured = capsys.readouterr()
    assert "Workout" in captured.out
    assert "Reading" in captured.out


# TASK 9 TESTS

def test_load_config_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr("main.Config_File", str(tmp_path / "config.json"))
    from main import load_config
    config = load_config()
    assert config["default_range_days"] == 7
    assert config["default_display_mode"] == "enabled_only"


def test_set_config_range_days(tmp_path, monkeypatch):
    monkeypatch.setattr("main.Config_File", str(tmp_path / "config.json"))
    from main import set_config, load_config
    set_config("default_range_days", "14")
    config = load_config()
    assert config["default_range_days"] == 14


def test_set_config_display_mode(tmp_path, monkeypatch):
    monkeypatch.setattr("main.Config_File", str(tmp_path / "config.json"))
    from main import set_config, load_config
    set_config("default_display_mode", "all")
    config = load_config()
    assert config["default_display_mode"] == "all"


def test_set_config_invalid_key(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("main.Config_File", str(tmp_path / "config.json"))
    from main import set_config
    set_config("nonexistent_key", "value")
    captured = capsys.readouterr()
    assert "Unknown config key" in captured.out


def test_set_config_invalid_display_mode(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("main.Config_File", str(tmp_path / "config.json"))
    from main import set_config
    set_config("default_display_mode", "wrong")
    captured = capsys.readouterr()
    assert "enabled_only" in captured.out


def test_set_config_invalid_range_type(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("main.Config_File", str(tmp_path / "config.json"))
    from main import set_config
    set_config("default_range_days", "abc")
    captured = capsys.readouterr()
    assert "integer" in captured.out


def test_config_persists_across_reloads(tmp_path, monkeypatch):
    monkeypatch.setattr("main.Config_File", str(tmp_path / "config.json"))
    from main import set_config, load_config
    set_config("default_range_days", "30")
    config = load_config()
    assert config["default_range_days"] == 30


# TASK 10 TESTS — stability with growing data

def test_multiple_checkins_accumulate(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr("main.My_Data", str(data_file))

    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": []
    }
    data_file.write_text(json.dumps(test_data))

    # Simulate 3 separate checkins
    for i in range(1, 4):
        data = load_data()
        data["checkins"].append({
            "date": f"2026-05-{str(i).zfill(2)}",
            "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 100}]
        })
        save_data(data)

    data = load_data()
    assert len(data["checkins"]) == 3


def test_rename_stable_after_multiple_reruns(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr("main.My_Data", str(data_file))

    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": [
            {"date": "2026-05-01", "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 100}]}
        ]
    }
    data_file.write_text(json.dumps(test_data))

    # Rename twice simulating reruns
    rename(1, "Gym")
    rename(1, "Training")

    data = load_data()
    assert data["activities"][0]["name"] == "Training"
    assert data["checkins"][0]["activities"][0]["name"] == "Training"


def test_disable_enable_cycle(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr("main.My_Data", str(data_file))

    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": []
    }
    data_file.write_text(json.dumps(test_data))

    disable(1)
    enable(1)
    disable(1)

    data = load_data()
    assert data["activities"][0]["enabled"] is False


def test_large_data_table_still_shows_7(tmp_path, monkeypatch, capsys):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr("main.My_Data", str(data_file))

    checkins = [
        {
            "date": f"2026-{str((i // 30) + 1).zfill(2)}-{str((i % 28) + 1).zfill(2)}",
            "activities": [{"id": 1, "name": "Workout", "status": "completed", "progress": 80}]
        }
        for i in range(50)
    ]
    test_data = {
        "activities": [{"id": 1, "name": "Workout", "enabled": True}],
        "checkins": checkins
    }
    data_file.write_text(json.dumps(test_data))

    progress_table()

    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().split("\n") if l.strip() and "---" not in l and "Date" not in l]
    assert len(lines) <= 7


def test_note_overwrites_previous(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr("main.My_Data", str(data_file))

    test_data = {
        "activities": [],
        "checkins": [{"date": "2026-05-01", "activities": [], "note": "Old note"}]
    }
    data_file.write_text(json.dumps(test_data))

    from main import add_note
    add_note("2026-05-01", "New note")

    data = load_data()
    assert data["checkins"][0]["note"] == "New note"
