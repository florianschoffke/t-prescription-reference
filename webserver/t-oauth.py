from flask import Flask, request, jsonify
import uuid
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, 
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Authorization", "Content-Type"])

# In-memory storage for client credentials and tokens
clients = {
    'client_id_1': 'client_secret_1',
    'client_id_2': 'client_secret_2'
}

access_tokens = {}

@app.route('/token', methods=['POST', 'OPTIONS'])
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
    
    response = jsonify({'access_token': access_token, 'token_type': 'bearer'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/resource', methods=['GET', 'OPTIONS'])
def resource():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'invalid_token'}), 401

    access_token = auth_header.split(' ')[1]
    if access_token not in access_tokens:
        return jsonify({'error': 'invalid_token'}), 401
    
    response = jsonify({'data': 'This is protected data.'})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/introspect', methods=['POST', 'OPTIONS'])
def introspect():
    print(request)
    token = request.form.get('token')
    if not token:
        return jsonify({'error': 'token_missing'}), 400

    # Check if the token is valid
    if token in access_tokens:
        response = jsonify({
            'active': True,
            'client_id': access_tokens[token]
        }), 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        response = jsonify({'active': False}), 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    app.run(port=3001, debug=True)
