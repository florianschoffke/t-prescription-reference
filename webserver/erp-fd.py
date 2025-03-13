from flask import Flask, jsonify
import requests
import random
import string
import os

app = Flask(__name__)

# Set the NO_PROXY environment variable to prevent requests from going through the proxy if necessary
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# Function to generate random prescription data
def generate_random_prescription():
    prescription_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    patient_name = ''.join(random.choices(string.ascii_uppercase, k=5))
    medication = ''.join(random.choices(string.ascii_uppercase, k=7))
    dispense_date = f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    off_label_use = random.choice(['true', 'false'])
    return prescription_id, patient_name, medication, dispense_date, off_label_use

# Function to retrieve a bearer token
def get_bearer_token():
    print("Getting Token")
    try:
        # Replace with your actual client credentials
        client_id = 'client_id_1'
        client_secret = 'client_secret_1'

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
        response = jsonify({'status': response.status_code, 'message': response.json()}), response.status_code
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except requests.exceptions.RequestException as e:
        response = jsonify({'error': str(e)}), 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    app.run(port=3002, debug=True)
