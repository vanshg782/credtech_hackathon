# backend/ingestion.py
from datetime import datetime
import pandas as pd

# Structured sources (CSV/API stubs)
def fetch_structured_data() -> pd.DataFrame:
    # Example stub: rows = issuer_name, asset_class, financial metrics
    data = [
        {"issuer":"ABC Bank", "asset_class":"Financials", "revenue": 1200, "debt": 300, "cash": 200, "date": datetime.utcnow()},
        {"issuer":"XYZ Steel", "asset_class":"Materials", "revenue": 900, "debt": 500, "cash": 100, "date": datetime.utcnow()},
    ]
    return pd.DataFrame(data)

# Unstructured (news) — later swap for real API
def fetch_unstructured_data() -> list[dict]:
    return [
        {"issuer":"ABC Bank", "source":"stub_news", "headline":"Capital adequacy improves", "sentiment": 0.35, "date": datetime.utcnow()},
        {"issuer":"XYZ Steel", "source":"stub_news", "headline":"Input costs rising", "sentiment": -0.22, "date": datetime.utcnow()},
    ]
