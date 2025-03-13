from flask import Flask, jsonify
from flask_cors import CORS
import requests
import random
import string
import os

app = Flask(__name__)
CORS(app)

# Set the NO_PROXY environment variable to prevent requests from going through the proxy if necessary
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

@app.after_request
def add_header(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


# Function to generate random prescription data
def generate_random_prescription():
    # Prescription ID format: [166|206].xxx.xxx.xxx.xx
    prefix = random.choice(['166', '206'])
    prescription_id = f"{prefix}." + '.'.join(''.join(random.choices(string.digits, k=3)) for _ in range(3)) + '.' + ''.join(random.choices(string.digits, k=2))
    
    # Expanded list of realistic patient names
    first_names = [
        "John", "Jane", "Alex", "Emily", "Chris", "Katie", "Michael", "Sarah",
        "David", "Laura", "Daniel", "Jessica", "James", "Megan", "Andrew", "Ashley"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Martinez",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson",
        "Anderson", "Thomas"
    ]
    patient_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Expanded list of medication names
    medications = [
        "Aspirin", "Ibuprofen", "Paracetamol", "Amoxicillin", "Ciprofloxacin", "Metformin",
        "Simvastatin", "Omeprazole", "Lisinopril", "Atorvastatin", "Levothyroxine", "Amlodipine",
        "Hydrochlorothiazide", "Albuterol", "Gabapentin", "Sertraline"
    ]
    medication = random.choice(medications)
    
    # Dispense date
    year = 2025
    month = random.randint(1, 12)
    day = random.randint(1, 28 if month in [2] else 30 if month in [4, 6, 9, 11] else 31)
    dispense_date = f"{year}-{month:02d}-{day:02d}"
    
    # Off-label use
    off_label_use = random.choice(['true', 'false'])
    
    return prescription_id, patient_name, medication, dispense_date, off_label_use


# Function to retrieve a bearer token
def get_bearer_token():
    print("Getting Token")
    try:
        # Replace with your actual client credentials and load from config
        client_id = 'client_erp_fd'
        client_secret = 'client_secret_erp_fd'

        response = requests.post(
            'http://127.0.0.1:3001/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials'
            }
        )

        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Failed to obtain token: {response.status_code} {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining token: {e}")
        return None

@app.route('/dispense', methods=['POST'])
def dispense():
    # Retrieve the bearer token
    print("Sending Dispense")
    token = get_bearer_token()
    if not token:
        return jsonify({'error': 'Failed to retrieve bearer token'}), 500

    # Generate random prescription data
    prescription_id, patient_name, medication, dispense_date, off_label_use = generate_random_prescription()
    
    # Create a CSV line with the random data
    csv_line = f"{prescription_id},{patient_name},{medication},{dispense_date},{off_label_use}"
    
    # Call the /t-prescription-carbon-copy endpoint on the other server
    print("Connect to T-Server")
    try:
        response = requests.post(
            'http://localhost:3000/t-prescription-carbon-copy',
            data=csv_line,
            headers={
                'Content-Type': 'text/csv',
                'Authorization': f'Bearer {token}'
            }
        )
        
        # Return the response from the other server
        return jsonify({'status': response.status_code, 'message': response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=3002, debug=True)
