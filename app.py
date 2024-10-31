from flask import Flask, redirect, request, session, url_for, jsonify
import requests
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

@app.route('/login')
def login():
    # Spotify authorization URL
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": "user-read-private user-read-email user-follow-read"
    }
    # Redirect to Spotify's OAuth page
    url = f"{auth_url}?{urlencode(params)}"
    return redirect(url)

@app.route('/callback')
def callback():
    # Get authorization code from Spotify
    code = request.args.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    # Request access token from Spotify
    response = requests.post(token_url, data=payload)
    response_data = response.json()
    
    # Save access token to session
    session["access_token"] = response_data.get("access_token")
    return redirect(url_for("profile"))

@app.route('/profile')
def profile():
    # Ensure access token is available
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Fetch user profile information
    profile_url = "https://api.spotify.com/v1/me"
    profile_response = requests.get(profile_url, headers=headers)
    profile_data = profile_response.json()
    
    # Fetch user's playlists count
    playlists_url = "https://api.spotify.com/v1/me/playlists"
    playlists_response = requests.get(playlists_url, headers=headers)
    playlists_data = playlists_response.json()
    
    # Prepare profile information for response
    profile_info = {
        "Name": profile_data.get("display_name"),
        "Followers": profile_data.get("followers", {}).get("total"),
        "Pic": profile_data["images"][0]["url"] if profile_data.get("images") else None,
        "Playlists": playlists_data.get("total", 0)
    }
    
    # Return profile information as JSON
    return jsonify(profile_info)

if __name__ == "__main__":
    app.run(debug=True)