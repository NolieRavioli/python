def crypt_key(KEY_FILE = '$.key', DATA_FOLDER = '.gitignore/data/')):
    """load encrypted files."""
    #print('crypt_key func')
    from cryptography.fernet import Fernet
    from os import path
    if not path.exists(DATA_FOLDER + KEY_FILE):
        with open(DATA_FOLDER + KEY_FILE, "wb") as key_file:
            key = Fernet.generate_key()
            key_file.write(key)
    else:
        with open(DATA_FOLDER + KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return Fernet(key)

def load_token(DATA_FOLDER='.gitignore/data/', TOKEN_FILE='.token'):
    """load_token."""
    #print('load_token func')
    from os import path, makedirs
    makedirs(DATA_FOLDER.strip('/'), exist_ok=True)
    from time import time
    from json import loads
    if path.exists(DATA_FOLDER + TOKEN_FILE):
        fernet = crypt_key()
        with open(DATA_FOLDER + TOKEN_FILE, 'rb') as token_file:
            encrypted_token = token_file.read()
        token_data = loads(fernet.decrypt(encrypted_token).decode())
    else:
        print("No token found.")
        token_data = firstAuth()
    token_data['access_token'] = validateToken(token_data['access_token'],token_data['refresh_token'])
    
    
    return token_data

def save_token(token_data, DATA_FOLDER = '.gitignore/data/', TOKEN_FILE = '.token'):
    """save_token."""
    #print('save_token func')
    from json import dumps
    fernet = crypt_key()
    encrypted_token = fernet.encrypt(dumps(token_data).encode())
    with open(DATA_FOLDER + TOKEN_FILE, "wb") as token_file:
        token_file.write(encrypted_token)

def new_token(refresh_token, TOKEN_URL="https://login.eveonline.com/v2/oauth/token"):
    """new_token."""
    #print('new_token func')
    from time import time
    from requests import post
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES = load_client_credentials()
    response = post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,})
    if response.status_code == 200:
        new_token_data = response.json()
        new_token_data['expires_at'] = time()+2000
        if validateToken(new_token_data['access_token'],refresh_token):
            save_token(new_token_data)
        else:
            print('cant refresh')
            exit()
        return new_token_data
    else:
        raise Exception(f'Failed to refresh token: {response.status_code}, {response.text}')

def load_client_credentials(DATA_FOLDER='.gitignore/data/', CLIENT_CRED_FILE=".clientcred", DB_FILE='eve.db'):
    """load_client_credentials."""
    #print('load_client_credentials func')
    from os import path
    from json import dumps,loads
    fernet = crypt_key()
    if path.exists(DATA_FOLDER + CLIENT_CRED_FILE):
        with open(DATA_FOLDER + CLIENT_CRED_FILE, "rb") as cred_file:
            encrypted_creds = cred_file.read()
        creds = loads(fernet.decrypt(encrypted_creds).decode())
        return creds['client_id'], creds['client_secret'], creds['redirect_uri'], creds['scopes']
    import webbrowser
    webbrowser.open('https://developers.eveonline.com/applications')
    client_id = input("Enter your client ID: ").strip()
    client_secret = input("Enter your client secret: ").strip()
    redirect_uri = input("Enter callback URL: ").strip()
    scopes = input("Enter scopes: ")
    creds = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "scopes": scopes
    }
    
    import dbLib
    dbLib.addEntry("applications",['Test',client_id,client_secret,scopes],dbLib.connDB(DATA_FOLDER+DB_FILE))
    encrypted_creds = fernet.encrypt(dumps(creds).encode())
    with open(DATA_FOLDER + CLIENT_CRED_FILE, "wb") as cred_file:
        cred_file.write(encrypted_creds)
    return creds['client_id'], creds['client_secret'], creds['redirect_uri'], creds['scopes']

def firstAuth(AUTHORIZATION_BASE_URL='https://login.eveonline.com/v2/oauth/authorize',
              TOKEN_URL='https://login.eveonline.com/v2/oauth/token'):
    """Open a Browser for SSO auth"""
    #print('firstAuth func')
    APPS = {
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': ''
        }
    from flask import Flask, request, session
    from os import environ, urandom
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    from requests_oauthlib import OAuth2Session
    from requests.auth import HTTPBasicAuth
    from threading import Timer
    import webbrowser
    from werkzeug.serving import make_server
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES = load_client_credentials()
    token = None
    auth = Flask(__name__)
    auth.secret_key = CLIENT_ID
    @auth.route("/")
    def index():
        """Generate the Authorization URL and redirect the user with JavaScript."""
        eve = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
        eve.headers.update({"Cache-Control": "no-cache"})
        authorization_url, state = eve.authorization_url(AUTHORIZATION_BASE_URL)
        session["oauth_state"] = state
        return f"""
        <html>
        <head>
            <title>Redirecting...</title>
            <script type="text/javascript">window.onload = function() {{window.location.href = "{authorization_url}";}};</script>
        </head>
        <body>
            <p>Redirecting to EVE Online for auth...</p>
        </body>
        </html>
        """

    @auth.route("/callback")
    def callback(DATA_FOLDER='.gitignore/data/',DB_FILE='eve.db'):
        """Handle the callback and fetch the token."""
        state = session.get("oauth_state")
        nonlocal token
        print(f"DEBUG: State from session: {state}")
        if not state:
            print("DEBUG: State mismatch or session expired.")
            return "Session expired. Please try again."
        eve = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=state, scope=SCOPES)
        try:
            auth_header = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
            token = eve.fetch_token(
                TOKEN_URL,
                authorization_response=request.url,
                auth=auth_header,
            )
            print(f"DEBUG: Token fetched: {token}")
            save_token(token)            
            import dbLib ########################
            dbLib.addEntry("tokens",{'access_token':token['access_token'],'refresh_token':token['refresh_token'],'expires_at':token['expires_at'],'character_index':1},dbLib.connDB(DATA_FOLDER+DB_FILE))
        except Exception as e:
            print(f"DEBUG: Error fetching token: {e}")
            return f"Error fetching token: {e}"
        Timer(1, lambda: shutdown_server(shutdown_func)).start()
        return "Authorization complete! You can close this window."

    def shutdown_server(shutdown_func):
        """Shut down the Flask server."""
        if shutdown_func:
            shutdown_func()
        else:
            print("DEBUG: No shutdown function available.")

    # First Auth Logic =================================
    server = make_server("127.0.0.1", 5000, auth)
    shutdown_func = server.shutdown
    print("DEBUG: Starting Flask server for authentication.")
    webbrowser.open("http://localhost:5000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("DEBUG: Flask server interrupted.")
        shutdown_server(shutdown_func)
    return token
    
def validateToken(token, refresh_token,
                  JWT_URL="https://login.eveonline.com/oauth/jwks",
                  DATA_FOLDER='.gitignore/data/', TOKEN_FILE=".token", VERI_CACHE='.verify'):
    """Validate the JWT token against EVE's public JWKS."""
    import jwt
    from jwt.algorithms import RSAAlgorithm
    import json
    from requests import get
    from time import time
    from os import path

    try:
        # Load JWKS from cache or fetch it
        if path.exists(DATA_FOLDER + VERI_CACHE):
            with open(DATA_FOLDER + VERI_CACHE, 'r') as verifyDump:
                jwks = json.load(verifyDump)
        else:
            response = get(JWT_URL)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch JWKS: {response.status_code} {response.text}")
            jwks = response.json()
            with open(DATA_FOLDER + VERI_CACHE, 'w') as verifyDump:
                json.dump(jwks, verifyDump)

        # key id search
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise Exception("JWT is missing 'kid' in the header.")
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                break
        if not public_key:
            print(f"No matching key found for 'key id': {kid}")
            response = get(JWT_URL)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch JWKS: {response.status_code} {response.text}")
            jwks = response.json()
            with open(DATA_FOLDER + VERI_CACHE, 'w') as verifyDump:
                json.dump(jwks, verifyDump)
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            if not public_key:
                raise Exception(f"No matching key found for 'key id': {kid} even after refreshing JWKS.")

        # Decode and verify
        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="EVE Online",
            options={"verify_exp": True}
        )
        if time() > decoded_token['exp'] or decoded_token['iat'] > time():
            print(f"time: {time()}. Exp: {decoded_token['exp']}. iat {decoded_token['iat']}.")
        return token

    except jwt.ExpiredSignatureError:
        print("DEBUG: The token has expired.")
        # Refresh the token
        token_data = new_token(refresh_token)
        token = token_data['access_token']
        save_token(token_data)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise Exception("JWT is missing 'kid' in the header.")
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                break
        if not public_key:
            print(f"No matching key found for 'key id': {kid} after token refresh.")
            response = get(JWT_URL)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch JWKS: {response.status_code} {response.text}")
            jwks = response.json()
            with open(DATA_FOLDER + VERI_CACHE, 'w') as verifyDump:
                json.dump(jwks, verifyDump)
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            if not public_key:
                raise Exception(f"No matching key found for 'key id': {kid} even after refreshing JWKS.")

        # Decode and verify the new token
        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="EVE Online",
            options={"verify_exp": True}
        )
        return token

    except Exception as e:
        print(f"DEBUG: Validation failed: {e}")
        raise
    
if __name__ == "__main__":
    output = load_token()
    if output:
        print("Token loaded successfully.")
    else:
        print("DANGER")

    from requests import get
    # character_id = {charid}
    token = output['access_token']
    print(token)
    # headers = {"Authorization": f"Bearer {token}"}
    # response = get(f"https://esi.evetech.net/latest/characters/{character_id}/skills/", headers=headers)
    # print(f'{response.text}')

