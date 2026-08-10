import streamlit as st
import pandas as pd
import tempfile
import os
import importlib
import parser
import excel_generator
importlib.reload(parser)
importlib.reload(excel_generator)
from parser import parse_pdf
from excel_generator import generate_excel

# Set page configuration
st.set_page_config(
    page_title="Bank Statement Converter & Analyzer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS
st.markdown("""
<style>
    /* Theme overrides */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stMetric label {
        color: #8b949e !important;
        font-size: 14px !important;
    }
    .stMetric div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-size: 24px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏦 Bank Statement Converter")
st.markdown("Convert any Indian bank PDF statement into a clean, styled Excel sheet with live analytics.")

# Sidebar info
with st.sidebar:
    st.header("Supported Banks")
    st.markdown("""
    - Karur Vysya Bank (KVB)
    - Indian Bank
    - Union Bank of India (UBI)
    - City Union Bank (CUB)
    - IDBI Bank
    - HDFC Bank
    - IndusInd Bank
    - ICICI Bank
    - Kotak Mahindra Bank
    - Punjab National Bank (PNB)
    - Standard Chartered Bank (SCB)
    - State Bank of India (SBI)
    - Bank of Baroda (BoB)
    - Canara Bank
    - DBS Bank
    - RBL Bank
    - South Indian Bank (SIB)
    - IDFC FIRST Bank
    - Axis Bank *(scanned check)*
    """)
    st.info("💡 **Scanned PDF check**: Axis and scanned SBI statements will trigger a scanned document warning.")

uploaded_file = st.file_uploader("Upload statement PDF", type="pdf")

if uploaded_file is not None:
    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Check if password is required
    pwd_required = st.session_state.get(f"pwd_required_{uploaded_file.name}", False)
    password = st.session_state.get(f"pwd_{uploaded_file.name}", None)
    
    success = False
    metadata, transactions = {}, []
    
    try:
        if pwd_required and password is not None:
            with st.spinner("Unlocking and processing PDF statement..."):
                metadata, transactions = parse_pdf(tmp_path, password=password)
            success = True
        else:
            with st.spinner("Processing PDF statement..."):
                metadata, transactions = parse_pdf(tmp_path)
            success = True
    except ValueError as e:
        if str(e) == "PASSWORD_REQUIRED":
            st.session_state[f"pwd_required_{uploaded_file.name}"] = True
            st.warning("🔑 This PDF statement is password protected. Please enter the password below to unlock it.")
            pwd_val = st.text_input("Enter Password", type="password", key=f"pwd_field_{uploaded_file.name}")
            if pwd_val:
                st.session_state[f"pwd_{uploaded_file.name}"] = pwd_val
                st.rerun()
        elif str(e) == "PASSWORD_INCORRECT":
            st.error("❌ Incorrect password. Please try again.")
            pwd_val = st.text_input("Enter Password", type="password", key=f"pwd_field_{uploaded_file.name}")
            if pwd_val:
                st.session_state[f"pwd_{uploaded_file.name}"] = pwd_val
                st.rerun()
        else:
            st.error(f"Error parsing PDF: {str(e)}")
            st.warning("This PDF might be a scanned image statement or unsupported layout. Please verify.")
    except Exception as e:
        st.error(f"Error parsing PDF: {str(e)}")
        st.warning("This PDF might be a scanned image statement or unsupported layout. Please verify.")
    finally:
        if not success:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    if success:
        try:
            st.success("Successfully parsed PDF!")

            # Create editable metadata inputs
            st.subheader("📝 Metadata")
            col1, col2, col3 = st.columns(3)
            with col1:
                meta_holder = st.text_input("Account Holder Name", value=metadata.get("holder_name", ""))
                meta_num = st.text_input("Account Number", value=metadata.get("account_number", ""))
            with col2:
                meta_cust = st.text_input("Customer ID", value=metadata.get("customer_id", ""))
                meta_type = st.text_input("Account Type", value=metadata.get("account_type", ""))
            with col3:
                meta_period = st.text_input("Statement Period", value=metadata.get("statement_period", ""))
                currency_symbol = st.selectbox("Excel Currency Symbol", ["₹", "$", "€", "£", ""])

            # Convert transactions list to pandas DataFrame
            df_tx = pd.DataFrame(transactions)
            if df_tx.empty:
                df_tx = pd.DataFrame(columns=["txn_date", "value_date", "particulars", "ref_no", "debit", "credit", "balance"])
            else:
                # Reorder columns
                cols_order = ["txn_date", "value_date", "particulars", "ref_no", "debit", "credit", "balance"]
                for col in cols_order:
                    if col not in df_tx.columns:
                        df_tx[col] = ""
                df_tx = df_tx[cols_order]

            # Calculate live stats
            def to_float(val):
                if not val: return 0.0
                try:
                    return float(str(val).replace(",", "").strip())
                except ValueError:
                    return 0.0

            df_tx["debit_f"] = df_tx["debit"].apply(to_float)
            df_tx["credit_f"] = df_tx["credit"].apply(to_float)

            total_debits = df_tx["debit_f"].sum()
            total_credits = df_tx["credit_f"].sum()
            net_flow = total_credits - total_debits
            
            # Get ending balance
            ending_bal = 0.0
            if not df_tx.empty:
                ending_bal = to_float(df_tx.iloc[-1]["balance"])

            # Display Metrics
            st.subheader("📊 Live Statement Summary")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Total Credits (Inflow)", f"{currency_symbol} {total_credits:,.2f}")
            m_col2.metric("Total Debits (Outflow)", f"{currency_symbol} {total_debits:,.2f}")
            
            if net_flow >= 0:
                m_col3.metric("Net Cash Flow", f"+ {currency_symbol} {net_flow:,.2f}")
            else:
                m_col3.metric("Net Cash Flow", f"- {currency_symbol} {abs(net_flow):,.2f}")
                
            m_col4.metric("Ending Balance", f"{currency_symbol} {ending_bal:,.2f}")

            # Editable Transaction Grid
            st.subheader("✏️ Edit Transactions")
            st.markdown("*Double-click a cell to edit. You can add or delete rows using the toolbar at the bottom of the table.*")
            
            # Drop temporary helper floats before displaying
            df_display = df_tx.drop(columns=["debit_f", "credit_f"], errors="ignore")
            
            edited_df = st.data_editor(
                df_display,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "txn_date": st.column_config.TextColumn("Txn Date", width="small"),
                    "value_date": st.column_config.TextColumn("Value Date", width="small"),
                    "particulars": st.column_config.TextColumn("Particulars / Description", width="large"),
                    "ref_no": st.column_config.TextColumn("Ref / Chq No.", width="small"),
                    "debit": st.column_config.TextColumn("Debit (Dr.)", width="small"),
                    "credit": st.column_config.TextColumn("Credit (Cr.)", width="small"),
                    "balance": st.column_config.TextColumn("Running Balance", width="small"),
                }
            )

            # Export Excel Action
            st.subheader("📥 Export Spreadsheet")
            
            # Compile metadata dict
            meta_edited = {
                "holder_name": meta_holder,
                "account_number": meta_num,
                "customer_id": meta_cust,
                "account_type": meta_type,
                "statement_period": meta_period
            }
            
            # Convert edited DataFrame back to dict list
            tx_edited_list = edited_df.to_dict("records")
            
            # Temp path for Excel export
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_excel:
                excel_path = tmp_excel.name
                
            try:
                # Generate styled workbook
                generate_excel(meta_edited, tx_edited_list, excel_path, currency_symbol)
                
                with open(excel_path, "rb") as f:
                    excel_data = f.read()
                    
                st.download_button(
                    label="📥 Download Styled Excel Workbook",
                    data=excel_data,
                    file_name=f"statement_analysis_{meta_num if meta_num else 'export'}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as ex:
                st.error(f"Failed to generate Excel file: {str(ex)}")
            finally:
                if os.path.exists(excel_path):
                    os.remove(excel_path)

        finally:
            # Clean up temporary PDF
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
