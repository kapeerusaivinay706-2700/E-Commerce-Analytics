import pandas as pd


def get_kpis(df):
    total_sales = df["Sales"].sum()
    total_orders = df["Order_ID"].nunique()
    total_quantity = df["Quantity"].sum()
    unique_customers = df["Customer_ID"].nunique()

    average_order_value = (
        total_sales / total_orders if total_orders > 0 else 0
    )

    unsuccessful_orders = df[
        df["Order_Status"].isin(["Cancelled", "Returned"])
    ]

    loss_rate = (
        len(unsuccessful_orders) / len(df) * 100
        if len(df) > 0 else 0
    )

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "total_quantity": total_quantity,
        "unique_customers": unique_customers,
        "loss_rate": loss_rate,
    }


def category_sales_analysis(df):
    return (
        df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )


def monthly_sales_analysis(df):
    return (
        df.groupby(["Month_Number", "Month"], as_index=False)["Sales"]
        .sum()
        .sort_values("Month_Number")
    )


def payment_method_analysis(df):
    payment_df = df["Payment_Method"].value_counts().reset_index()
    payment_df.columns = ["Payment_Method", "Orders"]
    return payment_df


def order_status_analysis(df):
    status_df = df["Order_Status"].value_counts().reset_index()
    status_df.columns = ["Order_Status", "Orders"]
    return status_df


def top_products_analysis(df, limit=10):
    return (
        df.groupby("Product_Name", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Quantity_Sold=("Quantity", "sum"),
            Orders=("Order_ID", "nunique"),
        )
        .sort_values("Sales", ascending=False)
        .head(limit)
    )


def lowest_selling_products(df, limit=10):
    return (
        df.groupby("Product_Name", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Quantity_Sold=("Quantity", "sum"),
        )
        .sort_values("Sales", ascending=True)
        .head(limit)
    )


def top_customers_analysis(df, limit=10):
    return (
        df.groupby("Customer_ID", as_index=False)
        .agg(
            Total_Spend=("Sales", "sum"),
            Orders=("Order_ID", "nunique"),
            Quantity_Purchased=("Quantity", "sum"),
        )
        .sort_values("Total_Spend", ascending=False)
        .head(limit)
    )


def city_sales_analysis(df):
    if "City" not in df.columns:
        return None

    return (
        df.groupby("City", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )