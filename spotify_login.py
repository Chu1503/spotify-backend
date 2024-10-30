import requests
from flask import Flask, redirect, request, session, url_for
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Get the secret key from .env

CLIENT_ID = os.getenv('CLIENT_ID')  # Get the client ID from .env
CLIENT_SECRET = os.getenv('CLIENT_SECRET')  # Get the client secret from .env
REDIRECT_URI = 'http://localhost:5000/callback'

# Authorization URL
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
USER_PROFILE_URL = "https://api.spotify.com/v1/me"

@app.route('/')
def index():
    # Check if the user is already logged in
    access_token = session.get('access_token')
    if not access_token:
        return '<a href="/login">Login to Spotify</a>'

    # User is logged in, fetch and display profile information
    headers = {'Authorization': f'Bearer {access_token}'}
    user_profile_response = requests.get(USER_PROFILE_URL, headers=headers)
    user_profile = user_profile_response.json()

    # Safely extract user profile information
    followers_count = user_profile.get('followers', {}).get('total', 0)
    display_name = user_profile.get('display_name', 'Unknown User')  # Fallback if not available
    profile_image_url = user_profile['images'][0]['url'] if user_profile.get('images') else 'https://via.placeholder.com/100'

    # Fetch user playlists to get the count
    playlists_response = requests.get(f'{USER_PROFILE_URL}/playlists', headers=headers)
    playlists_data = playlists_response.json()

    # Count the number of playlists
    playlists_count = len(playlists_data.get('items', []))

    # Display user profile information with the number of playlists
    return f'''
        <h1>User Profile</h1>
        <img src="{profile_image_url}" alt="Profile Picture" style="width:100px;height:100px;">
        <p><strong>Name:</strong> {display_name}</p>
        <p><strong>Followers:</strong> {followers_count}</p>
        <p><strong>Number of Playlists:</strong> {playlists_count}</p>
        <a href="/playlists">View Playlists</a>
        <a href="/logout">Logout</a>
    '''

@app.route('/login')
def login():
    auth_query = f'{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user-read-private user-read-email playlist-read-private'
    return redirect(auth_query)

@app.route('/callback')
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

    # Redirect to the homepage with user profile after login
    return redirect(url_for('index'))

@app.route('/playlists')
def playlists():
    # Use the access token from the session
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('index'))

    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Fetch user playlists
    playlists_response = requests.get(f'{USER_PROFILE_URL}/playlists', headers=headers)
    playlists_data = playlists_response.json()

    # Extract playlist details
    playlists_list = playlists_data.get('items', [])
    playlists_info = ""
    for playlist in playlists_list:
        playlist_name = playlist['name']
        playlist_tracks_count = playlist['tracks']['total']
        # Get the playlist image, default to a placeholder if not available
        playlist_image_url = playlist['images'][0]['url'] if playlist['images'] else 'https://via.placeholder.com/150'
        playlists_info += f'''
            <div style="margin-bottom: 20px;">
                <img src="{playlist_image_url}" alt="{playlist_name} Image" style="width:150px;height:150px;">
                <p><strong>{playlist_name}</strong>: {playlist_tracks_count} tracks</p>
            </div>
        '''

    # Display playlists information
    return f'''
        <h1>Your Playlists</h1>
        {playlists_info}
        <a href="/">Back to Home</a>  <!-- This will take you back to the home page -->
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)