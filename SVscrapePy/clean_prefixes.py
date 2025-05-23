def clean_prefixes(df):
    for col in df.columns:
        col_str = str(col).strip()
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(f"^{re.escape(col_str)}", "", regex=True)
            .str.strip()
            .replace("nan", pd.NA)
        )
    return df