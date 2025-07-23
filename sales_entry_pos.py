import streamlit as st
import pandas as pd
from datetime import datetime

# Load inventory
inventory_file = 'inventory_2024_detailed-2.xlsx'
inventory_df = pd.read_excel(inventory_file)

st.set_page_config(page_title="Baba Jina POS", layout="wide")

# --- SALES ENTRY FORM ---
st.title("📦 Baba Jina Toys POS System")
st.header("Sales Entry Form")

# Columns for Product, Customer Name, and Phone
col1, col2, col3 = st.columns(3)

with col1:
    product_list = inventory_df['Product Name'].dropna().unique()
    selected_product = st.selectbox("Product", product_list)

with col2:
    customer_name = st.text_input("Customer Name")

with col3:
    customer_phone = st.text_input("Phone Number")

product_row = inventory_df[inventory_df['Product Name'] == selected_product].iloc[0]
price_per_unit = product_row['Price Per Unit']
quantity_in_stock = product_row['Quantity In Stock']

st.write(f"**Price per unit:** {price_per_unit}")
st.write(f"**Available stock:** {quantity_in_stock}")

quantity_sold = st.number_input("Enter quantity sold:", min_value=1, max_value=int(quantity_in_stock), step=1)
total_sale = quantity_sold * price_per_unit
st.write(f"**Total Sale Amount:** {total_sale} $")

confirm = st.checkbox("Confirm sale submission")

if st.button("Record Sale", type="primary") and confirm:
    inventory_df.loc[inventory_df['Product Name'] == selected_product, 'Quantity In Stock'] -= quantity_sold
    inventory_df.to_excel(inventory_file, index=False)

    sale_log = pd.DataFrame({
        'Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'Customer Name': [customer_name],
        'Phone Number': [customer_phone],
        'Product Name': [selected_product],
        'Quantity Sold': [quantity_sold],
        'Unit Price': [price_per_unit],
        'Total Sale Amount': [total_sale]
    })

    try:
        existing_log = pd.read_csv('sales_log.csv')
        sale_log = pd.concat([existing_log, sale_log], ignore_index=True)
    except FileNotFoundError:
        pass

    sale_log.to_csv('sales_log.csv', index=False)
    st.success(f"Sale of {quantity_sold} {selected_product} recorded!")

    updated_stock = inventory_df[inventory_df['Product Name'] == selected_product]['Quantity In Stock'].values[0]
    st.info(f"Updated stock for **{selected_product}**: {int(updated_stock)} units remaining.")

st.markdown("---")

# --- SPLIT LAYOUT: Inventory Dashboard & Sales Log Dashboard ---
col1, col2 = st.columns(2)

# INVENTORY DASHBOARD (LEFT)
with col1:
    st.header("📊 Inventory Dashboard")

    # Product Search Bar
    search_term = st.text_input("🔍 Search Product Name")
    filtered_inventory = inventory_df[inventory_df['Product Name'].str.contains(search_term, case=False, na=False)]

    def highlight_stock(row):
        if row['Quantity In Stock'] == 0:
            return ['background-color: red; color: white'] * len(row)
        elif row['Quantity In Stock'] < 5:
            return ['background-color: yellow'] * len(row)
        else:
            return [''] * len(row)

    styled_table = filtered_inventory.style.apply(highlight_stock, axis=1)

    st.write("**Current Inventory Status:**")
    st.dataframe(styled_table, use_container_width=True, height=400)

    total_items = inventory_df['Quantity In Stock'].sum()
    st.write(f"**Total Items in Stock:** {int(total_items)}")

# SALES LOG DASHBOARD (RIGHT)
with col2:
    st.header("📈 Sales Log Dashboard")

    try:
        sales_log_df = pd.read_csv('sales_log.csv')

        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = sales_log_df[sales_log_df['Date'].str.startswith(today)]
        today_revenue = today_sales['Total Sale Amount'].sum()
        today_transactions = len(today_sales)

        st.subheader(f"📅 Today's Summary: {today}")

        summary_col1, summary_col2 = st.columns(2)
        with summary_col1:
            st.write(f"**Transactions Today:** {today_transactions}")
        with summary_col2:
            st.write(f"**Revenue Today:** {today_revenue:.2f} $")

        sales_log_df = sales_log_df.iloc[::-1].reset_index(drop=True)
        st.dataframe(sales_log_df, use_container_width=True, height=400)

        total_sales = sales_log_df['Total Sale Amount'].sum()
        total_transactions = len(sales_log_df)

        totals_col, export_col = st.columns([1, 1.5])

        with totals_col:
            st.write(f"**Total Transactions:** {total_transactions}")
            st.write(f"**Total Sales Revenue:** {total_sales:.2f} $")

        with export_col:
            st.subheader("📥 Export Daily Report")
            selected_day = st.date_input("Select Day:", key="export_date_bottom")
            selected_day_str = selected_day.strftime("%Y-%m-%d")
            day_sales = sales_log_df[sales_log_df['Date'].str.startswith(selected_day_str)]

            if day_sales.empty:
                st.info(f"No sales recorded on {selected_day_str}.")
            else:
                csv = day_sales.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"Download Sales Report for {selected_day_str}",
                    data=csv,
                    file_name=f"sales_report_{selected_day_str}.csv",
                    mime='text/csv'
                )

    except FileNotFoundError:
        st.warning("No sales have been recorded yet.")

# --- OPTIONAL ANALYTICS SECTION ---
# --- OPTIONAL ANALYTICS SECTION ---
import matplotlib.pyplot as plt

st.markdown("---")
st.header("📊 Analytics View")

try:
    sales_log_df = pd.read_csv('sales_log.csv')
    sales_log_df['Date'] = pd.to_datetime(sales_log_df['Date'])

    col1, col2 = st.columns(2)

    # --- LEFT: Top-Selling Products ---
    with col1:
        st.subheader("🏆 Top-Selling Products")
        top_products = sales_log_df.groupby('Product Name')['Quantity Sold'].sum().sort_values(ascending=True)

        fig1, ax1 = plt.subplots(figsize=(5, 3))
        ax1.barh(top_products.index, top_products.values, color='mediumseagreen')
        ax1.set_xlabel("Units Sold")
        ax1.set_title("Top-Selling Products")
        st.pyplot(fig1)

    # --- RIGHT: Daily Revenue for Selected Month ---
    with col2:
        st.subheader("📅 Daily Revenue (Selected Month)")
        selected_month = st.date_input("Select Month to Analyze", value=datetime.today().replace(day=1), key="daily_rev_input")

        month_str = selected_month.strftime("%Y-%m")
        monthly_sales = sales_log_df[sales_log_df['Date'].dt.strftime("%Y-%m") == month_str]

        daily_revenue = monthly_sales.groupby(sales_log_df['Date'].dt.day)['Total Sale Amount'].sum()
        full_range = pd.Series(index=range(1, 32), dtype=float)
        daily_revenue = full_range.add(daily_revenue, fill_value=0)

        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.plot(daily_revenue.index, daily_revenue.values, marker='o', color='dodgerblue')
        ax2.set_xlim(1, 31)
        ax2.set_xticks(range(1, 32, 2))
        ax2.set_xlabel("Day of Month")
        ax2.set_ylabel("Revenue ($)")
        ax2.set_title(f"Daily Revenue - {month_str}")
        # No ax2.grid() here
        st.pyplot(fig2)

except FileNotFoundError:
    st.info("Analytics unavailable (no sales data found).")
