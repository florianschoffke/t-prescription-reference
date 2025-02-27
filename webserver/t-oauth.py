import os
from flask import Flask
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2 import OAuth2Request

# Allow HTTP for development
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# In-memory storage for demonstration purposes
clients = {
    "client_id_1": {
        "client_secret": "client_secret_1",
        "scope": "write"
    }
}

# Initialize Authorization Server
authorization = AuthorizationServer(app)

# Custom ClientCredentialsGrant class
class MyClientCredentialsGrant(grants.ClientCredentialsGrant):
    def authenticate_client(self, request: OAuth2Request):
        client_id = request.client_id
        client_secret = request.client_secret
        client = clients.get(client_id)
        if client and client['client_secret'] == client_secret:
            return client
        return None

    def save_token(self, token, request):
        # Token storage logic (in-memory for demonstration)
        pass

# Register grant
authorization.register_grant(MyClientCredentialsGrant)

@app.route('/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()

if __name__ == '__main__':
    app.run(port=3001, debug=True)
