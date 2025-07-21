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

    def highlight_stock(row):
        if row['Quantity In Stock'] == 0:
            return ['background-color: red; color: white'] * len(row)
        elif row['Quantity In Stock'] < 5:
            return ['background-color: yellow'] * len(row)
        else:
            return [''] * len(row)

    styled_table = inventory_df.style.apply(highlight_stock, axis=1)

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

        # Side-by-side display
        summary_col1, summary_col2 = st.columns(2)
        with summary_col1:
            st.write(f"**Transactions Today:** {today_transactions}")
        with summary_col2:
            st.write(f"**Revenue Today:** {today_revenue:.2f} $")


        sales_log_df = sales_log_df.iloc[::-1].reset_index(drop=True)
        st.dataframe(sales_log_df, use_container_width=True, height=400)

        total_sales = sales_log_df['Total Sale Amount'].sum()
        total_transactions = len(sales_log_df)
        st.write(f"**Total Transactions:** {total_transactions}")
        st.write(f"**Total Sales Revenue:** {total_sales:.2f} $")





      # --- Download Sales Log for a Specific Day ---
    st.markdown("---")
    st.subheader("📥 Export Daily Sales Report")

    selected_day = st.date_input("Select a day to download its sales transactions:")

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
