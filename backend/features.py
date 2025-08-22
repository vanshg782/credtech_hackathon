# backend/features.py
import pandas as pd

def extract_features(df_struct: pd.DataFrame, news: list[dict]) -> pd.DataFrame:
    news_df = pd.DataFrame(news)
    # Aggregate news sentiment per issuer (fallback to 0 if none)
    sent = news_df.groupby("issuer")["sentiment"].mean().rename("news_sentiment") if not news_df.empty else pd.Series(dtype=float)

    df = df_struct.copy()
    if not sent.empty:
        df = df.merge(sent, left_on="issuer", right_index=True, how="left")
    df["news_sentiment"] = df["news_sentiment"].fillna(0.0)

    # Example ratio features
    df["debt_to_revenue"] = (df["debt"] / df["revenue"]).replace([float("inf")], 0).fillna(0)
    df["cash_ratio"] = (df["cash"] / (df["debt"] + 1e-6))

    # Final feature set
    feat_cols = ["revenue", "debt", "cash", "debt_to_revenue", "cash_ratio", "news_sentiment"]
    return df[["issuer", "asset_class"] + feat_cols]
