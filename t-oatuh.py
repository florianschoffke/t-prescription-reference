from flask import Flask, request, jsonify
from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector, ClientCredentialsGrant

app = Flask(__name__)

# In-memory storage for clients and tokens (for demonstration purposes)
clients = {
    "client_id_1": {
        "client_secret": "client_secret_1",  # Client secret for authentication
        "scope": "write"  # Scope of access
    }
}

# Dictionary to store issued tokens (for demonstration purposes)
tokens = {}

# Initialize the OAuth 2.0 server
authorization = AuthorizationServer(app)

# Resource protector to secure endpoints
require_oauth = ResourceProtector()

# Custom Client Credentials Grant class
class MyClientCredentialsGrant(ClientCredentialsGrant):
    # Save the issued token
    def save_token(self, token, client):
        tokens[token['access_token']] = token

    # Validate client credentials
    def get_client(self, client_id, client_secret):
        client = clients.get(client_id)
        if client and client['client_secret'] == client_secret:
            return client  # Return the client if credentials are valid
        return None  # Return None if credentials are invalid

# Register the custom grant with the authorization server
authorization.register_grant(MyClientCredentialsGrant)

# Endpoint to issue access tokens
@app.route('/token', methods=['POST'])
def issue_token():
    # Create and return a token response
    return authorization.create_token_response()

# Run the OAuth server
if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Run on a different port
