import sqlite3

# Connect to the database
conn = sqlite3.connect('data/hisaabsetu.db')
cursor = conn.cursor()

# Get the table structure
cursor.execute("PRAGMA table_info(transactions);")
columns = cursor.fetchall()

print("Transactions Table Structure:")
for column in columns:
    print(f"Column {column[0]}: {column[1]} ({column[2]})")

# Close the connection
conn.close()