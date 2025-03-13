import sqlite3
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DB_PATH = './t-database.db'  # Define the database path

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create a table for prescriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id TEXT,
            patient_name TEXT,
            medication TEXT,
            dispense_date TEXT,
            off_label_use INTEGER,
            pharmacy TEXT,
            doctor TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Establish a connection to the SQLite database, creating it if necessary."""
    if not os.path.exists(DB_PATH):
        logger.info("Database file not found. Creating database...")
        create_database()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def insert_prescription(prescription_id, patient_name, medication, dispense_date, off_label_use, pharmacy, doctor):
    """Insert a prescription into the database."""
    conn = get_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        
        # Log the data being inserted
        logger.info(f"Inserting prescription: ID={prescription_id}, Patient={patient_name}, Medication={medication}, Date={dispense_date}, OffLabelUse={off_label_use}, Pharmacy={pharmacy}, Doctor={doctor}")
        
        # Insert the prescription data into the database
        cursor.execute('''
            INSERT INTO prescriptions (prescription_id, patient_name, medication, dispense_date, off_label_use, pharmacy, doctor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (prescription_id, patient_name, medication, dispense_date, off_label_use, pharmacy, doctor))
        
        conn.commit()
        logger.info("Prescription data inserted successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error inserting prescription data: {e}")
    finally:
        conn.close()
        
def delete_all_prescriptions():
    """Delete all prescriptions from the database."""
    conn = get_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prescriptions')
        conn.commit()
        logger.info("All prescriptions deleted successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error deleting prescriptions: {e}")
    finally:
        conn.close()

def get_all_prescriptions():
    """Retrieve all prescriptions from the database."""
    conn = get_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescriptions')
        prescriptions = cursor.fetchall()
        return prescriptions
    except sqlite3.Error as e:
        logger.error(f"Error fetching prescriptions: {e}")
        return []
    finally:
        conn.close()

def get_prescriptions_off_label_use():
    """Retrieve prescriptions with off-label use from the database."""
    conn = get_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescriptions WHERE off_label_use = 1')
        prescriptions = cursor.fetchall()
        return prescriptions
    except sqlite3.Error as e:
        logger.error(f"Error fetching off-label prescriptions: {e}")
        return []
    finally:
        conn.close()

def get_prescription_by_date(date):
    """Retrieve prescriptions by dispense date from the database."""
    conn = get_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescriptions WHERE dispense_date = ?', (date,))
        prescriptions = cursor.fetchall()
        return prescriptions
    except sqlite3.Error as e:
        logger.error(f"Error fetching prescriptions by date: {e}")
        return []
    finally:
        conn.close()