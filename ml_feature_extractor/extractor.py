import pandas as pd
import numpy as np

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Robust ML feature extractor:
    - Normalizes numeric features
    - Adds positivity indicators
    - Encodes low-cardinality categoricals
    - Extracts string length from high-cardinality categoricals
    - Handles missing values
    """
    features = pd.DataFrame(index=df.index)

    # --- Numeric Features ---
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        col_data = df[col].fillna(df[col].mean())  # Impute with mean
        std = col_data.std()
        features[f"{col}_norm"] = (col_data - col_data.mean()) / (std + 1e-6)
        features[f"{col}_is_positive"] = (col_data > 0).astype(int)

    # --- Categorical Features ---
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        nuni = df[col].nunique(dropna=True)
        if nuni <= 10:
            dummies = pd.get_dummies(df[col].fillna("Missing"), prefix=col)
            features = pd.concat([features, dummies], axis=1)
        else:
            features[f"{col}_length"] = df[col].fillna("").astype(str).apply(len)

    # --- Datetime Features ---
    date_cols = df.select_dtypes(include=['datetime64[ns]']).columns
    for col in date_cols:
        features[f"{col}_year"] = df[col].dt.year
        features[f"{col}_month"] = df[col].dt.month
        features[f"{col}_day"] = df[col].dt.day
        features[f"{col}_weekday"] = df[col].dt.weekday
        features[f"{col}_is_weekend"] = df[col].dt.weekday >= 5

    return features
