from flask import Flask, request, jsonify
from authlib.integrations.flask_oauth2 import ResourceProtector
import sqlite3
import csv
import io

app = Flask(__name__)

# Resource protector to secure endpoints
require_oauth = ResourceProtector()

# Function to insert prescription data into the SQLite database
def insert_prescription(prescription_id, patient_name, medication, dispense_date, off_label_use):
    # Connect to the SQLite database
    conn = sqlite3.connect('../t-database.db')  # Updated database path
    cursor = conn.cursor()
    
    # Insert the prescription data into the database
    cursor.execute('''
        INSERT INTO prescriptions (prescription_id, patient_name, medication, dispense_date, off_label_use)
        VALUES (?, ?, ?, ?, ?)
    ''', (prescription_id, patient_name, medication, dispense_date, off_label_use))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Function to retrieve prescriptions by dispense date
def get_prescription_by_date(dispense_date):
    conn = sqlite3.connect('../t-database.db')
    cursor = conn.cursor()
    
    # Query to select prescriptions with the specified dispense date
    cursor.execute('''
        SELECT * FROM prescriptions WHERE dispense_date = ?
    ''', (dispense_date,))
    
    prescriptions = cursor.fetchall()
    conn.close()
    
    return prescriptions

# Function to retrieve all prescriptions with off-label use
def get_prescriptions_off_label_use():
    conn = sqlite3.connect('../t-database.db')
    cursor = conn.cursor()
    
    # Query to select prescriptions where off_label_use is true
    cursor.execute('''
        SELECT * FROM prescriptions WHERE off_label_use = 1
    ''')
    
    prescriptions = cursor.fetchall()
    conn.close()
    
    return prescriptions

# Protected endpoint to receive prescription data
@app.route('/t-prescription-carbon-copy', methods=['POST'])
@require_oauth('write')  # Require 'write' scope for access
def receive_prescription():
    # Get the CSV line from the request body
    csv_line = request.data.decode('utf-8')
    
    # Parse the CSV line using the csv module
    csv_reader = csv.reader(io.StringIO(csv_line))
    for row in csv_reader:
        # Check if the row has the expected number of columns (5)
        if len(row) != 5:
            return jsonify({"error": "Invalid CSV format. Expected 5 columns."}), 400
        
        # Unpack the row into individual variables
        prescription_id, patient_name, medication, dispense_date, off_label_use = row
        
        # Convert off_label_use to boolean
        off_label_use = True if off_label_use.lower() == 'true' else False
        
        # Insert the data into the database
        insert_prescription(prescription_id, patient_name, medication, dispense_date, off_label_use)
    
    # Return a success message
    return jsonify({"message": "Prescription data received and stored successfully."}), 201

# GET endpoint to retrieve prescriptions by dispense date
@app.route('/t-prescription-by-date', methods=['GET'])
@require_oauth('read')  # Require 'read' scope for access
def get_prescription_by_date_route():
    dispense_date = request.args.get('dispense_date')
    if not dispense_date:
        return jsonify({"error": "dispense_date query parameter is required."}), 400
    
    prescriptions = get_prescription_by_date(dispense_date)
    
    if prescriptions:
        # Convert the list of tuples to a list of dictionaries for JSON response
        prescriptions_list = [
            {
                "prescription_id": prescription[1],
                "patient_name": prescription[2],
                "medication": prescription[3],
                "dispense_date": prescription[4],
                "off_label_use": prescription[5]
            }
            for prescription in prescriptions
        ]
        return jsonify(prescriptions_list), 200
    else:
        return jsonify({"message": "No prescriptions found for the given dispense date."}), 404

# GET endpoint to retrieve all prescriptions with off-label use
@app.route('/t-prescription-off-label-use', methods=['GET'])
@require_oauth('read')  # Require 'read' scope for access
def get_prescription_off_label_use_route():
    prescriptions = get_prescriptions_off_label_use()
    
    if prescriptions:
        # Convert the list of tuples to a list of dictionaries for JSON response
        prescriptions_list = [
            {
                "prescription_id": prescription[1],
                "patient_name": prescription[2],
                "medication": prescription[3],
                "dispense_date": prescription[4],
                "off_label_use": prescription[5]
            }
            for prescription in prescriptions
        ]
        return jsonify(prescriptions_list), 200
    else:
        return jsonify({"message": "No prescriptions found with off-label use."}), 404

# Run the prescription service
if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Run on a different port
