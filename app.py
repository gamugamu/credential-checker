from flask import Flask, redirect, request
from oauth2client.client import OAuth2WebServerFlow
import json
from oauth2client.client import AccessTokenCredentials

app     = Flask(__name__)
flow    = OAuth2WebServerFlow( client_id    ='826903433229-tnt9v5hqfnehcgpp1jtujhpeucjekmcl.apps.googleusercontent.com',
                            client_secret   ='uf61_58yxN573EyNBEjAL06n',
                            scope           ='https://www.googleapis.com/auth/plus.me',
                            redirect_uri    ='http://localhost:5000/oauth2callback')

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/login")
def login():
    print "login"

    auth_uri = flow.step1_get_authorize_url()
    print "auth_uri ", auth_uri
    return redirect(auth_uri)

@app.route("/oauth2callback")
def oauth2callback():
    code        = request.args.get('code')
    credentials = flow.step2_exchange(code)
    print "credential--> ", credentials

    # SERVER
    token = credentials.access_token
    print "access token--> ", token
    # return credential object
    credentials = AccessTokenCredentials(token, 'user-agent-value')
    print "credential 2 --> ", credentials
    return token
    return _request_user_info(credentials)

def _request_user_info(credentials):
    import httplib2
    """
    Makes an HTTP request to the Google+ API to retrieve the user's basic
    profile information, including full name and photo, and stores it in the
    Flask session.
    """
    http            = httplib2.Http()
    credentials.authorize(http)
    resp, content   = http.request('https://www.googleapis.com/plus/v1/people/me')
    print "resp.status ", resp.status

    if resp.status != 200:
        print("Error while obtaining user profile: \n%s: %s", resp, content)
        return "error"

    profil = json.loads(content.decode('utf-8'))
    # session['profile'] = json.loads(content.decode('utf-8'))
    print "profil--> ", profil
    return profil['id']

if __name__ == '__main__':
    app.run()
