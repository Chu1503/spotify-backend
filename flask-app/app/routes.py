# app/routes.py
from flask import Blueprint, session, redirect, url_for
import requests
import os

main_bp = Blueprint('main', __name__)
USER_PROFILE_URL = "https://api.spotify.com/v1/me"

@main_bp.route('/')
def index():
    access_token = session.get('access_token')
    if not access_token:
        return '<a href="/login">Login to Spotify</a>'

    # Fetch user profile information
    headers = {'Authorization': f'Bearer {access_token}'}
    user_profile_response = requests.get(USER_PROFILE_URL, headers=headers)
    user_profile = user_profile_response.json()

    # Extract profile information safely
    followers_count = user_profile.get('followers', {}).get('total', 0)
    display_name = user_profile.get('display_name', 'Unknown User')
    profile_image_url = user_profile['images'][0]['url'] if user_profile.get('images') else 'https://via.placeholder.com/100'

    # Fetch user playlists to get the count
    playlists_response = requests.get(f'{USER_PROFILE_URL}/playlists', headers=headers)
    playlists_data = playlists_response.json()
    playlists_count = len(playlists_data.get('items', []))

    # Display user profile and playlists count
    return f'''
        <h1>User Profile</h1>
        <img src="{profile_image_url}" alt="Profile Picture" style="width:100px;height:100px;">
        <p><strong>Name:</strong> {display_name}</p>
        <p><strong>Followers:</strong> {followers_count}</p>
        <p><strong>Number of Playlists:</strong> {playlists_count}</p>
        <a href="/playlists">View Playlists</a>
        <a href="/logout">Logout</a>
    '''

@main_bp.route('/playlists')
def playlists():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('main.index'))

    headers = {'Authorization': f'Bearer {access_token}'}
    playlists_response = requests.get(f'{USER_PROFILE_URL}/playlists', headers=headers)
    playlists_data = playlists_response.json()

    # Extract playlist details
    playlists_list = playlists_data.get('items', [])
    playlists_info = ""
    for playlist in playlists_list:
        playlist_name = playlist['name']
        playlist_tracks_count = playlist['tracks']['total']
        playlist_image_url = playlist['images'][0]['url'] if playlist['images'] else 'https://via.placeholder.com/150'
        playlists_info += f'''
            <div style="margin-bottom: 20px;">
                <img src="{playlist_image_url}" alt="{playlist_name} Image" style="width:150px;height:150px;">
                <p><strong>{playlist_name}</strong>: {playlist_tracks_count} tracks</p>
            </div>
        '''

    # Display playlists
    return f'''
        <h1>Your Playlists</h1>
        {playlists_info}
        <a href="/">Back to Home</a>
    '''

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))