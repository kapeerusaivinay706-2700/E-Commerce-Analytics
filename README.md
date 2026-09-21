# E-Commerce Analytics Dashboard

A Streamlit web application for analysing e-commerce orders data.

## Features

- Upload CSV or Excel datasets
- Clean duplicate and missing records
- Calculate sales automatically
- Display KPIs such as total sales, orders, customers, and average order value
- Show category, monthly, payment, status, product, customer, and city analysis
- Generate business insights automatically
- Download cleaned dataset as CSV

## Required Dataset Columns

Your dataset must include these columns:

```text
Order_ID
Order_Date
Customer_ID
Product_Name
Category
Quantity
Price
Payment_Method
Order_Status
```

Optional column:

```text
City
```

## Installation

Open the project folder in VS Code terminal and run:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run app.py
```

The application opens in the browser automatically.

## Default Dataset

Place your dataset here if you want it to load automatically:

```text
data/ecommerce_orders.csv
```

You can also upload CSV, XLSX, or XLS files from the Streamlit sidebar.