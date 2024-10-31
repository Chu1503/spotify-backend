# app/routes.py
from flask import Blueprint, session, jsonify, redirect, url_for
import requests
import os

main_bp = Blueprint('main', __name__)
USER_PROFILE_URL = "https://api.spotify.com/v1/me"

@main_bp.route('/')
def index():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Unauthorized"}), 401

    # Fetch user profile information
    headers = {'Authorization': f'Bearer {access_token}'}
    user_profile_response = requests.get(USER_PROFILE_URL, headers=headers)
    user_profile = user_profile_response.json()

    # Extract profile information
    followers_count = user_profile.get('followers', {}).get('total', 0)
    display_name = user_profile.get('display_name', 'Unknown User')
    profile_image_url = user_profile['images'][0]['url'] if user_profile.get('images') else ''

    # Fetch user playlists count
    playlists_response = requests.get(f'{USER_PROFILE_URL}/playlists', headers=headers)
    playlists_data = playlists_response.json()
    playlists_count = len(playlists_data.get('items', []))

    # Return JSON with profile data
    return jsonify({
        "display_name": display_name,
        "followers_count": followers_count,
        "profile_image_url": profile_image_url,
        "playlists_count": playlists_count
    })

@main_bp.route('/playlists')
def playlists():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Unauthorized"}), 401

    headers = {'Authorization': f'Bearer {access_token}'}
    playlists_response = requests.get(f'{USER_PROFILE_URL}/playlists', headers=headers)
    playlists_data = playlists_response.json()

    # Extract playlist details
    playlists_list = playlists_data.get('items', [])
    playlists_info = []
    for playlist in playlists_list:
        playlist_info = {
            "name": playlist['name'],
            "tracks_count": playlist['tracks']['total'],
            "image_url": playlist['images'][0]['url'] if playlist['images'] else ''
        }
        playlists_info.append(playlist_info)

    # Return JSON with playlists data
    return jsonify(playlists_info)

@main_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})