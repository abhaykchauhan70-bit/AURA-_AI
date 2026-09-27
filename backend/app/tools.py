"""Tool registry with declarative metadata; no arbitrary host command execution."""
from pathlib import Path
import pandas as pd

TOOLS = {
    "csv_profile": {"description": "Profile an uploaded CSV or Excel workbook", "risk": "LOW", "permission": "file:read", "timeout_seconds": 30},
    "document_search": {"description": "Search text extracted from the user's documents", "risk": "LOW", "permission": "file:read", "timeout_seconds": 5},
}

def profile_table(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".csv": df = pd.read_csv(path, nrows=100000)
    elif suffix in (".xlsx", ".xls"): df = pd.read_excel(path, nrows=100000)
    else: raise ValueError("Data profiling supports CSV and XLSX files")
    numeric = df.select_dtypes(include="number")
    return {"rows": int(len(df)), "columns": int(len(df.columns)), "column_names": [str(c) for c in df.columns],
        "missing_values": {str(k): int(v) for k, v in df.isna().sum().items()}, "duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": numeric.describe().round(3).to_dict()}

def search_text(text: str, query: str, limit: int = 5) -> list[str]:
    chunks = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    terms = set(query.lower().split())
    return sorted(chunks, key=lambda s: len(terms.intersection(s.lower().split())), reverse=True)[:limit]
