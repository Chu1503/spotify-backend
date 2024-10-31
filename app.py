from flask import Flask, redirect, request, jsonify, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_PROFILE_URL = 'https://api.spotify.com/v1/me'
SPOTIFY_PLAYLISTS_URL = 'https://api.spotify.com/v1/me/playlists'

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

@app.route('/')
def home():
    return "Welcome to the Spotify API App! Go to /auth/login to start."

@app.route('/auth/login')
def login():
    scope = "user-read-private user-read-email playlist-read-private"
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/auth/callback')
def callback():
    code = request.args.get('code')
    response = requests.post(SPOTIFY_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    session['token_info'] = response.json()
    return redirect(f'{REDIRECT_URI}')

def get_token():
    return session.get('token_info', {}).get('access_token')

@app.route('/api/profile')
def profile():
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    profile_data = requests.get(SPOTIFY_PROFILE_URL, headers=headers).json()
    playlists_data = requests.get(SPOTIFY_PLAYLISTS_URL, headers=headers).json()
    profile_data['playlists'] = playlists_data['total']
    return jsonify(profile_data)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
