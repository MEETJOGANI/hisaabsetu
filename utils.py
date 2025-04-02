import os
import pandas as pd
from datetime import datetime
import streamlit as st
import shutil
import zipfile
import json

def format_currency(amount):
    """Format a number as Indian Rupees currency without decimal places"""
    if amount is None:
        return "₹0"
    
    # Convert to string with no decimal places
    amount_str = f"₹{int(float(amount)):,}"
    
    return amount_str

def parse_date(date_str):
    """Parse a date string to datetime object"""
    try:
        # Try different formats
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Date {date_str} doesn't match any expected format")
    except Exception as e:
        st.error(f"Error parsing date: {e}")
        return None

def format_date(date_obj):
    """Format a date object to string in DD/MM/YYYY format"""
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
    
    if date_obj:
        return date_obj.strftime("%d/%m/%Y")
    return ""

def export_data(data, file_format, filename_prefix):
    """Export data to CSV or Excel format"""
    if not data:
        st.error("No data to export")
        return None
    
    # Create exports directory if it doesn't exist
    export_dir = "data/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create full filename
    filename = f"{export_dir}/{filename_prefix}_{timestamp}.{file_format}"
    
    try:
        # Convert to DataFrame if it's not already
        if not isinstance(data, pd.DataFrame):
            df = pd.DataFrame(data)
        else:
            df = data
        
        # Export based on format
        if file_format.lower() == "csv":
            df.to_csv(filename, index=False)
        elif file_format.lower() == "excel" or file_format.lower() == "xlsx":
            df.to_excel(filename, index=False)
        else:
            st.error(f"Unsupported file format: {file_format}")
            return None
        
        return filename
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return None

def validate_numeric_input(value, field_name, min_value=None, max_value=None):
    """Validate numeric input"""
    try:
        # Convert to float
        num_value = float(value)
        
        # Check minimum value if specified
        if min_value is not None and num_value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        
        # Check maximum value if specified
        if max_value is not None and num_value > max_value:
            return False, f"{field_name} must be at most {max_value}"
        
        return True, num_value
    except ValueError:
        return False, f"{field_name} must be a valid number"

def validate_transaction_input(data):
    """Validate all transaction input fields"""
    errors = []
    
    # Check if required party fields are selected
    if not data.get('apnaar_party_id'):
        errors.append("Apnaar Party must be selected")
    
    if not data.get('lenaar_party_id'):
        errors.append("Lenaar Party must be selected")
    
    # Validate total amount
    total_amount = data.get('total_amount')
    if not total_amount:
        errors.append("Total Amount is required")
    else:
        valid, result = validate_numeric_input(total_amount, "Total Amount", 0)
        if not valid:
            errors.append(result)
    
    # Validate interest rate
    interest_rate = data.get('interest_rate')
    if not interest_rate:
        errors.append("Interest Rate is required")
    else:
        valid, result = validate_numeric_input(interest_rate, "Interest Rate", 0)
        if not valid:
            errors.append(result)
    
    # Validate dalali rate
    dalali_rate = data.get('dalali_rate')
    if dalali_rate is not None:  # Allow zero
        valid, result = validate_numeric_input(dalali_rate, "Dalali Rate", 0)
        if not valid:
            errors.append(result)
    
    # Validate dates
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date:
        errors.append("Start Date is required")
    
    if not end_date:
        errors.append("End Date is required")
    
    if start_date and end_date and start_date > end_date:
        errors.append("End Date must be after Start Date")
    
    return errors

def backup_database(db_path="data/hisaabsetu.db", backup_dir="data/backups"):
    """Create a backup of the database file"""
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{backup_dir}/hisaabsetu_backup_{timestamp}.zip"
        
        # Create a zip file
        with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the database file to the zip
            zipf.write(db_path, os.path.basename(db_path))
            
            # Add backup metadata
            metadata = {
                "backup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "original_path": db_path,
                "backup_type": "manual"
            }
            
            # Write metadata to a file in the zip
            zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=4))
        
        return backup_filename
    except Exception as e:
        st.error(f"Error creating backup: {e}")
        return None

def restore_database(backup_file, db_path="data/hisaabsetu.db"):
    """Restore database from a backup file"""
    try:
        # Create a temporary directory for extraction
        temp_dir = "data/temp_restore"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extract the backup file
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Get the database file from the backup
        db_filename = os.path.basename(db_path)
        extracted_db_path = os.path.join(temp_dir, db_filename)
        
        # Check if the extracted database file exists
        if not os.path.exists(extracted_db_path):
            st.error("Backup file does not contain a valid database.")
            return False
        
        # Create a backup of the current database before restoring
        current_backup = backup_database(db_path, "data/auto_backups")
        
        # Copy the extracted database to the original location
        shutil.copy2(extracted_db_path, db_path)
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        st.error(f"Error restoring database: {e}")
        return False

def get_available_backups(backup_dir="data/backups"):
    """Get a list of available backup files"""
    if not os.path.exists(backup_dir):
        return []
    
    # List all backup files
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith("hisaabsetu_backup_") and file.endswith(".zip"):
            # Extract timestamp from filename
            try:
                timestamp = file.replace("hisaabsetu_backup_", "").replace(".zip", "")
                date_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                formatted_date = date_obj.strftime("%d/%m/%Y %H:%M:%S")
                
                backups.append({
                    "filename": file,
                    "path": os.path.join(backup_dir, file),
                    "timestamp": timestamp,
                    "formatted_date": formatted_date
                })
            except ValueError:
                # Skip files with invalid timestamp format
                continue
    
    # Sort backups by timestamp (newest first)
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return backups

def scrape_website_data(url):
    """
    Scrape transaction data from a website
    
    Args:
        url (str): URL of the website to scrape
        
    Returns:
        list: List of transactions extracted from the website
        or None if scraping fails
    """
    try:
        import trafilatura
        
        # Fetch and extract the text content from the URL
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            return None, "Failed to download content from the URL"
        
        text_content = trafilatura.extract(downloaded)
        
        if not text_content:
            return None, "No content could be extracted from the website"
        
        # Parse the extracted content for transaction data
        # This is a simple example and may need customization based on the structure of the website
        transactions = []
        
        # Split the content by lines
        lines = text_content.strip().split('\n')
        
        # Process the lines to extract transaction data
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Look for lines that might contain transaction data
            if "₹" in line or "Rs." in line:
                # This is a very simple heuristic; you may need a more sophisticated parser
                # based on the structure of the websites you're targeting
                transactions.append({
                    "raw_text": line,
                    "extracted_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return transactions, "Successfully extracted data from the website"
    except ImportError:
        return None, "Required libraries are not installed. Please install trafilatura."
    except Exception as e:
        return None, f"Error scraping website: {str(e)}"
