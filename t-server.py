from flask import Flask, request, jsonify
from authlib.integrations.flask_oauth2 import ResourceProtector
import sqlite3
import csv
import io
import requests

app = Flask(__name__)

# Resource protector to secure endpoints
require_oauth = ResourceProtector()

# Function to insert prescription data into the SQLite database
def insert_prescription(prescription_id, patient_name, medication, dispense_date):
    # Connect to the SQLite database
    conn = sqlite3.connect('prescriptions.db')
    cursor = conn.cursor()
    
    # Insert the prescription data into the database
    cursor.execute('''
        INSERT INTO prescriptions (prescription_id, patient_name, medication, dispense_date)
        VALUES (?, ?, ?, ?)
    ''', (prescription_id, patient_name, medication, dispense_date))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Function to validate the access token
def validate_token(token):
    response = requests.get('http://127.0.0.1:5001/token/validate', headers={'Authorization': f'Bearer {token}'})
    return response.status_code == 200

# Protected endpoint to receive prescription data
@app.route('/t-prescription-carbon-copy', methods=['POST'])
@require_oauth('write')  # Require 'write' scope for access
def receive_prescription():
    # Get the CSV line from the request body
    csv_line = request.data.decode('utf-8')
    
    # Parse the CSV line using the csv module
    csv_reader = csv.reader(io.StringIO(csv_line))
    for row in csv_reader:
        # Check if the row has the expected number of columns (4)
        if len(row) != 4:
            return jsonify({"error": "Invalid CSV format. Expected 4 columns."}), 400
        
        # Unpack the row into individual variables
        prescription_id, patient_name, medication, dispense_date = row
        
        # Insert the data into the database
        insert_prescription(prescription_id, patient_name, medication, dispense_date)
    
    # Return a success message
    return jsonify({"message": "Prescription data received and stored successfully."}), 201

# Run the prescription service
if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Run on a different port
