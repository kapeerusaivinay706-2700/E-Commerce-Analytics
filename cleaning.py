import pandas as pd


def validate_columns(df, required_columns):
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]
    return len(missing_columns) == 0, missing_columns


def clean_data(df):
    cleaned_df = df.copy()

    cleaned_df.columns = cleaned_df.columns.astype(str).str.strip()

    cleaned_df = cleaned_df.drop_duplicates()

    if "Order_ID" in cleaned_df.columns:
        cleaned_df = cleaned_df.drop_duplicates(
            subset=["Order_ID"],
            keep="first"
        )

    numeric_columns = ["Quantity", "Price", "Sales"]
    for column in numeric_columns:
        if column in cleaned_df.columns:
            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

    if "Quantity" in cleaned_df.columns:
        median_quantity = cleaned_df["Quantity"].median()
        cleaned_df["Quantity"] = cleaned_df["Quantity"].fillna(median_quantity)

    if "Category" in cleaned_df.columns:
        cleaned_df["Category"] = cleaned_df["Category"].fillna("Unknown")

    if "Payment_Method" in cleaned_df.columns:
        mode_values = cleaned_df["Payment_Method"].mode()
        most_common_payment = (
            mode_values.iloc[0] if not mode_values.empty else "Unknown"
        )
        cleaned_df["Payment_Method"] = cleaned_df["Payment_Method"].fillna(
            most_common_payment
        )

    if "Order_Status" in cleaned_df.columns:
        cleaned_df["Order_Status"] = cleaned_df["Order_Status"].fillna("Unknown")

    if "Order_Date" in cleaned_df.columns:
        cleaned_df["Order_Date"] = pd.to_datetime(
            cleaned_df["Order_Date"],
            errors="coerce"
        )

    required_not_null = [
        column for column in ["Order_ID", "Order_Date", "Price"]
        if column in cleaned_df.columns
    ]
    cleaned_df = cleaned_df.dropna(subset=required_not_null)

    for column in ["Category", "Payment_Method", "Order_Status"]:
        if column in cleaned_df.columns:
            cleaned_df[column] = (
                cleaned_df[column]
                .astype(str)
                .str.strip()
                .str.title()
            )

    if "Quantity" in cleaned_df.columns:
        cleaned_df = cleaned_df[cleaned_df["Quantity"] > 0]

    if "Price" in cleaned_df.columns:
        cleaned_df = cleaned_df[cleaned_df["Price"] > 0]

    cleaned_df["Sales"] = cleaned_df["Quantity"] * cleaned_df["Price"]

    cleaned_df["Month"] = cleaned_df["Order_Date"].dt.month_name()
    cleaned_df["Month_Number"] = cleaned_df["Order_Date"].dt.month
    cleaned_df["Year"] = cleaned_df["Order_Date"].dt.year

    return cleaned_df.reset_index(drop=True)


def get_data_quality_report(raw_df, cleaned_df):
    return {
        "original_rows": len(raw_df),
        "cleaned_rows": len(cleaned_df),
        "rows_removed": len(raw_df) - len(cleaned_df),
        "duplicate_rows": int(raw_df.duplicated().sum()),
        "missing_values_before": int(raw_df.isna().sum().sum()),
        "missing_values_after": int(cleaned_df.isna().sum().sum()),
    }