import sqlite3

def create_database():
    conn = sqlite3.connect('prescriptions.db')
    cursor = conn.cursor()
    
    # Create a table for prescriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id TEXT,
            patient_name TEXT,
            medication TEXT,
            dispense_date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
