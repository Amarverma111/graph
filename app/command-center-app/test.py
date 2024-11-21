import os
import requests
import msal
from flask import Flask, redirect, request, session, url_for, jsonify

app = Flask(__name__)

# Configuration - Replace with your own values
CLIENT_ID = '27ce20df-bdfa-4c24-90e2-cf6ba7ffa283'  # Your Azure AD App client ID
CLIENT_SECRET = 'dd67c725-2ed7-41bf-9163-8d1075d4adb4'  # Your Azure AD App client secret
TENANT_ID = '81844cf8-6426-4db3-923d-0945ee101579'  # Your Azure AD tenant ID
REDIRECT_URI = 'https://127.0.0.1:8001/'  # Redirect URI registered in Azure AD
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'

# Microsoft Graph API endpoint for fetching user calendar events
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/events'

# OAuth2 Scopes
SCOPES = ['User.Read', 'Calendars.Read', 'OnlineMeetings.Read']

# Flask session secret key
app.secret_key = os.urandom(24)


# Initialize MSAL confidential client
def get_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )


# Step 1: Start OAuth2 flow - User will be redirected to the Microsoft login page
@app.route('/login')
def index():
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI)
    return redirect(auth_url)


# Step 2: The user is redirected back to this route after login
@app.route('/getAToken')
def get_access_token():
    code = request.args.get('code')

    if not code:
        return 'Authorization code not received', 400

    msal_app = get_msal_app()

    # Step 3: Exchange the authorization code for an access token
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    if 'access_token' in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('fetch_meetings'))
    else:
        return jsonify(result), 400


# Step 4: Use the access token to fetch meetings (events) from Microsoft Graph
@app.route('/fetch_meetings')
def fetch_meetings():
    if 'access_token' not in session:
        return redirect(url_for('index'))

    access_token = session['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Fetch meetings from Microsoft Graph API
    response = requests.get(GRAPH_API_ENDPOINT, headers=headers)

    if response.status_code == 200:
        events = response.json()
        return jsonify(events)
    else:
        return f"Error fetching meetings: {response.status_code}", 400


if __name__ == '__main__':
    app.run(debug=True, port ='5003')
