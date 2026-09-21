import os
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.cleaning import clean_data, get_data_quality_report, validate_columns
from utils.analysis import (
    get_kpis,
    category_sales_analysis,
    monthly_sales_analysis,
    payment_method_analysis,
    order_status_analysis,
    top_products_analysis,
    top_customers_analysis,
    city_sales_analysis,
    lowest_selling_products,
)
from utils.insights import generate_insights

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
)

REQUIRED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Customer_ID",
    "Product_Name",
    "Category",
    "Quantity",
    "Price",
    "Payment_Method",
    "Order_Status",
]


@st.cache_data
def load_default_data():
    file_path = "data/ecommerce_orders.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None


def load_uploaded_data(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)

    return pd.read_excel(uploaded_file)


def show_logo():
    logo_path = "assets/university_logo.png"
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)


def main():
    show_logo()

    st.sidebar.title("🛒 E-Commerce Dashboard")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Upload Dataset",
            "Data Cleaning",
            "Dashboard",
            "Sales Analysis",
            "Customer Analysis",
            "Product Analysis",
            "Business Insights",
        ],
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload Orders Dataset",
        type=["csv", "xlsx", "xls"],
    )

    raw_df = None

    if uploaded_file is not None:
        try:
            raw_df = load_uploaded_data(uploaded_file)
            st.sidebar.success("Uploaded dataset loaded successfully.")
        except Exception as error:
            st.sidebar.error(f"Unable to read file: {error}")
    else:
        raw_df = load_default_data()
        if raw_df is not None:
            st.sidebar.info("Using default dataset from data folder.")

    if page == "Home":
        st.title("🛒 E-Commerce Orders Data Analysis")
        st.subheader("Interactive Business Intelligence Dashboard")

        st.markdown(
            """
            This dashboard helps analyse e-commerce order data and identify useful
            business patterns from sales, products, customers, payments, and order status.

            ### Project Objectives
            - Analyse total sales and order performance
            - Identify best-performing categories and products
            - Understand customer purchase behaviour
            - Track monthly sales trends
            - Review payment method preference
            - Measure cancellation and return rates
            """
        )

        st.info(
            "Upload a CSV or Excel dataset from the sidebar, or place "
            "`ecommerce_orders.csv` inside the `data` folder."
        )
        return

    if raw_df is None:
        st.warning(
            "Please upload a CSV/Excel dataset or add "
            "`data/ecommerce_orders.csv` to start analysis."
        )
        return

    raw_df.columns = raw_df.columns.astype(str).str.strip()
    is_valid, missing_columns = validate_columns(raw_df, REQUIRED_COLUMNS)

    if not is_valid:
        st.error(
            "The dataset is missing required columns: "
            + ", ".join(missing_columns)
        )
        st.write("Required columns:", REQUIRED_COLUMNS)
        return

    cleaned_df = clean_data(raw_df)
    quality_report = get_data_quality_report(raw_df, cleaned_df)

    if page == "Upload Dataset":
        st.title("📤 Upload Dataset")

        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", f"{raw_df.shape[0]:,}")
        col2.metric("Columns", raw_df.shape[1])
        col3.metric("Duplicate Rows", f"{raw_df.duplicated().sum():,}")

        st.subheader("Dataset Preview")
        st.dataframe(raw_df.head(10), use_container_width=True)

        st.subheader("Column Names")
        st.write(list(raw_df.columns))

        st.subheader("Missing Values")
        missing_values = raw_df.isna().sum().reset_index()
        missing_values.columns = ["Column", "Missing Values"]
        st.dataframe(missing_values, use_container_width=True, hide_index=True)

    elif page == "Data Cleaning":
        st.title("🧹 Data Cleaning Report")

        col1, col2, col3 = st.columns(3)
        col1.metric("Original Rows", f"{quality_report['original_rows']:,}")
        col2.metric("Cleaned Rows", f"{quality_report['cleaned_rows']:,}")
        col3.metric("Rows Removed", f"{quality_report['rows_removed']:,}")

        st.subheader("Cleaning Actions Applied")
        st.markdown(
            """
            - Removed duplicate records
            - Removed duplicate order IDs
            - Converted order dates to valid datetime format
            - Filled missing quantity values using median quantity
            - Filled missing category values with `Unknown`
            - Filled missing payment methods using the most common value
            - Removed invalid rows with missing order ID, date, or price
            - Removed rows with zero or negative quantity/price
            - Calculated sales using Quantity × Price
            """
        )

        st.subheader("Cleaned Dataset Preview")
        st.dataframe(cleaned_df.head(10), use_container_width=True)

        csv_data = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Cleaned Dataset",
            data=csv_data,
            file_name="ecommerce_orders_cleaned.csv",
            mime="text/csv",
        )

    elif page == "Dashboard":
        st.title("📊 Business Dashboard")

        kpis = get_kpis(cleaned_df)

        row1_col1, row1_col2, row1_col3 = st.columns(3)
        row2_col1, row2_col2, row2_col3 = st.columns(3)

        row1_col1.metric("Total Sales", f"₹ {kpis['total_sales']:,.2f}")
        row1_col2.metric("Total Orders", f"{kpis['total_orders']:,}")
        row1_col3.metric("Average Order Value", f"₹ {kpis['average_order_value']:,.2f}")

        row2_col1.metric("Quantity Sold", f"{kpis['total_quantity']:,}")
        row2_col2.metric("Unique Customers", f"{kpis['unique_customers']:,}")
        row2_col3.metric("Cancelled / Returned", f"{kpis['loss_rate']:.2f}%")

        category_df = category_sales_analysis(cleaned_df)
        monthly_df = monthly_sales_analysis(cleaned_df)
        payment_df = payment_method_analysis(cleaned_df)
        status_df = order_status_analysis(cleaned_df)

        col1, col2 = st.columns(2)

        with col1:
            fig_category = px.bar(
                category_df,
                x="Category",
                y="Sales",
                color="Sales",
                title="Category-wise Sales",
                text_auto=".2s",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig_category, use_container_width=True)

        with col2:
            fig_month = px.line(
                monthly_df,
                x="Month",
                y="Sales",
                markers=True,
                title="Monthly Sales Trend",
            )
            st.plotly_chart(fig_month, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            fig_payment = px.pie(
                payment_df,
                names="Payment_Method",
                values="Orders",
                title="Payment Method Usage",
                hole=0.35,
            )
            st.plotly_chart(fig_payment, use_container_width=True)

        with col2:
            fig_status = px.bar(
                status_df,
                x="Order_Status",
                y="Orders",
                color="Order_Status",
                title="Order Status Distribution",
            )
            st.plotly_chart(fig_status, use_container_width=True)

    elif page == "Sales Analysis":
        st.title("💰 Sales Analysis")

        category_df = category_sales_analysis(cleaned_df)
        monthly_df = monthly_sales_analysis(cleaned_df)
        city_df = city_sales_analysis(cleaned_df)

        fig_category = px.bar(
            category_df,
            x="Category",
            y="Sales",
            color="Sales",
            title="Sales by Category",
            text_auto=".2s",
        )
        st.plotly_chart(fig_category, use_container_width=True)

        fig_month = px.line(
            monthly_df,
            x="Month",
            y="Sales",
            markers=True,
            title="Monthly Sales Performance",
        )
        st.plotly_chart(fig_month, use_container_width=True)

        if city_df is not None:
            fig_city = px.bar(
                city_df.head(10),
                x="City",
                y="Sales",
                color="Sales",
                title="Top 10 Cities by Sales",
                text_auto=".2s",
            )
            st.plotly_chart(fig_city, use_container_width=True)

        st.subheader("Category-wise Sales Table")
        st.dataframe(category_df, use_container_width=True, hide_index=True)

    elif page == "Customer Analysis":
        st.title("👥 Customer Analysis")

        top_customers_df = top_customers_analysis(cleaned_df)

        st.subheader("Top 10 Customers by Spending")
        st.dataframe(top_customers_df, use_container_width=True, hide_index=True)

        fig_customers = px.bar(
            top_customers_df.sort_values("Total_Spend"),
            x="Total_Spend",
            y="Customer_ID",
            orientation="h",
            color="Total_Spend",
            title="Top Customers by Total Spending",
            text_auto=".2s",
        )
        st.plotly_chart(fig_customers, use_container_width=True)

    elif page == "Product Analysis":
        st.title("📦 Product Analysis")

        top_products_df = top_products_analysis(cleaned_df)
        low_products_df = lowest_selling_products(cleaned_df)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top Products by Revenue")
            st.dataframe(top_products_df, use_container_width=True, hide_index=True)

        with col2:
            st.subheader("Lowest-selling Products")
            st.dataframe(low_products_df, use_container_width=True, hide_index=True)

        fig_top_products = px.bar(
            top_products_df.sort_values("Sales"),
            x="Sales",
            y="Product_Name",
            orientation="h",
            color="Sales",
            title="Top 10 Products by Revenue",
            text_auto=".2s",
        )
        st.plotly_chart(fig_top_products, use_container_width=True)

        fig_scatter = px.scatter(
            cleaned_df,
            x="Quantity",
            y="Sales",
            color="Category",
            hover_data=["Product_Name", "Order_ID"],
            title="Quantity vs Sales",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    elif page == "Business Insights":
        st.title("💡 Business Insights")

        insights = generate_insights(cleaned_df)

        st.success(insights["top_category"])
        st.info(insights["top_product"])
        st.warning(insights["best_month"])
        st.info(insights["payment_method"])
        st.error(insights["loss_rate"])
        st.warning(insights["improvement_category"])

        st.subheader("Detailed Insights")
        for item in insights["all_insights"]:
            st.write(f"• {item}")


if __name__ == "__main__":
    main()