from flask import Flask, request, jsonify
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# In-memory storage for client credentials and tokens
clients = {
    'client_id_1': 'client_secret_1'
}

access_tokens = {}

@app.route('/token', methods=['POST'])
def token():
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    grant_type = request.form.get('grant_type')
    print(clients[client_id])
    
    if grant_type != 'client_credentials':
        return jsonify({'error': 'unsupported_grant_type'}), 400

    if request.form.get('client_id') not in clients or clients[client_id] != client_secret:
        return jsonify({'error': 'invalid_client'}), 400

    # Issue an access token
    access_token = str(uuid.uuid4())
    access_tokens[access_token] = client_id

    return jsonify({'access_token': access_token, 'token_type': 'bearer'})

@app.route('/resource', methods=['GET'])
def resource():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'invalid_token'}), 401

    access_token = auth_header.split(' ')[1]
    if access_token not in access_tokens:
        return jsonify({'error': 'invalid_token'}), 401

    return jsonify({'data': 'This is protected data.'})

if __name__ == '__main__':
    app.run(port=3001, debug=True)
