import os
import sqlite3
import pandas as pd
from datetime import datetime

class Database:
    def __init__(self, db_path="data/hisaabsetu.db"):
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Establish a connection to the SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            
    def create_tables(self):
        """Create the necessary tables if they don't exist"""
        try:
            # Apnaar Parties Table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS apnaar_parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact TEXT,
                address TEXT,
                boss_name TEXT,
                boss_phone TEXT,
                accountant_name TEXT,
                accountant_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Lenaar Parties Table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lenaar_parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact TEXT,
                address TEXT,
                boss_name TEXT,
                boss_phone TEXT,
                accountant_name TEXT,
                accountant_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Kapine Lenaar Parties Table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kapine_lenaar_parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact TEXT,
                address TEXT,
                boss_name TEXT,
                boss_phone TEXT,
                accountant_name TEXT,
                accountant_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Transactions Table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apnaar_party_id INTEGER NOT NULL,
                lenaar_party_id INTEGER NOT NULL,
                kapine_lenaar_party_id INTEGER,
                total_amount REAL NOT NULL,
                condition TEXT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                number_of_days INTEGER NOT NULL,
                number_of_months REAL NOT NULL,
                interest_rate REAL NOT NULL,
                dalali_rate REAL NOT NULL,
                interest_amount REAL NOT NULL,
                dalali_amount REAL NOT NULL,
                lenaar_return_amount REAL NOT NULL,
                apnaar_received_amount REAL NOT NULL,
                interest_received_by_apnar REAL NOT NULL,
                remaining_amount REAL,
                received BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (apnaar_party_id) REFERENCES apnaar_parties (id),
                FOREIGN KEY (lenaar_party_id) REFERENCES lenaar_parties (id),
                FOREIGN KEY (kapine_lenaar_party_id) REFERENCES kapine_lenaar_parties (id)
            )
            ''')
            
            # Partial Payments Table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS partial_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                payment_date DATE NOT NULL,
                payment_amount REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE
            )
            ''')
            
            # Remaining Balance Calculations Table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS remaining_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                calculation_date DATE NOT NULL,
                remaining_amount REAL NOT NULL,
                interest_amount REAL NOT NULL,
                dalali_amount REAL NOT NULL,
                days_since_last_payment INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE
            )
            ''')
            
            # Check if remaining_amount column exists in transactions table, add it if not
            self.cursor.execute("PRAGMA table_info(transactions)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'remaining_amount' not in columns:
                try:
                    print("Adding remaining_amount column to transactions table")
                    self.cursor.execute('''
                    ALTER TABLE transactions ADD COLUMN remaining_amount REAL
                    ''')
                    
                    # Initialize remaining_amount with total_amount for existing records
                    self.cursor.execute('''
                    UPDATE transactions SET remaining_amount = total_amount
                    ''')
                    
                    self.connection.commit()
                except Exception as e:
                    print(f"Error adding remaining_amount column: {e}")
            
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Table creation error: {e}")
            
    def add_apnaar_party(self, name, contact="", address="", boss_name="", boss_phone="", accountant_name="", accountant_phone=""):
        """Add a new Apnaar Party to the database with extended contact information"""
        try:
            self.cursor.execute(
                """INSERT INTO apnaar_parties 
                   (name, contact, address, boss_name, boss_phone, accountant_name, accountant_phone) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, contact, address, boss_name, boss_phone, accountant_name, accountant_phone)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error adding Apnaar Party: {e}")
            return False
            
    def add_lenaar_party(self, name, contact="", address=""):
        """Add a new Lenaar Party to the database"""
        try:
            self.cursor.execute(
                "INSERT INTO lenaar_parties (name, contact, address) VALUES (?, ?, ?)",
                (name, contact, address)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error adding Lenaar Party: {e}")
            return False
            
    def add_kapine_lenaar_party(self, name, contact="", address=""):
        """Add a new Kapine Lenaar Party to the database"""
        try:
            self.cursor.execute(
                "INSERT INTO kapine_lenaar_parties (name, contact, address) VALUES (?, ?, ?)",
                (name, contact, address)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error adding Kapine Lenaar Party: {e}")
            return False
    
    def get_all_apnaar_parties(self):
        """Get all Apnaar Parties from the database"""
        try:
            self.cursor.execute("SELECT id, name FROM apnaar_parties ORDER BY name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting Apnaar Parties: {e}")
            return []
            
    def get_all_lenaar_parties(self):
        """Get all Lenaar Parties from the database"""
        try:
            self.cursor.execute("SELECT id, name FROM lenaar_parties ORDER BY name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting Lenaar Parties: {e}")
            return []
            
    def get_all_kapine_lenaar_parties(self):
        """Get all Kapine Lenaar Parties from the database"""
        try:
            self.cursor.execute("SELECT id, name FROM kapine_lenaar_parties ORDER BY name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting Kapine Lenaar Parties: {e}")
            return []
    
    def add_transaction(self, transaction_data):
        """Add a new transaction to the database"""
        try:
            self.cursor.execute('''
            INSERT INTO transactions (
                apnaar_party_id, lenaar_party_id, kapine_lenaar_party_id, 
                total_amount, condition, start_date, end_date, number_of_days, 
                number_of_months, interest_rate, dalali_rate, interest_amount, 
                dalali_amount, lenaar_return_amount, apnaar_received_amount, 
                interest_received_by_apnar, remaining_amount, received
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_data['apnaar_party_id'],
                transaction_data['lenaar_party_id'],
                transaction_data['kapine_lenaar_party_id'],
                transaction_data['total_amount'],
                transaction_data['condition'],
                transaction_data['start_date'],
                transaction_data['end_date'],
                transaction_data['number_of_days'],
                transaction_data['number_of_months'],
                transaction_data['interest_rate'],
                transaction_data['dalali_rate'],
                transaction_data['interest_amount'],
                transaction_data['dalali_amount'],
                transaction_data['lenaar_return_amount'],
                transaction_data['apnaar_received_amount'],
                transaction_data['interest_received_by_apnar'],
                transaction_data['total_amount'],  # Set remaining_amount to total_amount initially
                0  # Initially not received
            ))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding transaction: {e}")
            return None
    
    def update_transaction(self, transaction_id, transaction_data):
        """Update an existing transaction"""
        try:
            # If this is an update without changing the total amount (editing other details)
            # we should get the old transaction to check if remaining_amount needs updating
            existing_remaining = None
            if 'remaining_amount' not in transaction_data:
                existing_transaction = self.get_transaction_by_id(transaction_id)
                if existing_transaction:
                    # If total amount didn't change, keep remaining amount
                    if existing_transaction['total_amount'] == transaction_data['total_amount']:
                        existing_remaining = existing_transaction.get('remaining_amount')
                    # Otherwise, set to new total (full amount)
                    else:
                        existing_remaining = transaction_data['total_amount']
            
            self.cursor.execute('''
            UPDATE transactions SET
                apnaar_party_id = ?, lenaar_party_id = ?, kapine_lenaar_party_id = ?,
                total_amount = ?, condition = ?, start_date = ?, end_date = ?, 
                number_of_days = ?, number_of_months = ?, interest_rate = ?, 
                dalali_rate = ?, interest_amount = ?, dalali_amount = ?,
                lenaar_return_amount = ?, apnaar_received_amount = ?, 
                interest_received_by_apnar = ?, remaining_amount = ?
            WHERE id = ?
            ''', (
                transaction_data['apnaar_party_id'],
                transaction_data['lenaar_party_id'],
                transaction_data['kapine_lenaar_party_id'],
                transaction_data['total_amount'],
                transaction_data['condition'],
                transaction_data['start_date'],
                transaction_data['end_date'],
                transaction_data['number_of_days'],
                transaction_data['number_of_months'],
                transaction_data['interest_rate'],
                transaction_data['dalali_rate'],
                transaction_data['interest_amount'],
                transaction_data['dalali_amount'],
                transaction_data['lenaar_return_amount'],
                transaction_data['apnaar_received_amount'],
                transaction_data['interest_received_by_apnar'],
                transaction_data.get('remaining_amount', existing_remaining),
                transaction_id
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating transaction: {e}")
            return False
    
    def update_transaction_received_status(self, transaction_id, received):
        """Update the received status of a transaction"""
        try:
            self.cursor.execute(
                "UPDATE transactions SET received = ? WHERE id = ?",
                (1 if received else 0, transaction_id)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating transaction received status: {e}")
            return False
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction from the database"""
        try:
            self.cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting transaction: {e}")
            return False
            
    def delete_apnaar_party(self, party_id):
        """Delete an Apnaar Party from the database"""
        try:
            # Check if party is used in any transactions
            self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE apnaar_party_id = ?", (party_id,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                return False, f"Cannot delete party - it's used in {count} transactions"
            
            # Delete the party
            self.cursor.execute("DELETE FROM apnaar_parties WHERE id = ?", (party_id,))
            self.connection.commit()
            return True, "Party deleted successfully"
        except sqlite3.Error as e:
            print(f"Error deleting Apnaar Party: {e}")
            return False, f"Database error: {e}"
            
    def delete_lenaar_party(self, party_id):
        """Delete a Lenaar Party from the database"""
        try:
            # Check if party is used in any transactions
            self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE lenaar_party_id = ?", (party_id,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                return False, f"Cannot delete party - it's used in {count} transactions"
            
            # Delete the party
            self.cursor.execute("DELETE FROM lenaar_parties WHERE id = ?", (party_id,))
            self.connection.commit()
            return True, "Party deleted successfully"
        except sqlite3.Error as e:
            print(f"Error deleting Lenaar Party: {e}")
            return False, f"Database error: {e}"
            
    def delete_kapine_lenaar_party(self, party_id):
        """Delete a Kapine Lenaar Party from the database"""
        try:
            # Check if party is used in any transactions
            self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE kapine_lenaar_party_id = ?", (party_id,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                return False, f"Cannot delete party - it's used in {count} transactions"
            
            # Delete the party
            self.cursor.execute("DELETE FROM kapine_lenaar_parties WHERE id = ?", (party_id,))
            self.connection.commit()
            return True, "Party deleted successfully"
        except sqlite3.Error as e:
            print(f"Error deleting Kapine Lenaar Party: {e}")
            return False, f"Database error: {e}"
    
    def get_transactions_ending_today(self):
        """Get all transactions ending today"""
        try:
            today = datetime.now().date()
            query = '''
            SELECT 
                t.id, ap.name as apnaar_party_name, lp.name as lenaar_party_name, 
                klp.name as kapine_lenaar_party_name, t.total_amount, t.condition,
                t.start_date, t.end_date, t.number_of_days, t.number_of_months,
                t.interest_rate, t.dalali_rate, t.interest_amount, t.dalali_amount,
                t.lenaar_return_amount, t.apnaar_received_amount, t.interest_received_by_apnar,
                t.remaining_amount, t.received, t.created_at
            FROM transactions t
            JOIN apnaar_parties ap ON t.apnaar_party_id = ap.id
            JOIN lenaar_parties lp ON t.lenaar_party_id = lp.id
            LEFT JOIN kapine_lenaar_parties klp ON t.kapine_lenaar_party_id = klp.id
            WHERE date(t.end_date) = date(?)
            ORDER BY t.created_at DESC
            '''
            
            self.cursor.execute(query, (today.strftime("%Y-%m-%d"),))
            columns = [column[0] for column in self.cursor.description]
            result = []
            for row in self.cursor.fetchall():
                result.append(dict(zip(columns, row)))
            
            return result
        except sqlite3.Error as e:
            print(f"Error getting transactions ending today: {e}")
            return []
            
    def get_transactions(self, filters=None):
        """
        Get all transactions with optional filtering
        filters: dictionary with column names as keys and filter values as values
        """
        try:
            query = '''
            SELECT 
                t.id, ap.name as apnaar_party_name, lp.name as lenaar_party_name, 
                klp.name as kapine_lenaar_party_name, t.total_amount, t.condition,
                t.start_date, t.end_date, t.number_of_days, t.number_of_months,
                t.interest_rate, t.dalali_rate, t.interest_amount, t.dalali_amount,
                t.lenaar_return_amount, t.apnaar_received_amount, t.interest_received_by_apnar,
                t.remaining_amount, t.received, t.created_at
            FROM transactions t
            JOIN apnaar_parties ap ON t.apnaar_party_id = ap.id
            JOIN lenaar_parties lp ON t.lenaar_party_id = lp.id
            LEFT JOIN kapine_lenaar_parties klp ON t.kapine_lenaar_party_id = klp.id
            '''
            
            params = []
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    if key == 'apnaar_party_name':
                        where_clauses.append("ap.name LIKE ?")
                        params.append(f"%{value}%")
                    elif key == 'lenaar_party_name':
                        where_clauses.append("lp.name LIKE ?")
                        params.append(f"%{value}%")
                    elif key == 'kapine_lenaar_party_name':
                        where_clauses.append("klp.name LIKE ?")
                        params.append(f"%{value}%")
                    elif key == 'received':
                        where_clauses.append("t.received = ?")
                        params.append(1 if value else 0)
                    elif key == 'date_range':
                        start, end = value
                        where_clauses.append("(t.start_date BETWEEN ? AND ? OR t.end_date BETWEEN ? AND ?)")
                        params.extend([start, end, start, end])
                    elif key == 'end_date_month_year':
                        month_num, year_num = value
                        
                        if month_num is not None and year_num is not None:
                            # Filter by both month and year
                            where_clauses.append("(strftime('%m', t.end_date) = ? AND strftime('%Y', t.end_date) = ?)")
                            params.extend([f"{month_num:02d}", str(year_num)])
                        elif month_num is not None:
                            # Filter by month only
                            where_clauses.append("strftime('%m', t.end_date) = ?")
                            params.append(f"{month_num:02d}")
                        elif year_num is not None:
                            # Filter by year only
                            where_clauses.append("strftime('%Y', t.end_date) = ?")
                            params.append(str(year_num))
                    elif key == 'min_amount':
                        where_clauses.append("t.total_amount >= ?")
                        params.append(value)
                    elif key == 'max_amount':
                        where_clauses.append("t.total_amount <= ?")
                        params.append(value)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            query += " ORDER BY t.created_at DESC"
            
            self.cursor.execute(query, params)
            columns = [column[0] for column in self.cursor.description]
            result = []
            for row in self.cursor.fetchall():
                result.append(dict(zip(columns, row)))
            
            return result
        except sqlite3.Error as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def get_transaction_by_id(self, transaction_id):
        """Get a specific transaction by ID"""
        try:
            query = '''
            SELECT 
                t.id, t.apnaar_party_id, t.lenaar_party_id, t.kapine_lenaar_party_id,
                ap.name as apnaar_party_name, lp.name as lenaar_party_name, 
                klp.name as kapine_lenaar_party_name, t.total_amount, t.condition,
                t.start_date, t.end_date, t.number_of_days, t.number_of_months,
                t.interest_rate, t.dalali_rate, t.interest_amount, t.dalali_amount,
                t.lenaar_return_amount, t.apnaar_received_amount, t.interest_received_by_apnar,
                t.remaining_amount, t.received, t.created_at
            FROM transactions t
            JOIN apnaar_parties ap ON t.apnaar_party_id = ap.id
            JOIN lenaar_parties lp ON t.lenaar_party_id = lp.id
            LEFT JOIN kapine_lenaar_parties klp ON t.kapine_lenaar_party_id = klp.id
            WHERE t.id = ?
            '''
            
            self.cursor.execute(query, (transaction_id,))
            columns = [column[0] for column in self.cursor.description]
            row = self.cursor.fetchone()
            
            if row:
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            print(f"Error getting transaction by ID: {e}")
            return None
    
    def export_transactions_to_csv(self, filename):
        """Export all transactions to a CSV file"""
        try:
            transactions = self.get_transactions()
            if transactions:
                df = pd.DataFrame(transactions)
                df.to_csv(filename, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error exporting transactions to CSV: {e}")
            return False
    
    def export_transactions_to_excel(self, filename):
        """Export all transactions to an Excel file"""
        try:
            transactions = self.get_transactions()
            if transactions:
                df = pd.DataFrame(transactions)
                df.to_excel(filename, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error exporting transactions to Excel: {e}")
            return False
            
    def add_partial_payment(self, transaction_id, payment_date, payment_amount, notes=""):
        """
        Add a partial payment for a transaction
        This will also update the transaction's remaining_amount
        """
        try:
            # First, get the current remaining amount
            transaction = self.get_transaction_by_id(transaction_id)
            if not transaction:
                return False, "Transaction not found"
                
            current_remaining = transaction.get('remaining_amount', transaction['total_amount'])
            
            # Make sure the payment amount is not more than the remaining amount
            if payment_amount > current_remaining:
                return False, "Payment amount exceeds remaining balance"
                
            # Calculate new remaining amount
            new_remaining = current_remaining - payment_amount
            
            # Update the transaction's remaining amount
            self.cursor.execute(
                "UPDATE transactions SET remaining_amount = ? WHERE id = ?",
                (new_remaining, transaction_id)
            )
                
            # Add the partial payment record
            self.cursor.execute(
                "INSERT INTO partial_payments (transaction_id, payment_date, payment_amount, notes) VALUES (?, ?, ?, ?)",
                (transaction_id, payment_date, payment_amount, notes)
            )
            
            # If remaining amount is 0, mark transaction as received
            if new_remaining == 0:
                self.cursor.execute(
                    "UPDATE transactions SET received = 1 WHERE id = ?",
                    (transaction_id,)
                )
                
            self.connection.commit()
            return True, "Payment added successfully"
            
        except sqlite3.Error as e:
            print(f"Error adding partial payment: {e}")
            return False, f"Database error: {e}"
    
    def get_partial_payments(self, transaction_id):
        """Get all partial payments for a transaction"""
        try:
            query = '''
            SELECT 
                id, transaction_id, payment_date, payment_amount, notes, created_at
            FROM partial_payments
            WHERE transaction_id = ?
            ORDER BY payment_date DESC
            '''
            
            self.cursor.execute(query, (transaction_id,))
            columns = [column[0] for column in self.cursor.description]
            result = []
            for row in self.cursor.fetchall():
                result.append(dict(zip(columns, row)))
            
            return result
        except sqlite3.Error as e:
            print(f"Error getting partial payments: {e}")
            return []
    
    def delete_partial_payment(self, payment_id):
        """Delete a partial payment and update the transaction's remaining amount"""
        try:
            # First, get the payment and transaction info
            self.cursor.execute(
                "SELECT transaction_id, payment_amount FROM partial_payments WHERE id = ?",
                (payment_id,)
            )
            payment = self.cursor.fetchone()
            if not payment:
                return False, "Payment not found"
                
            transaction_id, payment_amount = payment
            
            # Get the transaction's current remaining amount
            transaction = self.get_transaction_by_id(transaction_id)
            if not transaction:
                return False, "Transaction not found"
                
            current_remaining = transaction.get('remaining_amount', 0)
            
            # Add the payment amount back to the remaining amount
            new_remaining = current_remaining + payment_amount
            
            # Update the transaction
            self.cursor.execute(
                "UPDATE transactions SET remaining_amount = ?, received = 0 WHERE id = ?",
                (new_remaining, transaction_id)
            )
            
            # Delete the payment
            self.cursor.execute(
                "DELETE FROM partial_payments WHERE id = ?",
                (payment_id,)
            )
            
            self.connection.commit()
            return True, "Payment deleted successfully"
            
        except sqlite3.Error as e:
            print(f"Error deleting partial payment: {e}")
            return False, f"Database error: {e}"
    
    def calculate_pending_interest_dalali(self, transaction_id, calculation_date=None):
        """
        Calculate the pending interest and dalali on the remaining amount
        from the last payment date (or start date) until the given date or today
        """
        try:
            if calculation_date is None:
                calculation_date = datetime.now().date()
            else:
                if isinstance(calculation_date, str):
                    calculation_date = datetime.strptime(calculation_date, '%Y-%m-%d').date()
            
            # Get transaction details
            transaction = self.get_transaction_by_id(transaction_id)
            if not transaction:
                return None
                
            # Get remaining amount
            remaining_amount = transaction.get('remaining_amount', transaction['total_amount'])
            if remaining_amount <= 0:
                return {
                    'remaining_amount': 0,
                    'days_since_last_payment': 0,
                    'interest_amount': 0,
                    'dalali_amount': 0
                }
            
            # Get the last payment date or use start date if no payments
            payments = self.get_partial_payments(transaction_id)
            if payments:
                last_payment_date = datetime.strptime(payments[0]['payment_date'], '%Y-%m-%d').date()
            else:
                last_payment_date = datetime.strptime(transaction['start_date'], '%Y-%m-%d').date()
            
            # Calculate days since last payment
            days = (calculation_date - last_payment_date).days
            if days <= 0:
                days = 0
            
            # Get rates
            interest_rate = transaction['interest_rate']
            dalali_rate = transaction['dalali_rate']
            
            # Calculate interest and dalali
            from calculations import calculate_interest_amount, calculate_dalali_amount, calculate_remaining_lenaar_return_amount
            
            interest_amount = calculate_interest_amount(
                remaining_amount, interest_rate * 100, days, 365
            )
            
            dalali_amount = calculate_dalali_amount(
                remaining_amount, dalali_rate * 100, days, 365
            )
            
            # Calculate the remaining lenaar return amount (remaining principal + pending interest)
            remaining_lenaar_return_amount = calculate_remaining_lenaar_return_amount(
                remaining_amount, interest_amount
            )
            
            # Store calculation for record
            self.cursor.execute('''
            INSERT INTO remaining_balances (
                transaction_id, calculation_date, remaining_amount, 
                interest_amount, dalali_amount, days_since_last_payment
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                transaction_id, calculation_date, remaining_amount,
                interest_amount, dalali_amount, days
            ))
            self.connection.commit()
            
            return {
                'remaining_amount': remaining_amount,
                'days_since_last_payment': days,
                'interest_amount': interest_amount,
                'dalali_amount': dalali_amount,
                'remaining_lenaar_return_amount': remaining_lenaar_return_amount
            }
            
        except Exception as e:
            print(f"Error calculating pending interest and dalali: {e}")
            return None
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
