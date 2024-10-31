# app/auth.py
from flask import Blueprint, redirect, request, session, url_for, jsonify
import requests
import os

auth_bp = Blueprint('auth', __name__)
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

@auth_bp.route('/login')
def login():
    auth_query = f'{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user-read-private user-read-email playlist-read-private'
    return redirect(auth_query)

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    # Get access token
    response = requests.post(TOKEN_URL, data=token_data)
    response_data = response.json()
    access_token = response_data.get('access_token')

    # Store access token in session
    session['access_token'] = access_token

    # Redirect to front end after authentication
    return redirect(url_for('main.index'))