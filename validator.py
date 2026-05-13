import pandas as pd
from models import Category, Status


REQUIRED_COLUMNS = ["code", "category", "status"]
ALLOWED_STATUSES = [s.value for s in Status]
ALLOWED_CATEGORIES = [c.value for c in Category]


def validate_csv(filepath: str) -> pd.DataFrame:
    """
    Loads and validates the ticket CSV file.
    Raises ValueError with a clear message if validation fails.
    Returns a clean DataFrame if everything is valid.
    """

    # --- Load file ---
    try:
        df = pd.read_csv(filepath, dtype=str)
    except FileNotFoundError:
        raise ValueError(f"File not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Could not read CSV file: {e}")

    # --- Check required columns ---
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # --- Strip whitespace ---
    df[REQUIRED_COLUMNS] = df[REQUIRED_COLUMNS].apply(lambda col: col.str.strip())

    # --- Check empty required fields ---
    for col in REQUIRED_COLUMNS:
        empty_rows = df[df[col].isna() | (df[col] == "")].index.tolist()
        if empty_rows:
            raise ValueError(f"Empty values found in column '{col}' at rows: {[r + 2 for r in empty_rows]}")

    # --- Check duplicate codes ---
    duplicates = df[df["code"].duplicated()]["code"].tolist()
    if duplicates:
        raise ValueError(f"Duplicate ticket codes found: {duplicates}")

    # --- Check allowed status values ---
    invalid_statuses = df[~df["status"].isin(ALLOWED_STATUSES)]["status"].unique().tolist()
    if invalid_statuses:
        raise ValueError(f"Invalid status values found: {invalid_statuses}. Allowed: {ALLOWED_STATUSES}")

    # --- Check allowed category values ---
    invalid_categories = df[~df["category"].isin(ALLOWED_CATEGORIES)]["category"].unique().tolist()
    if invalid_categories:
        raise ValueError(f"Invalid category values found: {invalid_categories}. Allowed: {ALLOWED_CATEGORIES}")

    # --- Check code format (must be 12 digits) ---
    invalid_codes = df[~df["code"].str.match(r"^\d{12}$")]["code"].tolist()
    if invalid_codes:
        raise ValueError(f"Invalid code format (must be 12 digits): {invalid_codes}")

    return df
