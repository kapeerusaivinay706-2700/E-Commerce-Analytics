from utils.analysis import (
    category_sales_analysis,
    monthly_sales_analysis,
    top_products_analysis,
    payment_method_analysis,
    get_kpis,
)


def generate_insights(df):
    category_df = category_sales_analysis(df)
    monthly_df = monthly_sales_analysis(df)
    products_df = top_products_analysis(df)
    payment_df = payment_method_analysis(df)
    kpis = get_kpis(df)

    top_category = category_df.iloc[0]
    lowest_category = category_df.iloc[-1]
    top_product = products_df.iloc[0]
    best_month = monthly_df.loc[monthly_df["Sales"].idxmax()]
    payment_method = payment_df.iloc[0]

    top_category_message = (
        f"Highest-performing category: {top_category['Category']} "
        f"generated ₹ {top_category['Sales']:,.2f} in sales."
    )

    top_product_message = (
        f"Best-selling product: {top_product['Product_Name']} "
        f"generated ₹ {top_product['Sales']:,.2f} in revenue."
    )

    best_month_message = (
        f"Best sales month: {best_month['Month']} "
        f"recorded ₹ {best_month['Sales']:,.2f} in sales."
    )

    payment_method_message = (
        f"Most-used payment method: {payment_method['Payment_Method']} "
        f"was used for {payment_method['Orders']:,} orders."
    )

    loss_rate_message = (
        f"Cancellation and return rate: {kpis['loss_rate']:.2f}% "
        f"of order records have Cancelled or Returned status."
    )

    improvement_category_message = (
        f"Category needing improvement: {lowest_category['Category']} "
        f"has the lowest sales of ₹ {lowest_category['Sales']:,.2f}."
    )

    return {
        "top_category": top_category_message,
        "top_product": top_product_message,
        "best_month": best_month_message,
        "payment_method": payment_method_message,
        "loss_rate": loss_rate_message,
        "improvement_category": improvement_category_message,
        "all_insights": [
            top_category_message,
            top_product_message,
            best_month_message,
            payment_method_message,
            loss_rate_message,
            improvement_category_message,
        ],
    }