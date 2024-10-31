from flask import Flask, redirect, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://spotify-auth-app.vercel.app/api/callback"  # Vercel API route

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_USER_PROFILE_URL = "https://api.spotify.com/v1/me"

@app.route('/login')
def login():
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=user-read-private user-read-email"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get("code")
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    response_data = response.json()
    access_token = response_data.get("access_token")
    
    # Get user profile data
    profile_response = requests.get(
        SPOTIFY_USER_PROFILE_URL, headers={"Authorization": f"Bearer {access_token}"}
    )
    profile_data = profile_response.json()

    return jsonify({
        "name": profile_data["display_name"],
        "followers": profile_data["followers"]["total"],
        "profile_image": profile_data["images"][0]["url"] if profile_data["images"] else "",
        "playlists": get_playlist_count(access_token)
    })

def get_playlist_count(access_token):
    response = requests.get(
        "https://api.spotify.com/v1/me/playlists", headers={"Authorization": f"Bearer {access_token}"}
    )
    playlists = response.json()
    return playlists["total"]

if __name__ == "__main__":
    app.run()
