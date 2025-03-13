from flask import Flask, request, jsonify
from flask_cors import CORS
import t_database
import sqlite3
import csv
import io
import requests
import logging

app = Flask(__name__)
CORS(app)

# Middleware to check token validity
@app.before_request
def check_token():
    if request.method != 'OPTIONS':
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 403

        token = auth_header.split(" ")[1]  # Extract the token from the header

        print(validate_token(token))
        if not validate_token(token):
            return jsonify({"error": "Invalid or expired token"}), 401

@app.after_request
def add_header(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

# In-memory storage to simulate token validation
# This should be synchronized with the OAuth server's in-memory storage
access_tokens = {
    # Example token: 'example_token': 'client_id_123'
}

# Function to validate the access token
def validate_token(token):
    print("Validating Token")
    introspection_url = "http://localhost:3001/introspect"
    response = requests.post(introspection_url, data={'token': token})
    token_info = response.json()
    print(token_info)
    return token_info.get('active', False)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Function to interact with database


# Endpoint to receive prescription data
@app.route('/t-prescription-carbon-copy', methods=['POST', 'OPTIONS'])
def receive_prescription():
    csv_line = request.data.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_line))
    for row in csv_reader:
        if len(row) != 7:
            return jsonify({"error": "Invalid CSV format. Expected 5 columns."}), 400
        
        prescription_id, patient_name, medication, dispense_date, off_label_use, pharmacy, doctor = row
        off_label_use = True if off_label_use.lower() == 'true' else False
        
        t_database.insert_prescription(prescription_id, patient_name, medication, dispense_date, off_label_use, pharmacy, doctor)
        
    return jsonify({"message": "Prescription data received and stored successfully."}), 201
    

# Endpoint to retrieve all prescriptions
@app.route('/t-prescription-all', methods=['GET', 'OPTIONS'])
def get_all_prescriptions_route():
    prescriptions = t_database.get_all_prescriptions()
    
    print(prescriptions)
    
    if prescriptions:
        prescriptions_list = [
            {
                "prescription_id": prescription[1],
                "patient_name": prescription[2],
                "medication": prescription[3],
                "dispense_date": prescription[4],
                "off_label_use": prescription[5],
                "pharmacy": prescription[6],
                "doctor": prescription[7]
            }
            for prescription in prescriptions
        ]
        return jsonify(prescriptions_list), 200
    elif len(prescriptions) == 0:
        return jsonify({"message": "No prescriptions found"}), 200
    else:
        return jsonify({"message": "Error"}), 500

# Endpoint to retrieve prescriptions by dispense date
@app.route('/t-prescription-by-date', methods=['GET', 'OPTIONS'])
def get_prescription_by_date_route():
    dispense_date = request.args.get('dispense_date')
    if not dispense_date:
        return jsonify({"error": "dispense_date query parameter is required."}), 400
    
    prescriptions = t_database.get_prescription_by_date(dispense_date)
    
    if prescriptions:
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

# Endpoint to retrieve all prescriptions with off-label use
@app.route('/t-prescription-off-label-use', methods=['GET', 'OPTIONS'])
def get_prescription_off_label_use_route():
    prescriptions = t_database.get_prescriptions_off_label_use()
    
    if prescriptions:
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


@app.route('/delete-prescriptions', methods=['DELETE'])
def delete_prescriptions_endpoint():
    try:
        t_database.delete_all_prescriptions()
        return jsonify({"message": "All prescriptions deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
