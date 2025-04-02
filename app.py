import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os

from database import Database
from calculations import calculate_all
from utils import (
    format_currency, parse_date, format_date, 
    export_data, validate_transaction_input,
    backup_database, restore_database, get_available_backups
)

# Initialize the database
db = Database()

# Page configuration
st.set_page_config(
    page_title="HISAABSETU - Accounting Software",
    page_icon="💰",
    layout="wide"
)

# Custom styling with Aclonica font for HISAABSETU
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Aclonica&display=swap');

.hisaabsetu-logo {
    font-family: 'Aclonica', sans-serif;
    font-size: 2.5rem;
    color: #1E88E5;
    margin-bottom: 0.5rem;
}

.hisaabsetu-subheader {
    font-family: 'Aclonica', sans-serif;
    color: #1976D2;
}

.hisaabsetu-header {
    font-family: 'Aclonica', sans-serif;
    font-size: 1.8rem;
    color: #1565C0;
    margin-bottom: 0.5rem;
}

.hisaabsetu-subheader-page {
    font-family: 'Aclonica', sans-serif;
    font-size: 1.2rem;
    color: #1976D2;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Helper functions for styled headers
def styled_header(text):
    """Display header with Aclonica font styling"""
    st.markdown(f'<h2 class="hisaabsetu-header">{text}</h2>', unsafe_allow_html=True)
    
def styled_subheader(text):
    """Display subheader with Aclonica font styling"""
    st.markdown(f'<h3 class="hisaabsetu-subheader-page">{text}</h3>', unsafe_allow_html=True)

# Initialize session state for storing form data and UI state
if 'show_add_party_form' not in st.session_state:
    st.session_state.show_add_party_form = False
    
if 'party_type' not in st.session_state:
    st.session_state.party_type = None
    
if 'edit_transaction' not in st.session_state:
    st.session_state.edit_transaction = None
    
if 'show_add_transaction_form' not in st.session_state:
    st.session_state.show_add_transaction_form = False

if 'filter_applied' not in st.session_state:
    st.session_state.filter_applied = False
    
if 'filters' not in st.session_state:
    st.session_state.filters = {}
    
if 'show_partial_payment_form' not in st.session_state:
    st.session_state.show_partial_payment_form = False
    
if 'all_entries_filters' not in st.session_state:
    st.session_state.all_entries_filters = {}
    
if 'selected_transaction_for_payment' not in st.session_state:
    st.session_state.selected_transaction_for_payment = None

# Function to reset form state
def reset_form_state():
    st.session_state.show_add_party_form = False
    st.session_state.party_type = None
    st.session_state.edit_transaction = None
    st.session_state.show_add_transaction_form = False
    st.session_state.show_partial_payment_form = False
    st.session_state.selected_transaction_for_payment = None

# Main application header with Aclonica font
st.markdown('<h1 class="hisaabsetu-logo">HISAABSETU</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="hisaabsetu-subheader">Portable Accounting Software</h3>', unsafe_allow_html=True)

# Sidebar for navigation with Aclonica font
st.sidebar.markdown('<h2 class="hisaabsetu-logo" style="font-size: 1.8rem;">HISAABSETU</h2>', unsafe_allow_html=True)
st.sidebar.markdown('<h3 class="hisaabsetu-subheader" style="font-size: 1.2rem;">Navigation</h3>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "Go to", 
    ["Today", "Dashboard", "Manage Parties", "Transactions", "All Entries", "Payments", "Reports", "Settings"]
)

# Today Page - Transactions ending today
if page == "Today":
    styled_header("Today's Transactions")
    styled_subheader("Transactions Ending Today")
    
    # Get transactions ending today
    today_transactions = db.get_transactions_ending_today()
    
    if today_transactions:
        # Calculate the total dalali amount
        total_dalali = sum(t['dalali_amount'] for t in today_transactions)
        
        # Create a DataFrame for display
        df = pd.DataFrame(today_transactions)
        
        # Display a summary card with total dalali amount
        st.metric("Total Dalali Amount Today", format_currency(total_dalali))
        
        # Format the DataFrame for display
        display_df = df[[
            'id', 'apnaar_party_name', 'lenaar_party_name', 'kapine_lenaar_party_name',
            'total_amount', 'condition', 'start_date', 'end_date', 
            'dalali_amount', 'interest_amount', 'received'
        ]].copy()
        
        # Rename columns for better display
        display_df.columns = [
            'ID', 'Apnaar Party', 'Lenaar Party', 'Kapine Lenaar Party',
            'Total Amount (₹)', 'Condition', 'Start Date', 'End Date', 
            'Dalali Amount (₹)', 'Interest Amount (₹)', 'Received'
        ]
        
        # Format numeric and date columns
        display_df['Total Amount (₹)'] = display_df['Total Amount (₹)'].apply(lambda x: format_currency(x))
        display_df['Dalali Amount (₹)'] = display_df['Dalali Amount (₹)'].apply(lambda x: format_currency(x))
        display_df['Interest Amount (₹)'] = display_df['Interest Amount (₹)'].apply(lambda x: format_currency(x))
        display_df['Start Date'] = display_df['Start Date'].apply(format_date)
        display_df['End Date'] = display_df['End Date'].apply(format_date)
        display_df['Received'] = display_df['Received'].map({0: '❌', 1: '✅'})
        
        # Display the dataframe
        st.dataframe(display_df, use_container_width=True)
        
        # Add action buttons for the selected transaction
        if today_transactions:
            selected_transaction = st.selectbox(
                "Select a transaction to perform actions",
                options=df['id'].tolist(),
                format_func=lambda x: f"ID: {x} - {df[df['id'] == x]['apnaar_party_name'].iloc[0]} to {df[df['id'] == x]['lenaar_party_name'].iloc[0]} - {format_currency(df[df['id'] == x]['total_amount'].iloc[0])}"
            )
            
            if selected_transaction:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("Mark as Received", key="today_mark_received"):
                        success = db.update_transaction_received_status(selected_transaction, True)
                        if success:
                            st.success("Transaction marked as received!")
                            st.rerun()
                        else:
                            st.error("Failed to update transaction status")
                
                with col2:
                    if st.button("Mark as Pending", key="today_mark_pending"):
                        success = db.update_transaction_received_status(selected_transaction, False)
                        if success:
                            st.success("Transaction marked as pending!")
                            st.rerun()
                        else:
                            st.error("Failed to update transaction status")
                
                with col3:
                    if st.button("Edit Transaction", key="today_edit"):
                        st.session_state.edit_transaction = selected_transaction
                        st.session_state.page = "Transactions"
                        st.rerun()
                
                with col4:
                    if st.button("Delete Transaction", key="today_delete"):
                        if st.session_state.get('confirm_delete') == selected_transaction:
                            success = db.delete_transaction(selected_transaction)
                            if success:
                                st.success("Transaction deleted successfully!")
                                st.session_state.pop('confirm_delete', None)
                                st.rerun()
                            else:
                                st.error("Failed to delete transaction")
                        else:
                            st.session_state.confirm_delete = selected_transaction
                            st.warning("Click again to confirm deletion.")
    else:
        st.info("No transactions ending today.")
        
        # Add button to add a new transaction
        if st.button("Add New Transaction"):
            st.session_state.page = "Transactions"
            st.session_state.show_add_transaction_form = True
            st.rerun()

# Dashboard Page
elif page == "Dashboard":
    styled_header("Dashboard")
    
    # Get transaction data for summary
    transactions = db.get_transactions()
    
    # Display summary metrics with Dalali amount highlighted prominently
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_transactions = len(transactions)
        st.metric("Total Transactions", total_transactions)
    
    with col2:
        total_amount = sum(t['total_amount'] for t in transactions) if transactions else 0
        st.metric("Total Amount", format_currency(total_amount))
        
    with col3:
        # Highlighting Dalali amount as the main focus
        total_dalali = sum(t['dalali_amount'] for t in transactions) if transactions else 0
        st.metric("Total Dalali Amount", format_currency(total_dalali), 
                 delta_color="normal", help="Total commission earned from all transactions")
    
    with col4:
        total_interest = sum(t['interest_amount'] for t in transactions) if transactions else 0
        st.metric("Total Interest", format_currency(total_interest))
    
    with col5:
        completed_transactions = sum(1 for t in transactions if t['received']) if transactions else 0
        st.metric("Completed Transactions", f"{completed_transactions}/{total_transactions}")
    
    # Recent transactions
    st.subheader("Recent Transactions")
    if transactions:
        # Get only the 5 most recent transactions
        recent_transactions = transactions[:5]
        
        # Create a DataFrame with selected columns - highlighting dalali amount
        df = pd.DataFrame(recent_transactions)
        df = df[[
            'id', 'apnaar_party_name', 'lenaar_party_name', 
            'total_amount', 'dalali_amount', 'interest_amount',
            'start_date', 'end_date', 'received'
        ]]
        
        # Rename columns for better display
        df.columns = [
            'ID', 'Apnaar Party', 'Lenaar Party', 
            'Amount (₹)', 'Dalali (₹)', 'Interest (₹)',
            'Start Date', 'End Date', 'Received'
        ]
        
        # Format data for display
        df['Amount (₹)'] = df['Amount (₹)'].apply(lambda x: format_currency(x))
        df['Dalali (₹)'] = df['Dalali (₹)'].apply(lambda x: format_currency(x))
        df['Interest (₹)'] = df['Interest (₹)'].apply(lambda x: format_currency(x))
        df['Start Date'] = df['Start Date'].apply(format_date)
        df['End Date'] = df['End Date'].apply(format_date)
        df['Received'] = df['Received'].map({0: '❌', 1: '✅'})
        
        # Display the dataframe
        st.dataframe(df, use_container_width=True)
        
        # Button to view all transactions
        if st.button("View All Transactions"):
            st.session_state.page = "Transactions"
            st.rerun()
    else:
        st.info("No transactions found. Add your first transaction to get started.")
        if st.button("Add Transaction"):
            st.session_state.page = "Transactions"
            st.session_state.show_add_transaction_form = True
            st.rerun()

# Manage Parties Page
elif page == "Manage Parties":
    styled_header("Manage Parties")
    
    # Get all parties
    apnaar_parties = db.get_all_apnaar_parties()
    lenaar_parties = db.get_all_lenaar_parties()
    kapine_lenaar_parties = db.get_all_kapine_lenaar_parties()
    
    # Add new party section
    st.subheader("Add New Party")
    
    # Party type selection
    col1, col2 = st.columns([1, 3])
    
    with col1:
        party_type = st.selectbox(
            "Party Type",
            ["Apnaar Party", "Lenaar Party", "Kapine Lenaar Party"],
            key="party_type_select"
        )
    
    with col2:
        if st.button("Add New Party"):
            st.session_state.show_add_party_form = True
            st.session_state.party_type = party_type
    
    # Show add party form if requested
    if st.session_state.show_add_party_form:
        st.subheader(f"Add New {st.session_state.party_type}")
        
        with st.form(key="add_party_form"):
            name = st.text_input("Party Name*")
            contact = st.text_input("Contact Number")
            address = st.text_area("Address")
            
            submit_button = st.form_submit_button("Add Party")
            
            if submit_button:
                if not name:
                    st.error("Party Name is required")
                else:
                    success = False
                    
                    if st.session_state.party_type == "Apnaar Party":
                        success = db.add_apnaar_party(name, contact, address)
                    elif st.session_state.party_type == "Lenaar Party":
                        success = db.add_lenaar_party(name, contact, address)
                    elif st.session_state.party_type == "Kapine Lenaar Party":
                        success = db.add_kapine_lenaar_party(name, contact, address)
                    
                    if success:
                        st.success(f"{st.session_state.party_type} '{name}' added successfully")
                        st.session_state.show_add_party_form = False
                        st.session_state.party_type = None
                        st.rerun()
                    else:
                        st.error(f"Failed to add {st.session_state.party_type}. Party may already exist.")
    
    # Set up session state variables for party deletion
    if "delete_party_confirmation" not in st.session_state:
        st.session_state.delete_party_confirmation = False
    if "delete_party_id" not in st.session_state:
        st.session_state.delete_party_id = None
    if "delete_party_type" not in st.session_state:
        st.session_state.delete_party_type = None
    if "delete_party_name" not in st.session_state:
        st.session_state.delete_party_name = None
        
    # Display existing parties
    st.subheader("Existing Parties")
    
    tab1, tab2, tab3 = st.tabs(["Apnaar Parties", "Lenaar Parties", "Kapine Lenaar Parties"])
    
    # Function to handle delete button clicks
    def show_delete_confirmation(party_id, party_name, party_type):
        st.session_state.delete_party_confirmation = True
        st.session_state.delete_party_id = party_id
        st.session_state.delete_party_type = party_type
        st.session_state.delete_party_name = party_name
    
    # Show delete confirmation if requested
    if st.session_state.delete_party_confirmation:
        st.warning(f"Are you sure you want to delete {st.session_state.delete_party_name}? "
                  f"This action cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Yes, Delete Party"):
                # Perform delete operation based on party type
                if st.session_state.delete_party_type == "Apnaar Party":
                    success, message = db.delete_apnaar_party(st.session_state.delete_party_id)
                elif st.session_state.delete_party_type == "Lenaar Party":
                    success, message = db.delete_lenaar_party(st.session_state.delete_party_id)
                elif st.session_state.delete_party_type == "Kapine Lenaar Party":
                    success, message = db.delete_kapine_lenaar_party(st.session_state.delete_party_id)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                
                # Reset confirmation state
                st.session_state.delete_party_confirmation = False
                st.session_state.delete_party_id = None
                st.session_state.delete_party_type = None
                st.session_state.delete_party_name = None
                
                # Refresh page
                st.rerun()
        
        with col2:
            if st.button("No, Cancel"):
                # Reset confirmation state
                st.session_state.delete_party_confirmation = False
                st.session_state.delete_party_id = None
                st.session_state.delete_party_type = None
                st.session_state.delete_party_name = None
                st.rerun()
    
    with tab1:
        if apnaar_parties:
            # Create a DataFrame to display
            df = pd.DataFrame(apnaar_parties, columns=["ID", "Name"])
            st.dataframe(df, use_container_width=True)
            
            # Add delete buttons for each party
            st.write("Select Party to Delete:")
            for party_id, party_name in apnaar_parties:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{party_id}: {party_name}")
                with col2:
                    if st.button("Delete", key=f"delete_apnaar_{party_id}"):
                        show_delete_confirmation(party_id, party_name, "Apnaar Party")
        else:
            st.info("No Apnaar Parties found")
    
    with tab2:
        if lenaar_parties:
            # Create a DataFrame to display
            df = pd.DataFrame(lenaar_parties, columns=["ID", "Name"])
            st.dataframe(df, use_container_width=True)
            
            # Add delete buttons for each party
            st.write("Select Party to Delete:")
            for party_id, party_name in lenaar_parties:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{party_id}: {party_name}")
                with col2:
                    if st.button("Delete", key=f"delete_lenaar_{party_id}"):
                        show_delete_confirmation(party_id, party_name, "Lenaar Party")
        else:
            st.info("No Lenaar Parties found")
    
    with tab3:
        if kapine_lenaar_parties:
            # Create a DataFrame to display
            df = pd.DataFrame(kapine_lenaar_parties, columns=["ID", "Name"])
            st.dataframe(df, use_container_width=True)
            
            # Add delete buttons for each party
            st.write("Select Party to Delete:")
            for party_id, party_name in kapine_lenaar_parties:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{party_id}: {party_name}")
                with col2:
                    if st.button("Delete", key=f"delete_kapine_{party_id}"):
                        show_delete_confirmation(party_id, party_name, "Kapine Lenaar Party")
        else:
            st.info("No Kapine Lenaar Parties found")

# Transactions Page
elif page == "Transactions":
    styled_header("Manage Transactions")
    
    # Button to show/hide add transaction form
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("➕ Add Transaction"):
            st.session_state.show_add_transaction_form = not st.session_state.show_add_transaction_form
            st.session_state.edit_transaction = None
    
    with col2:
        if st.button("🔍 Show Filters"):
            st.session_state.filter_applied = not st.session_state.filter_applied
    
    # Show filter form
    if st.session_state.filter_applied:
        st.subheader("Filter Transactions")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Get party lists for filtering
            apnaar_parties = db.get_all_apnaar_parties()
            apnaar_options = ["All"] + [party[1] for party in apnaar_parties]
            filter_apnaar = st.selectbox("Apnaar Party", apnaar_options)
            
            if filter_apnaar and filter_apnaar != "All":
                st.session_state.filters['apnaar_party_name'] = filter_apnaar
            elif 'apnaar_party_name' in st.session_state.filters:
                del st.session_state.filters['apnaar_party_name']
        
        with filter_col2:
            lenaar_parties = db.get_all_lenaar_parties()
            lenaar_options = ["All"] + [party[1] for party in lenaar_parties]
            filter_lenaar = st.selectbox("Lenaar Party", lenaar_options)
            
            if filter_lenaar and filter_lenaar != "All":
                st.session_state.filters['lenaar_party_name'] = filter_lenaar
            elif 'lenaar_party_name' in st.session_state.filters:
                del st.session_state.filters['lenaar_party_name']
        
        with filter_col3:
            filter_received = st.selectbox(
                "Received Status", 
                ["All", "Received", "Pending"]
            )
            
            if filter_received == "Received":
                st.session_state.filters['received'] = True
            elif filter_received == "Pending":
                st.session_state.filters['received'] = False
            elif 'received' in st.session_state.filters:
                del st.session_state.filters['received']
        
        # Date filters
        filter_col4, filter_col5 = st.columns(2)
        
        with filter_col4:
            # Month and Year selection for end date filtering
            months = ["All", "January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
            filter_month = st.selectbox("End Date Month", months, key="filter_month")
            
            # Get current year and create a range of years from 5 years back
            current_year = datetime.now().year
            years = ["All"] + [str(current_year - i) for i in range(6)]
            filter_year = st.selectbox("End Date Year", years, key="filter_year")
            
            # Set filters based on month and year selection
            if filter_month != "All" or filter_year != "All":
                month_num = months.index(filter_month) if filter_month != "All" else None
                year_num = int(filter_year) if filter_year != "All" else None
                st.session_state.filters['end_date_month_year'] = (month_num, year_num)
            elif 'end_date_month_year' in st.session_state.filters:
                del st.session_state.filters['end_date_month_year']
        
        with filter_col5:
            amount_col1, amount_col2 = st.columns(2)
            
            with amount_col1:
                min_amount = st.number_input(
                    "Min Amount", 
                    min_value=0, 
                    value=0, 
                    step=1000
                )
                
                if min_amount > 0:
                    st.session_state.filters['min_amount'] = min_amount
                elif 'min_amount' in st.session_state.filters:
                    del st.session_state.filters['min_amount']
            
            with amount_col2:
                max_amount = st.number_input(
                    "Max Amount", 
                    min_value=0, 
                    value=0, 
                    step=1000
                )
                
                if max_amount > 0:
                    st.session_state.filters['max_amount'] = max_amount
                elif 'max_amount' in st.session_state.filters:
                    del st.session_state.filters['max_amount']
        
        # Clear filters button
        if st.button("Clear Filters"):
            st.session_state.filters = {}
            st.rerun()
    
    # Form to add new transaction or edit existing transaction
    if st.session_state.show_add_transaction_form or st.session_state.edit_transaction:
        st.subheader("Add New Transaction" if not st.session_state.edit_transaction else "Edit Transaction")
        
        # Get all parties for dropdowns
        apnaar_parties = db.get_all_apnaar_parties()
        lenaar_parties = db.get_all_lenaar_parties()
        kapine_lenaar_parties = db.get_all_kapine_lenaar_parties()
        
        # Get transaction data if editing
        transaction_data = {}
        if st.session_state.edit_transaction:
            transaction = db.get_transaction_by_id(st.session_state.edit_transaction)
            if transaction:
                transaction_data = transaction
        
        with st.form(key="transaction_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Apnaar Party selection
                apnaar_party_id = st.selectbox(
                    "Apnaar Party*",
                    options=[p[0] for p in apnaar_parties],
                    format_func=lambda x: next((p[1] for p in apnaar_parties if p[0] == x), ""),
                    index=next((i for i, p in enumerate(apnaar_parties) if p[0] == transaction_data.get('apnaar_party_id')), 0) if apnaar_parties else 0,
                )
                
                # Get the name for the selected ID
                apnaar_party_name = next((p[1] for p in apnaar_parties if p[0] == apnaar_party_id), "")
            
            with col2:
                # Lenaar Party selection
                lenaar_party_id = st.selectbox(
                    "Lenaar Party*",
                    options=[p[0] for p in lenaar_parties],
                    format_func=lambda x: next((p[1] for p in lenaar_parties if p[0] == x), ""),
                    index=next((i for i, p in enumerate(lenaar_parties) if p[0] == transaction_data.get('lenaar_party_id')), 0) if lenaar_parties else 0,
                )
                
                # Get the name for the selected ID
                lenaar_party_name = next((p[1] for p in lenaar_parties if p[0] == lenaar_party_id), "")
            
            with col3:
                # Kapine Lenaar Party selection (optional)
                kapine_lenaar_party_options = [0] + [p[0] for p in kapine_lenaar_parties]
                kapine_lenaar_party_id = st.selectbox(
                    "Kapine Lenaar Party (Optional)",
                    options=kapine_lenaar_party_options,
                    format_func=lambda x: "None" if x == 0 else next((p[1] for p in kapine_lenaar_parties if p[0] == x), ""),
                    index=next((i for i, p in enumerate(kapine_lenaar_party_options) if p == transaction_data.get('kapine_lenaar_party_id', 0)), 0),
                )
                
                # Treat 0 as None for the database
                if kapine_lenaar_party_id == 0:
                    kapine_lenaar_party_id = None
                
                # Get the name for the selected ID
                kapine_lenaar_party_name = next((p[1] for p in kapine_lenaar_parties if p[0] == kapine_lenaar_party_id), "") if kapine_lenaar_party_id else ""
            
            # Financial details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_amount = st.number_input(
                    "Total Amount (₹)*",
                    min_value=0.0,
                    value=float(transaction_data.get('total_amount', 0.0)),
                    step=1000.0
                )
            
            with col2:
                interest_rate = st.number_input(
                    "Interest Rate (%)*",
                    min_value=0.0,
                    value=float(transaction_data.get('interest_rate', 0.0)) * 100 if transaction_data.get('interest_rate') else 0.0,
                    step=0.1
                )
            
            with col3:
                dalali_rate = st.number_input(
                    "Dalali Rate (%)",
                    min_value=0.0,
                    value=float(transaction_data.get('dalali_rate', 0.0)) * 100 if transaction_data.get('dalali_rate') else 0.0,
                    step=0.1
                )
            
            # Date range and condition
            col1, col2, col3 = st.columns(3)
            
            with col1:
                start_date = st.date_input(
                    "Start Date*",
                    value=parse_date(transaction_data.get('start_date')) if transaction_data.get('start_date') else datetime.now()
                )
            
            with col2:
                end_date = st.date_input(
                    "End Date*",
                    value=parse_date(transaction_data.get('end_date')) if transaction_data.get('end_date') else (datetime.now() + timedelta(days=30))
                )
            
            with col3:
                condition = st.text_input(
                    "Condition",
                    value=transaction_data.get('condition', '')
                )
            
            # Year type for calculation
            year_type_selection = st.radio(
                "Year Type for Calculation",
                options=["365 days (Default)", "Custom"],
                index=0,
                horizontal=True
            )
            
            # If custom is selected, show a number input field
            if year_type_selection == "Custom":
                year_type = st.number_input(
                    "Custom Year Type (days)",
                    min_value=300,
                    max_value=366,
                    value=360,
                    step=1,
                    help="Enter the number of days to use for the yearly calculation"
                )
            else:
                year_type = 365
            
            # Calculate button to preview calculations
            if st.form_submit_button("Calculate"):
                # Convert percentage rates to decimal
                interest_rate_decimal = interest_rate / 100
                dalali_rate_decimal = dalali_rate / 100
                
                # Perform calculations
                calculations = calculate_all(
                    total_amount, 
                    interest_rate, 
                    dalali_rate, 
                    start_date, 
                    end_date, 
                    year_type
                )
                
                # Display calculation results
                st.subheader("Calculation Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Number of Days", calculations['number_of_days'])
                    st.metric("Number of Months", f"{calculations['number_of_months']:.2f}")
                    st.metric("Interest Amount", format_currency(calculations['interest_amount']))
                    st.metric("Dalali Amount", format_currency(calculations['dalali_amount']))
                
                with col2:
                    st.metric("Lenaar Return Amount", format_currency(calculations['lenaar_return_amount']))
                    st.metric("Apnaar Received Amount", format_currency(calculations['apnaar_received_amount']))
                    st.metric("Interest Received by Apnaar", format_currency(calculations['interest_received_by_apnar']))
            
            # Submit button for the form
            if st.form_submit_button("Save Transaction"):
                # Convert percentage rates to decimal
                interest_rate_decimal = interest_rate / 100
                dalali_rate_decimal = dalali_rate / 100
                
                # Perform calculations
                calculations = calculate_all(
                    total_amount, 
                    interest_rate, 
                    dalali_rate, 
                    start_date, 
                    end_date, 
                    year_type
                )
                
                # Prepare transaction data
                transaction_data = {
                    'apnaar_party_id': apnaar_party_id,
                    'lenaar_party_id': lenaar_party_id,
                    'kapine_lenaar_party_id': kapine_lenaar_party_id,
                    'total_amount': total_amount,
                    'condition': condition,
                    'start_date': start_date,
                    'end_date': end_date,
                    'number_of_days': calculations['number_of_days'],
                    'number_of_months': calculations['number_of_months'],
                    'interest_rate': interest_rate_decimal,
                    'dalali_rate': dalali_rate_decimal,
                    'interest_amount': calculations['interest_amount'],
                    'dalali_amount': calculations['dalali_amount'],
                    'lenaar_return_amount': calculations['lenaar_return_amount'],
                    'apnaar_received_amount': calculations['apnaar_received_amount'],
                    'interest_received_by_apnar': calculations['interest_received_by_apnar'],
                }
                
                # Validate input data
                errors = validate_transaction_input(transaction_data)
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    success = False
                    
                    if st.session_state.edit_transaction:
                        # Update existing transaction
                        success = db.update_transaction(st.session_state.edit_transaction, transaction_data)
                        if success:
                            st.success("Transaction updated successfully")
                            st.session_state.edit_transaction = None
                            st.session_state.show_add_transaction_form = False
                            st.rerun()
                        else:
                            st.error("Failed to update transaction")
                    else:
                        # Add new transaction
                        transaction_id = db.add_transaction(transaction_data)
                        if transaction_id:
                            st.success("Transaction added successfully")
                            st.session_state.show_add_transaction_form = False
                            st.rerun()
                        else:
                            st.error("Failed to add transaction")
        
        # Cancel button outside the form
        if st.button("Cancel"):
            st.session_state.show_add_transaction_form = False
            st.session_state.edit_transaction = None
            st.rerun()
    
    # Partial Payment Form
    if st.session_state.show_partial_payment_form and st.session_state.selected_transaction_for_payment:
        transaction_id = st.session_state.selected_transaction_for_payment
        transaction = db.get_transaction_by_id(transaction_id)
        
        if transaction:
            st.subheader(f"Manage Partial Payments")
            
            # Display transaction details
            st.markdown(f"""
            ### Transaction Details
            - **Apnaar Party:** {transaction['apnaar_party_name']}
            - **Lenaar Party:** {transaction['lenaar_party_name']}
            - **Total Amount:** {format_currency(transaction['total_amount'])}
            - **Start Date:** {format_date(transaction['start_date'])}
            - **End Date:** {format_date(transaction['end_date'])}
            """)
            
            # Show remaining balance and pending interest/dalali
            remaining_amount = transaction.get('remaining_amount', transaction['total_amount'])
            pending_calcs = db.calculate_pending_interest_dalali(transaction_id)
            
            st.markdown("### Current Status")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Remaining Amount", format_currency(remaining_amount))
            
            if pending_calcs:
                with col2:
                    st.metric(
                        "Pending Interest", 
                        format_currency(pending_calcs['interest_amount']),
                        f"{pending_calcs['days_since_last_payment']} days"
                    )
                
                with col3:
                    st.metric(
                        "Pending Dalali", 
                        format_currency(pending_calcs['dalali_amount'])
                    )
            
            # Form to add new partial payment
            st.subheader("Add Partial Payment")
            
            with st.form(key="add_partial_payment_form"):
                payment_amount = st.number_input(
                    "Payment Amount*", 
                    min_value=0.0, 
                    max_value=float(remaining_amount),
                    step=1000.0
                )
                
                payment_date = st.date_input(
                    "Payment Date*",
                    value=datetime.now().date()
                )
                
                notes = st.text_area("Notes")
                
                submitted = st.form_submit_button("Add Payment")
                
                if submitted:
                    if payment_amount <= 0:
                        st.error("Payment amount must be greater than 0")
                    elif payment_amount > remaining_amount:
                        st.error(f"Payment amount cannot exceed remaining balance of {format_currency(remaining_amount)}")
                    else:
                        success, message = db.add_partial_payment(
                            transaction_id,
                            payment_date.strftime("%Y-%m-%d"),
                            payment_amount,
                            notes
                        )
                        
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            # Display existing partial payments
            st.subheader("Payment History")
            payments = db.get_partial_payments(transaction_id)
            
            if payments:
                payment_df = pd.DataFrame(payments)
                display_df = payment_df[[
                    'id', 'payment_date', 'payment_amount', 'notes'
                ]].copy()
                
                display_df.columns = [
                    'Payment ID', 'Payment Date', 'Amount (₹)', 'Notes'
                ]
                
                # Format columns
                display_df['Amount (₹)'] = display_df['Amount (₹)'].apply(lambda x: format_currency(x))
                display_df['Payment Date'] = display_df['Payment Date'].apply(format_date)
                
                st.dataframe(display_df, use_container_width=True)
                
                # Delete payment functionality
                st.markdown("### Delete Payment")
                
                payment_to_delete = st.selectbox(
                    "Select payment to delete",
                    options=payment_df['id'].tolist(),
                    format_func=lambda x: f"ID: {x} - {payment_df[payment_df['id'] == x]['payment_date'].iloc[0]} - {format_currency(payment_df[payment_df['id'] == x]['payment_amount'].iloc[0])}"
                )
                
                if st.button("Delete Selected Payment"):
                    if st.session_state.get('confirm_delete_payment') == payment_to_delete:
                        success, message = db.delete_partial_payment(payment_to_delete)
                        
                        if success:
                            st.success(message)
                            st.session_state.pop('confirm_delete_payment', None)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.session_state.confirm_delete_payment = payment_to_delete
                        st.warning("Click the delete button again to confirm deletion.")
            else:
                st.info("No partial payments made yet.")
            
            # Button to go back
            if st.button("Back to Transactions"):
                st.session_state.show_partial_payment_form = False
                st.session_state.selected_transaction_for_payment = None
                st.rerun()
    
    # Display transactions table
    st.subheader("All Transactions")
    
    # Get transactions with applied filters
    transactions = db.get_transactions(st.session_state.filters)
    
    # Calculate summary totals
    if transactions:
        total_amount = sum(t['total_amount'] for t in transactions)
        total_dalali = sum(t['dalali_amount'] for t in transactions)
        total_interest = sum(t['interest_amount'] for t in transactions)
        
        # Display summary metrics in columns
        total_col1, total_col2, total_col3 = st.columns(3)
        
        with total_col1:
            st.metric("Total Amount", format_currency(total_amount))
        
        with total_col2:
            st.metric("Total Dalali Amount", format_currency(total_dalali))
        
        with total_col3:
            st.metric("Total Interest Amount", format_currency(total_interest))
    
    if transactions:
        # Create a DataFrame for display
        df = pd.DataFrame(transactions)
        
        # Format the DataFrame for display
        display_df = df[[
            'id', 'apnaar_party_name', 'lenaar_party_name', 'kapine_lenaar_party_name',
            'total_amount', 'remaining_amount', 'condition', 'start_date', 'end_date', 'number_of_days',
            'number_of_months', 'interest_rate', 'dalali_rate', 'interest_amount',
            'dalali_amount', 'lenaar_return_amount', 'apnaar_received_amount',
            'interest_received_by_apnar', 'received'
        ]].copy()
        
        # Rename columns for better display
        display_df.columns = [
            'ID', 'Apnaar Party', 'Lenaar Party', 'Kapine Lenaar Party',
            'Total Amount (₹)', 'Remaining (₹)', 'Condition', 'Start Date', 'End Date', 'Days',
            'Months', 'Interest Rate (%)', 'Dalali Rate (%)', 'Interest Amount (₹)',
            'Dalali Amount (₹)', 'Lenaar Return (₹)', 'Apnaar Received (₹)',
            'Interest Received (₹)', 'Received'
        ]
        
        # Format numeric and date columns
        display_df['Total Amount (₹)'] = display_df['Total Amount (₹)'].apply(lambda x: format_currency(x))
        display_df['Remaining (₹)'] = display_df['Remaining (₹)'].apply(lambda x: format_currency(x) if pd.notnull(x) else format_currency(0))
        display_df['Interest Amount (₹)'] = display_df['Interest Amount (₹)'].apply(lambda x: format_currency(x))
        display_df['Dalali Amount (₹)'] = display_df['Dalali Amount (₹)'].apply(lambda x: format_currency(x))
        display_df['Lenaar Return (₹)'] = display_df['Lenaar Return (₹)'].apply(lambda x: format_currency(x))
        display_df['Apnaar Received (₹)'] = display_df['Apnaar Received (₹)'].apply(lambda x: format_currency(x))
        display_df['Interest Received (₹)'] = display_df['Interest Received (₹)'].apply(lambda x: format_currency(x))
        display_df['Interest Rate (%)'] = display_df['Interest Rate (%)'].apply(lambda x: f"{x*100:.2f}%")
        display_df['Dalali Rate (%)'] = display_df['Dalali Rate (%)'].apply(lambda x: f"{x*100:.2f}%")
        display_df['Start Date'] = display_df['Start Date'].apply(format_date)
        display_df['End Date'] = display_df['End Date'].apply(format_date)
        display_df['Received'] = display_df['Received'].map({0: '❌', 1: '✅'})
        
        # Display the styled dataframe
        st.dataframe(display_df, use_container_width=True)
        
        # Add action buttons for the selected transaction
        selected_transaction = st.selectbox(
            "Select a transaction to perform actions",
            options=df['id'].tolist(),
            format_func=lambda x: f"ID: {x} - {df[df['id'] == x]['apnaar_party_name'].iloc[0]} to {df[df['id'] == x]['lenaar_party_name'].iloc[0]} - {format_currency(df[df['id'] == x]['total_amount'].iloc[0])}"
        )
        
        if selected_transaction:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("✏️ Edit Selected Transaction"):
                    st.session_state.edit_transaction = selected_transaction
                    st.session_state.show_add_transaction_form = True
                    st.rerun()
            
            with col2:
                # Get current received status
                selected_row = df[df['id'] == selected_transaction].iloc[0]
                current_status = selected_row['received']
                
                if st.button("📝 Mark as " + ("Pending" if current_status else "Received")):
                    success = db.update_transaction_received_status(
                        selected_transaction, 
                        not current_status
                    )
                    if success:
                        st.success(f"Transaction marked as {'Pending' if current_status else 'Received'}")
                        st.rerun()
                    else:
                        st.error("Failed to update transaction status")
            
            with col3:
                # Button to manage partial payments
                if st.button("💰 Partial Payments"):
                    st.session_state.selected_transaction_for_payment = selected_transaction
                    st.session_state.show_partial_payment_form = True
                    st.rerun()
            
            with col4:
                if st.button("❌ Delete Selected Transaction"):
                    if st.session_state.get('confirm_delete_transaction') == selected_transaction:
                        success = db.delete_transaction(selected_transaction)
                        if success:
                            st.success("Transaction deleted successfully")
                            st.session_state.pop('confirm_delete_transaction', None)
                            st.rerun()
                        else:
                            st.error("Failed to delete transaction")
                    else:
                        st.session_state.confirm_delete_transaction = selected_transaction
                        st.warning("Click the delete button again to confirm deletion.")
            
            with col5:
                if st.button("📊 Export Data"):
                    export_format = st.radio(
                        "Export Format",
                        ["CSV", "Excel"],
                        horizontal=True
                    )
                    
                    if st.button(f"Export as {export_format}"):
                        filename = export_data(
                            df, 
                            export_format.lower(), 
                            "transactions"
                        )
                        if filename:
                            st.success(f"Data exported to {filename}")
                        else:
                            st.error("Failed to export data")
    else:
        st.info("No transactions found. Add your first transaction to get started.")

# All Entries Page - Excel-like interface
elif page == "All Entries":
    styled_header("All Entries")
    st.subheader("Excel-like View with Filters")
    
    # Get all transactions
    all_transactions = db.get_transactions()
    
    # Initialize column filters in session state if not already present
    if 'all_entries_filters' not in st.session_state:
        st.session_state.all_entries_filters = {}
    
    if not all_transactions:
        st.info("No transactions found. Add your first transaction to get started.")
    else:
        # Create a DataFrame for display
        df = pd.DataFrame(all_transactions)
        
        # Convert necessary columns to appropriate types
        if 'start_date' in df.columns:
            df['start_date'] = pd.to_datetime(df['start_date'])
        if 'end_date' in df.columns:
            df['end_date'] = pd.to_datetime(df['end_date'])
        
        # Calculate additional fields for each transaction
        calculated_data = []
        
        for _, row in df.iterrows():
            # Use the calculate_all function from calculations.py
            calc_results = calculate_all(
                row['total_amount'],
                row['interest_rate'] * 100,  # Convert to percentage
                row['dalali_rate'] * 100,    # Convert to percentage
                row['start_date'],
                row['end_date']
            )
            
            # Add calculated values
            row_data = {
                'id': row['id'],
                'apnaar_party_name': row['apnaar_party_name'],
                'lenaar_party_name': row['lenaar_party_name'],
                'kapine_lenaar_party_name': row['kapine_lenaar_party_name'],
                'total_amount': row['total_amount'],
                'condition': row['condition'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'number_of_days': calc_results['number_of_days'],
                'number_of_months': round(calc_results['number_of_months'], 2),
                'interest_rate': row['interest_rate'] * 100,  # Convert to percentage
                'dalali_rate': row['dalali_rate'] * 100,      # Convert to percentage
                'interest_amount': calc_results['interest_amount'],
                'dalali_amount': calc_results['dalali_amount'],
                'lenaar_return_amount': calc_results['lenaar_return_amount'],
                'apnaar_received_amount': calc_results['apnaar_received_amount'],
                'interest_received_by_apnar': calc_results['interest_received_by_apnar'],
                'received': row['received'],
                'remaining_amount': row.get('remaining_amount', row['total_amount'])
            }
            
            # If there's a remaining amount, calculate pending interest and dalali
            if row.get('remaining_amount', 0) > 0 and row['remaining_amount'] != row['total_amount']:
                # Get partial payments to find the last payment date
                partial_payments = db.get_partial_payments(row['id'])
                
                if partial_payments:
                    # Get the latest payment date from the list of payment dates
                    payment_dates = [parse_date(payment['payment_date']) for payment in partial_payments if payment['payment_date']]
                    if payment_dates and all(date is not None for date in payment_dates):
                        latest_payment_date = max(date for date in payment_dates if date is not None)
                    
                    # Calculate pending interest and dalali from last payment date until today
                    pending_calcs = db.calculate_pending_interest_dalali(row['id'])
                    
                    # Add pending interest and dalali to the row data
                    if pending_calcs:
                        row_data['pending_interest'] = pending_calcs['pending_interest']
                        row_data['pending_dalali'] = pending_calcs['pending_dalali']
                        # Use the imported function from calculations.py
                        from calculations import calculate_remaining_lenaar_return_amount
                        row_data['remaining_lenaar_return'] = calculate_remaining_lenaar_return_amount(
                            row['remaining_amount'], pending_calcs['pending_interest']
                        )
            
            calculated_data.append(row_data)
        
        # Create a DataFrame with all calculated data
        calculated_df = pd.DataFrame(calculated_data)
        
        # Get all unique values for each column for filters
        st.write("### Filters")
        st.write("Use the following filters to narrow down your view:")
        
        # Create filter columns
        filter_cols = st.columns(4)
        
        # Filter for Apnaar Party Name
        with filter_cols[0]:
            apnaar_party_options = ["All"] + sorted(calculated_df['apnaar_party_name'].unique().tolist())
            selected_apnaar = st.selectbox("Apnaar Party", apnaar_party_options, key="filter_apnaar_all")
            
            if selected_apnaar != "All":
                st.session_state.all_entries_filters['apnaar_party_name'] = selected_apnaar
            elif 'apnaar_party_name' in st.session_state.all_entries_filters:
                del st.session_state.all_entries_filters['apnaar_party_name']
        
        # Filter for Lenaar Party Name
        with filter_cols[1]:
            lenaar_party_options = ["All"] + sorted(calculated_df['lenaar_party_name'].unique().tolist())
            selected_lenaar = st.selectbox("Lenaar Party", lenaar_party_options, key="filter_lenaar_all")
            
            if selected_lenaar != "All":
                st.session_state.all_entries_filters['lenaar_party_name'] = selected_lenaar
            elif 'lenaar_party_name' in st.session_state.all_entries_filters:
                del st.session_state.all_entries_filters['lenaar_party_name']
        
        # Filter for Status (Received)
        with filter_cols[2]:
            received_options = ["All", "Received", "Pending"]
            selected_received = st.selectbox("Status", received_options, key="filter_received_all")
            
            if selected_received == "Received":
                st.session_state.all_entries_filters['received'] = True
            elif selected_received == "Pending":
                st.session_state.all_entries_filters['received'] = False
            elif 'received' in st.session_state.all_entries_filters:
                del st.session_state.all_entries_filters['received']
        
        # Filter by Date Type first
        with filter_cols[3]:
            date_filter_type = st.selectbox(
                "Date Filter Type", 
                ["Month & Year", "Custom Date Range", "None"],
                key="date_filter_type"
            )
        
        # Create additional rows for more filters
        filter_row2 = st.columns(4)
        filter_row3 = st.columns(4)
        
        # Initialize filtered dataframe
        filtered_df = calculated_df.copy()
        
        # Apply base filters from session state
        for column, value in st.session_state.all_entries_filters.items():
            if column in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[column] == value]
        
        # Apply different date filters based on selection
        if date_filter_type == "Month & Year":
            with filter_row2[0]:
                # Month selection for end date filtering
                months = ["All", "January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"]
                filter_month = st.selectbox("End Date Month", months, key="filter_month_all")
            
            with filter_row2[1]:
                # Get current year and create a range of years from 5 years back
                current_year = datetime.now().year
                years = ["All"] + [str(current_year - i) for i in range(6)]
                filter_year = st.selectbox("End Date Year", years, key="filter_year_all")
            
            # Apply month filter
            if filter_month != "All":
                month_num = months.index(filter_month)
                filtered_df = filtered_df[filtered_df['end_date'].dt.month == month_num]
            
            # Apply year filter
            if filter_year != "All":
                year_num = int(filter_year)
                filtered_df = filtered_df[filtered_df['end_date'].dt.year == year_num]
                
        elif date_filter_type == "Custom Date Range":
            with filter_row2[0]:
                # Date field selection
                date_field = st.selectbox(
                    "Date Field", 
                    ["End Date", "Start Date"],
                    key="date_field_select"
                )
            
            with filter_row2[1]:
                # From date
                from_date = st.date_input(
                    "From Date",
                    value=datetime.now() - timedelta(days=30),
                    key="from_date_custom"
                )
            
            with filter_row2[2]:
                # To date
                to_date = st.date_input(
                    "To Date",
                    value=datetime.now(),
                    key="to_date_custom"
                )
            
            # Convert dates to datetime for comparison
            from_datetime = pd.to_datetime(from_date)
            to_datetime = pd.to_datetime(to_date) + timedelta(days=1)  # Include the end date
            
            # Apply date range filter
            if date_field == "End Date":
                filtered_df = filtered_df[(filtered_df['end_date'] >= from_datetime) & 
                                         (filtered_df['end_date'] < to_datetime)]
            else:
                filtered_df = filtered_df[(filtered_df['start_date'] >= from_datetime) & 
                                         (filtered_df['start_date'] < to_datetime)]
            
            # Add a button to clear date filters
            with filter_row3[0]:
                if st.button("Clear Date Filters"):
                    # This will cause a rerun with the default filter
                    st.rerun()
        
        # Display summary metrics for filtered data
        st.write("### Summary of Filtered Data")
        summary_cols = st.columns(5)
        
        with summary_cols[0]:
            st.metric("Total Transactions", len(filtered_df))
        
        with summary_cols[1]:
            total_amount = filtered_df['total_amount'].sum()
            st.metric("Total Amount", format_currency(total_amount))
        
        with summary_cols[2]:
            total_dalali = filtered_df['dalali_amount'].sum()
            st.metric("Total Dalali", format_currency(total_dalali))
        
        with summary_cols[3]:
            total_interest = filtered_df['interest_amount'].sum()
            st.metric("Total Interest", format_currency(total_interest))
        
        with summary_cols[4]:
            total_lenaar_return = filtered_df['lenaar_return_amount'].sum()
            st.metric("Total Lenaar Return", format_currency(total_lenaar_return))
        
        # Format the DataFrame for display
        display_df = filtered_df.copy()
        
        # Rename columns for better display
        display_columns = {
            'id': 'ID',
            'apnaar_party_name': 'Apnaar Party',
            'lenaar_party_name': 'Lenaar Party',
            'kapine_lenaar_party_name': 'Kapine Lenaar Party',
            'total_amount': 'Total Amount (₹)',
            'condition': 'Condition',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'number_of_days': 'Days',
            'number_of_months': 'Months',
            'interest_rate': 'Interest Rate (%)',
            'dalali_rate': 'Dalali Rate (%)',
            'interest_amount': 'Interest Amount (₹)',
            'dalali_amount': 'Dalali Amount (₹)',
            'lenaar_return_amount': 'Lenaar Return (₹)',
            'apnaar_received_amount': 'Apnaar Received (₹)',
            'interest_received_by_apnar': 'Interest Received (₹)',
            'received': 'Status',
            'remaining_amount': 'Remaining Amount (₹)'
        }
        
        # Rename the columns
        display_df = display_df.rename(columns=display_columns)
        
        # Format numeric columns
        numeric_columns = [
            'Total Amount (₹)', 'Interest Amount (₹)', 'Dalali Amount (₹)',
            'Lenaar Return (₹)', 'Apnaar Received (₹)', 'Interest Received (₹)',
            'Remaining Amount (₹)'
        ]
        
        for col in numeric_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x) if pd.notna(x) else "")
        
        # Format date columns
        date_columns = ['Start Date', 'End Date']
        for col in date_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: format_date(x) if pd.notna(x) else "")
        
        # Format status column
        if 'Status' in display_df.columns:
            display_df['Status'] = display_df['Status'].map({True: '✅ Received', False: '❌ Pending'})
        
        # Display the dataframe with all entries
        st.write("### All Entries")
        st.dataframe(display_df, use_container_width=True)
        
        # Add options for transaction actions
        st.write("### Transaction Actions")
        
        selected_transaction = None
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            transaction_ids = filtered_df['id'].unique().tolist()
            if transaction_ids:
                selected_transaction = st.selectbox(
                    "Select a Transaction",
                    options=transaction_ids,
                    format_func=lambda x: f"ID: {x} - {filtered_df[filtered_df['id'] == x]['apnaar_party_name'].iloc[0]} to {filtered_df[filtered_df['id'] == x]['lenaar_party_name'].iloc[0]} ({format_currency(filtered_df[filtered_df['id'] == x]['total_amount'].iloc[0])})"
                )
        
        with action_col2:
            if selected_transaction is not None:
                if st.button("Edit Transaction", key="edit_from_all"):
                    st.session_state.edit_transaction = selected_transaction
                    st.session_state.page = "Transactions"
                    st.rerun()
        
        with action_col3:
            if selected_transaction is not None:
                if st.button("Record Payment", key="payment_from_all"):
                    st.session_state.show_partial_payment_form = True
                    st.session_state.selected_transaction_for_payment = selected_transaction
                    st.session_state.page = "Payments"
                    st.rerun()
        
        # Export options
        st.write("### Export Data")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("Export to Excel", key="export_excel_all"):
                try:
                    # Export the filtered DataFrame to Excel
                    filename = export_data(filtered_df.copy(), "excel", "all_entries")
                    st.success(f"Data exported to {filename}")
                    # Provide download link
                    if filename:
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="Download Excel File",
                                data=file,
                                file_name=os.path.basename(filename),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                except Exception as e:
                    st.error(f"Error exporting data: {e}")
        
        with export_col2:
            if st.button("Export to CSV", key="export_csv_all"):
                try:
                    # Export the filtered DataFrame to CSV
                    filename = export_data(filtered_df.copy(), "csv", "all_entries")
                    st.success(f"Data exported to {filename}")
                    # Provide download link
                    if filename:
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="Download CSV File",
                                data=file,
                                file_name=os.path.basename(filename),
                                mime="text/csv"
                            )
                except Exception as e:
                    st.error(f"Error exporting data: {e}")

# Payments Page
elif page == "Payments":
    styled_header("Payments")
    st.subheader("Record Payment Entries")
    
    # Get all transactions with pending payments for selection
    pending_transactions = db.get_transactions(filters={"received": False})
    
    # Define selected_transaction outside the form to avoid scoping issues
    selected_transaction = None
    transaction_id = None
    
    # Add payment form
    with st.form(key="payment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction selection
            if pending_transactions:
                transaction_options = [(t['id'], f"{t['apnaar_party_name']} - {t['lenaar_party_name']} - {format_currency(t['total_amount'])} (Remaining: {format_currency(t['remaining_amount'])})") for t in pending_transactions]
                transaction_id = st.selectbox(
                    "Select Transaction*",
                    options=[t[0] for t in transaction_options],
                    format_func=lambda x: next((t[1] for t in transaction_options if t[0] == x), ""),
                )
                
                # Get the selected transaction for display
                selected_transaction = next((t for t in pending_transactions if t['id'] == transaction_id), None)
                
                if selected_transaction:
                    st.info(f"Remaining Amount: {format_currency(selected_transaction['remaining_amount'])}")
                    
                    # Display additional transaction details
                    with st.expander("Transaction Details"):
                        st.write(f"**Apnaar Party:** {selected_transaction['apnaar_party_name']}")
                        st.write(f"**Lenaar Party:** {selected_transaction['lenaar_party_name']}")
                        st.write(f"**Total Amount:** {format_currency(selected_transaction['total_amount'])}")
                        st.write(f"**Original Interest Amount:** {format_currency(selected_transaction['interest_amount'])}")
                        st.write(f"**Original Dalali Amount:** {format_currency(selected_transaction['dalali_amount'])}")
                        st.write(f"**Original Lenaar Return Amount:** {format_currency(selected_transaction['lenaar_return_amount'])}")
                        st.write(f"**Start Date:** {format_date(selected_transaction['start_date'])}")
                        st.write(f"**End Date:** {format_date(selected_transaction['end_date'])}")
                        st.write(f"**Interest Rate:** {selected_transaction['interest_rate']*100:.2f}%")
                        st.write(f"**Dalali Rate:** {selected_transaction['dalali_rate']*100:.2f}%")
            else:
                st.warning("No pending transactions found. All transactions are marked as received.")
                transaction_id = None
        
        # Store the max value and default value for the payment amount
        max_amount = 0.0
        default_amount = 0.0
        if selected_transaction is not None:
            try:
                max_amount = float(selected_transaction.get('remaining_amount', 0.0))
                default_amount = float(selected_transaction.get('remaining_amount', 0.0))
            except (TypeError, ValueError, AttributeError):
                max_amount = 0.0
                default_amount = 0.0
        
        with col2:
            payment_date = st.date_input("Payment Date*", value=datetime.now())
            payment_amount = st.number_input(
                "Payment Amount (₹)*",
                min_value=0.0,
                max_value=max_amount,
                value=default_amount,
                step=1000.0
            )
            notes = st.text_area("Notes", placeholder="Add any additional notes about this payment...")
        
        submit_button = st.form_submit_button("Record Payment")
    
    # Process form submission outside the form
    if submit_button:
        if not transaction_id:
            st.error("Please select a transaction.")
        elif payment_amount <= 0:
            st.error("Payment amount must be greater than zero.")
        elif selected_transaction is not None:
            try:
                remaining = float(selected_transaction.get('remaining_amount', 0.0))
                if payment_amount > remaining:
                    st.error(f"Payment amount cannot exceed the remaining amount ({format_currency(remaining)}).")
                else:
                    # Continue with payment processing - Move the payment recording here
                    # Record the payment
                    success = db.add_partial_payment(transaction_id, payment_date.strftime("%Y-%m-%d"), payment_amount, notes)
                    if success:
                        st.success("Payment recorded successfully!")
                        
                        # Check if this was the final payment
                        updated_transaction = db.get_transaction_by_id(transaction_id)
                        if updated_transaction and updated_transaction['remaining_amount'] == 0:
                            # Mark the transaction as received if fully paid
                            db.update_transaction_received_status(transaction_id, True)
                            st.success("Transaction marked as fully received!")
                        
                        # Calculate pending interest and dalali
                        pending_calculations = db.calculate_pending_interest_dalali(transaction_id)
                        if pending_calculations and isinstance(pending_calculations, dict):
                            st.info(
                                f"Pending interest: {format_currency(pending_calculations['interest_amount'])}, " +
                                f"Pending dalali: {format_currency(pending_calculations['dalali_amount'])}, " +
                                f"Lenaar Return Amount: {format_currency(pending_calculations['remaining_lenaar_return_amount'])}"
                            )
                        
                        # Rerun to refresh the form
                        st.rerun()
                    else:
                        st.error("Failed to record payment.")
            except (TypeError, ValueError, AttributeError):
                st.error("Error retrieving remaining amount.")
        else:
            # For any other case not captured above
            st.error("Please select a valid transaction.")
    
    # Display payment history
    st.subheader("Payment History")
    
    # Add tabs for different payment views
    tab1, tab2 = st.tabs(["Recent Payments", "Search Payments"])
    
    with tab1:
        # Get all transactions with partial payments
        partial_payments_query = '''
        SELECT 
            pp.id as payment_id, 
            t.id as transaction_id,
            ap.name as apnaar_party_name, 
            lp.name as lenaar_party_name,
            pp.payment_date, 
            pp.payment_amount,
            pp.notes,
            t.total_amount,
            t.remaining_amount
        FROM partial_payments pp
        JOIN transactions t ON pp.transaction_id = t.id
        JOIN apnaar_parties ap ON t.apnaar_party_id = ap.id
        JOIN lenaar_parties lp ON t.lenaar_party_id = lp.id
        ORDER BY pp.payment_date DESC
        LIMIT 20
        '''
        try:
            db.cursor.execute(partial_payments_query)
            columns = [column[0] for column in db.cursor.description]
            payments = []
            for row in db.cursor.fetchall():
                payments.append(dict(zip(columns, row)))
                
            if payments:
                # Convert to DataFrame for display
                df = pd.DataFrame(payments)
                
                # Format columns for display
                display_df = df[[
                    'payment_id', 'transaction_id', 'apnaar_party_name', 
                    'lenaar_party_name', 'payment_date', 'payment_amount', 
                    'total_amount', 'remaining_amount', 'notes'
                ]].copy()
                
                # Rename columns for better display
                display_df.columns = [
                    'Payment ID', 'Transaction ID', 'Apnaar Party', 
                    'Lenaar Party', 'Payment Date', 'Payment Amount (₹)', 
                    'Total Amount (₹)', 'Remaining Amount (₹)', 'Notes'
                ]
                
                # Format numeric and date columns
                display_df['Payment Amount (₹)'] = display_df['Payment Amount (₹)'].apply(lambda x: format_currency(x))
                display_df['Total Amount (₹)'] = display_df['Total Amount (₹)'].apply(lambda x: format_currency(x))
                display_df['Remaining Amount (₹)'] = display_df['Remaining Amount (₹)'].apply(lambda x: format_currency(x))
                display_df['Payment Date'] = display_df['Payment Date'].apply(format_date)
                
                # Display the dataframe
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No payment history found.")
        except Exception as e:
            st.error(f"Error fetching payment history: {e}")
    
    with tab2:
        # Add search functionality for payments
        st.write("Search payments by party name or date range")
        
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            search_apnaar = st.text_input("Search by Apnaar Party Name")
        
        with search_col2:
            search_lenaar = st.text_input("Search by Lenaar Party Name")
        
        date_col1, date_col2 = st.columns(2)
        
        with date_col1:
            start_search_date = st.date_input("From Date", value=datetime.now() - timedelta(days=30))
        
        with date_col2:
            end_search_date = st.date_input("To Date", value=datetime.now())
        
        # Apply search button
        if st.button("Search Payments"):
            search_query = '''
            SELECT 
                pp.id as payment_id, 
                t.id as transaction_id,
                ap.name as apnaar_party_name, 
                lp.name as lenaar_party_name,
                pp.payment_date, 
                pp.payment_amount,
                pp.notes,
                t.total_amount,
                t.remaining_amount
            FROM partial_payments pp
            JOIN transactions t ON pp.transaction_id = t.id
            JOIN apnaar_parties ap ON t.apnaar_party_id = ap.id
            JOIN lenaar_parties lp ON t.lenaar_party_id = lp.id
            WHERE 1=1
            '''
            
            params = []
            
            if search_apnaar:
                search_query += " AND ap.name LIKE ?"
                params.append(f"%{search_apnaar}%")
            
            if search_lenaar:
                search_query += " AND lp.name LIKE ?"
                params.append(f"%{search_lenaar}%")
            
            search_query += " AND pp.payment_date BETWEEN ? AND ?"
            params.extend([start_search_date.strftime("%Y-%m-%d"), end_search_date.strftime("%Y-%m-%d")])
            
            search_query += " ORDER BY pp.payment_date DESC"
            
            try:
                db.cursor.execute(search_query, params)
                columns = [column[0] for column in db.cursor.description]
                search_results = []
                for row in db.cursor.fetchall():
                    search_results.append(dict(zip(columns, row)))
                
                if search_results:
                    # Convert to DataFrame for display
                    df = pd.DataFrame(search_results)
                    
                    # Format columns for display
                    display_df = df[[
                        'payment_id', 'transaction_id', 'apnaar_party_name', 
                        'lenaar_party_name', 'payment_date', 'payment_amount', 
                        'total_amount', 'remaining_amount', 'notes'
                    ]].copy()
                    
                    # Rename columns for better display
                    display_df.columns = [
                        'Payment ID', 'Transaction ID', 'Apnaar Party', 
                        'Lenaar Party', 'Payment Date', 'Payment Amount (₹)', 
                        'Total Amount (₹)', 'Remaining Amount (₹)', 'Notes'
                    ]
                    
                    # Format numeric and date columns
                    display_df['Payment Amount (₹)'] = display_df['Payment Amount (₹)'].apply(lambda x: format_currency(x))
                    display_df['Total Amount (₹)'] = display_df['Total Amount (₹)'].apply(lambda x: format_currency(x))
                    display_df['Remaining Amount (₹)'] = display_df['Remaining Amount (₹)'].apply(lambda x: format_currency(x))
                    display_df['Payment Date'] = display_df['Payment Date'].apply(format_date)
                    
                    # Display the dataframe
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Summary metrics
                    total_payments = len(search_results)
                    total_amount_paid = sum(p['payment_amount'] for p in search_results)
                    
                    st.metric("Total Payments", total_payments)
                    st.metric("Total Amount Paid", format_currency(total_amount_paid))
                else:
                    st.info("No payments found matching your search criteria.")
            except Exception as e:
                st.error(f"Error searching payments: {e}")

# Reports Page
elif page == "Reports":
    styled_header("Reports")
    
    # Create tabs for different report types
    tab1, tab2, tab3, tab4 = st.tabs(["Summary Reports", "Dalali Reports", "Import/Export", "Web Data"])
    
    with tab1:
        st.subheader("Transaction Summary")
        
        # Get transaction data
        transactions = db.get_transactions()
        
    # Web Data tab for web scraping
    with tab4:
        st.subheader("Get Data from Websites")
        
        # Create a form for the URL input
        with st.form(key="web_scrape_form"):
            url = st.text_input(
                "Enter Website URL", 
                placeholder="https://example.com/financial-data"
            )
            
            # Provide options for data types to look for
            data_type = st.selectbox(
                "What kind of data are you looking for?",
                ["Financial transactions", "Dalali rates", "Interest rates", "General financial data"]
            )
            
            submit_button = st.form_submit_button("Scrape Website Data")
        
        # Process the form when submitted
        if submit_button:
            if not url:
                st.error("Please enter a valid URL")
            else:
                with st.spinner("Extracting data from website..."):
                    # Call the web scraping function
                    transactions, message = scrape_website_data(url)
                    
                    if transactions:
                        st.success(message)
                        
                        # Display the extracted data
                        st.write(f"##### Found {len(transactions)} potential transaction entries")
                        
                        # Create a dataframe from the extracted data
                        df = pd.DataFrame(transactions)
                        st.dataframe(df, use_container_width=True)
                        
                        # Option to export the scraped data
                        if st.button("Export Scraped Data to Excel"):
                            try:
                                filename = export_data(df, "excel", "scraped_data")
                                st.success(f"Data exported to {filename}")
                                # Provide download link
                                with open(filename, "rb") as file:
                                    st.download_button(
                                        label="Download Excel File",
                                        data=file,
                                        file_name=os.path.basename(filename),
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                            except Exception as e:
                                st.error(f"Error exporting data: {e}")
                    else:
                        st.error(message)
        
        # Add instructions and examples
        with st.expander("How to use this feature"):
            st.write("""
            ### Web Data Scraping
            
            This feature allows you to extract financial transaction data from websites. Here's how to use it:
            
            1. Enter the URL of the website containing financial transaction data
            2. Select the type of data you're looking for
            3. Click 'Scrape Website Data' to extract the information
            4. Review the extracted data
            5. Export to Excel if needed
            
            #### Notes:
            - Not all websites allow data scraping, and some may block automated access
            - The quality of extracted data depends on the structure of the website
            - This feature works best with simple, structured financial data tables
            - For complex websites, you may need to manually select and copy the data
            
            #### Example URLs:
            - Bank statement pages (when logged in)
            - Online accounting services with transaction tables
            - Financial report websites
            """)
            
        # Add a section for data cleaning and preprocessing
        with st.expander("Data Cleaning Options"):
            st.write("""
            ### Clean and Process Scraped Data
            
            If you've already scraped data, you can use these options to clean and process it:
            
            - Remove duplicate entries
            - Extract numeric values from text
            - Identify transaction types
            - Format dates consistently
            
            **Note:** These features will be available after you've successfully scraped data from a website.
            """)
            
            # Placeholder for future functionality
            st.info("Advanced data cleaning features coming soon!")
    
    if not transactions:
        st.info("No transactions found. Add transactions to generate reports.")
    else:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(transactions)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Transactions", len(df))
            st.metric("Total Amount", format_currency(df['total_amount'].sum()))
        
        with col2:
            st.metric("Total Interest", format_currency(df['interest_amount'].sum()))
            st.metric("Total Dalali", format_currency(df['dalali_amount'].sum()))
        
        with col3:
            st.metric("Net Interest Received", format_currency(df['interest_received_by_apnar'].sum()))
            received_count = (df['received'] == 1).sum()
            pending_count = (df['received'] == 0).sum()
            st.metric("Received/Pending", f"{received_count}/{pending_count}")
        
        # Party-wise summary
        st.subheader("Party-wise Summary")
        
        tab1, tab2 = st.tabs(["Apnaar Parties", "Lenaar Parties"])
        
        with tab1:
            # Apnaar party summary
            apnaar_summary = df.groupby('apnaar_party_name').agg({
                'total_amount': 'sum',
                'interest_amount': 'sum',
                'dalali_amount': 'sum',
                'interest_received_by_apnar': 'sum',
                'id': 'count'
            }).reset_index()
            
            apnaar_summary.columns = [
                'Party Name', 'Total Amount (₹)', 'Interest Amount (₹)',
                'Dalali Amount (₹)', 'Net Interest (₹)', 'Transaction Count'
            ]
            
            # Format currency columns
            for col in ['Total Amount (₹)', 'Interest Amount (₹)', 'Dalali Amount (₹)', 'Net Interest (₹)']:
                apnaar_summary[col] = apnaar_summary[col].apply(lambda x: format_currency(x))
            
            st.dataframe(apnaar_summary, use_container_width=True)
        
        with tab2:
            # Lenaar party summary
            lenaar_summary = df.groupby('lenaar_party_name').agg({
                'total_amount': 'sum',
                'interest_amount': 'sum',
                'lenaar_return_amount': 'sum',
                'id': 'count'
            }).reset_index()
            
            lenaar_summary.columns = [
                'Party Name', 'Total Amount (₹)', 'Interest Amount (₹)',
                'Return Amount (₹)', 'Transaction Count'
            ]
            
            # Format currency columns
            for col in ['Total Amount (₹)', 'Interest Amount (₹)', 'Return Amount (₹)']:
                lenaar_summary[col] = lenaar_summary[col].apply(lambda x: format_currency(x))
            
            st.dataframe(lenaar_summary, use_container_width=True)
        
        # Monthly analysis
        st.subheader("Monthly Analysis")
        
        # Add month and year columns to dataframe
        df['month'] = pd.to_datetime(df['start_date']).dt.month
        df['year'] = pd.to_datetime(df['start_date']).dt.year
        df['month_year'] = pd.to_datetime(df['start_date']).dt.strftime('%b %Y')
        
        monthly_data = df.groupby(['year', 'month', 'month_year']).agg({
            'total_amount': 'sum',
            'interest_amount': 'sum',
            'dalali_amount': 'sum',
            'interest_received_by_apnar': 'sum',
            'id': 'count'
        }).reset_index().sort_values(['year', 'month'])
        
        # Create a chart using Streamlit
        st.bar_chart(
            data=monthly_data.set_index('month_year')['total_amount'],
            use_container_width=True
        )
        
        # Display monthly data in a table
        monthly_data = monthly_data[['month_year', 'total_amount', 'interest_amount', 'dalali_amount', 'interest_received_by_apnar', 'id']]
        monthly_data.columns = ['Month/Year', 'Total Amount (₹)', 'Interest Amount (₹)', 'Dalali Amount (₹)', 'Net Interest (₹)', 'Transaction Count']
        
        # Format currency columns
        for col in ['Total Amount (₹)', 'Interest Amount (₹)', 'Dalali Amount (₹)', 'Net Interest (₹)']:
            monthly_data[col] = monthly_data[col].apply(lambda x: format_currency(x))
        
        st.dataframe(monthly_data, use_container_width=True)
        
        # Export options
        st.subheader("Export Reports")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("Export All Transactions"):
                export_format = st.radio(
                    "Export Format",
                    ["CSV", "Excel"],
                    horizontal=True,
                    key="export_all_format"
                )
                
                if st.button(f"Export as {export_format}", key="export_all_button"):
                    filename = export_data(
                        df, 
                        export_format.lower(), 
                        "all_transactions"
                    )
                    if filename:
                        st.success(f"Data exported to {filename}")
                    else:
                        st.error("Failed to export data")
        
        with export_col2:
            if st.button("Export Monthly Summary"):
                export_format = st.radio(
                    "Export Format",
                    ["CSV", "Excel"],
                    horizontal=True,
                    key="export_monthly_format"
                )
                
                if st.button(f"Export as {export_format}", key="export_monthly_button"):
                    filename = export_data(
                        monthly_data, 
                        export_format.lower(), 
                        "monthly_summary"
                    )
                    if filename:
                        st.success(f"Data exported to {filename}")
                    else:
                        st.error("Failed to export data")

# Settings Page
elif page == "Settings":
    styled_header("Settings")
    
    # Database backup and restore
    st.subheader("Database Management")
    
    tab1, tab2 = st.tabs(["Backup", "Restore"])
    
    with tab1:
        st.write("Create a backup of your database to protect your data.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            backup_name = st.text_input("Backup Name (Optional)", 
                placeholder="Leave empty for automatic timestamp")
            
            if st.button("Create Backup", key="create_backup"):
                with st.spinner("Creating backup..."):
                    # Close the database connection before backup
                    db.close()
                    
                    # Create backup
                    backup_file = backup_database()
                    
                    # Reconnect to the database
                    db.connect()
                    
                    if backup_file:
                        st.success(f"Backup created successfully: {os.path.basename(backup_file)}")
                    else:
                        st.error("Failed to create backup.")
        
        with col2:
            st.write("Existing backups:")
            backups = get_available_backups()
            
            if backups:
                backup_df = pd.DataFrame({
                    "Date": [b["formatted_date"] for b in backups],
                    "Filename": [b["filename"] for b in backups]
                })
                
                st.dataframe(backup_df, use_container_width=True)
            else:
                st.info("No backups found. Create your first backup to protect your data.")
    
    with tab2:
        st.write("Restore your database from a previous backup.")
        st.warning("⚠️ Restoring will replace your current data with the backup data. This cannot be undone!")
        
        backups = get_available_backups()
        
        if backups:
            selected_backup = st.selectbox(
                "Select a backup to restore",
                options=range(len(backups)),
                format_func=lambda i: f"{backups[i]['formatted_date']} - {backups[i]['filename']}"
            )
            
            if st.button("Restore Selected Backup", key="restore_backup"):
                with st.spinner("Restoring database..."):
                    # Ask for confirmation
                    if st.checkbox("I understand this will replace my current data", key="confirm_restore"):
                        # Close the database connection before restore
                        db.close()
                        
                        # Restore from backup
                        success = restore_database(backups[selected_backup]["path"])
                        
                        # Reconnect to the database
                        db.connect()
                        
                        if success:
                            st.success("Database restored successfully!")
                            st.info("The application will now reload with the restored data.")
                            
                            # Trigger a rerun to reload the application with the restored data
                            st.rerun()
                        else:
                            st.error("Failed to restore database.")
                    else:
                        st.error("Please confirm that you understand the implications of restoring a backup.")
        else:
            st.info("No backups found. Create a backup first before attempting to restore.")
    
    # Application information
    st.subheader("About HISAABSETU")
    
    st.info("""
    HISAABSETU Portable Accounting Software
    
    Version: 1.0.0
    
    This application allows you to manage financial transactions between parties,
    with automatic calculation of interest and dalali (brokerage).
    
    Features:
    - Party management (Apnaar, Lenaar, Kapine Lenaar)
    - Transaction tracking
    - Interest and dalali calculations
    - Reports and analysis
    - Data export
    
    All data is stored locally on the pendrive.
    """)
    
    # Instructions
    st.subheader("How to Use")
    
    st.markdown("""
    ### Getting Started
    
    1. **Add Parties**: Go to the "Manage Parties" page to add Apnaar and Lenaar parties.
    2. **Create Transactions**: Go to the "Transactions" page to add new transactions.
    3. **View Reports**: Go to the "Reports" page to see summary statistics and export data.
    
    ### Backup and Portability
    
    - The application stores all data in the `data/` directory.
    - Use the backup feature to create regular backups of your database.
    - To move the application to another computer, simply copy the entire application folder.
    
    ### Calculations
    
    - **Interest Amount**: Principal * Rate * (12/year type) * days
    - **Dalali Amount**: Principal * Rate * (12/year type) * days
    - **Lenaar Return Amount**: Principal + Interest
    - **Apnaar Received Amount**: Principal + Interest - Dalali
    - **Interest Received by Apnaar**: Interest - Dalali
    """)

# Close the database connection when the app is done
# (In a real Streamlit app, this isn't strictly necessary as the connection will be reopened on next run)
db.close()
