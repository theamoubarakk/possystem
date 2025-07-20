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

product_list = inventory_df['Product Name'].dropna().unique()
selected_product = st.selectbox("Select Product:", product_list)

product_row = inventory_df[inventory_df['Product Name'] == selected_product].iloc[0]
price_per_unit = product_row['Price Per Unit']
quantity_in_stock = product_row['Quantity In Stock']

st.write(f"**Price per unit:** {price_per_unit}")
st.write(f"**Available stock:** {quantity_in_stock}")

quantity_sold = st.number_input("Enter quantity sold:", min_value=1, max_value=int(quantity_in_stock), step=1)

total_sale = quantity_sold * price_per_unit
st.write(f"**Total Sale Amount:** {total_sale} $")

if st.button("Record Sale"):
    inventory_df.loc[inventory_df['Product Name'] == selected_product, 'Quantity In Stock'] -= quantity_sold
    inventory_df.to_excel(inventory_file, index=False)

    sale_log = pd.DataFrame({
        'Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
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

st.markdown("---")

# --- INVENTORY DASHBOARD ---
st.header("📊 Inventory Dashboard")

def highlight_stock(row):
    if row['Quantity In Stock'] == 0:
        return ['background-color: red; color: white'] * len(row)
    elif row['Quantity In Stock'] < 5:
        return ['background-color: yellow'] * len(row)
    else:
        return [''] * len(row)

styled_table = inventory_df.style.apply(highlight_stock, axis=1)

with st.container():
    st.write("**Current Inventory Status:**")
    st.dataframe(styled_table, use_container_width=True, height=300)

total_items = inventory_df['Quantity In Stock'].sum()
st.write(f"**Total Items in Stock:** {int(total_items)}")

st.markdown("---")

# --- SALES LOG DASHBOARD ---
st.header("📈 Sales Log Dashboard")

try:
    sales_log_df = pd.read_csv('sales_log.csv')
    st.dataframe(sales_log_df, use_container_width=True, height=300)

    total_sales = sales_log_df['Total Sale Amount'].sum()
    total_transactions = len(sales_log_df)
    st.write(f"**Total Transactions:** {total_transactions}")
    st.write(f"**Total Sales Revenue:** {total_sales:.2f} $")

except FileNotFoundError:
    st.warning("No sales have been recorded yet.")
