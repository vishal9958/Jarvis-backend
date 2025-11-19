# Jarvis_spotify_player.py
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from livekit.agents import function_tool

# .env file se credentials load karega
scope = "user-modify-playback-state user-read-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

@function_tool
def play_on_spotify(track_name: str) -> str:
    """
    Searches for a track on Spotify and plays it on the active device.
    Use this to play songs on Spotify.
    For example: "Play 'Kesariya' on Spotify"
    """
    try:
        # Check for active devices
        devices = sp.devices()
        if not devices or not devices['devices']:
            return "Sorry, I couldn't find any active Spotify device. Please start playing something on any device first."

        # Search for the track
        results = sp.search(q=f'track:{track_name}', type='track', limit=1)
        tracks = results['tracks']['items']

        if not tracks:
            return f"Sorry, I could not find the track '{track_name}' on Spotify."

        # Get the URI of the first track and play it
        track_uri = tracks[0]['uri']
        sp.start_playback(uris=[track_uri])

        song_name = tracks[0]['name']
        artist_name = tracks[0]['artists'][0]['name']
        return f"Now playing '{song_name}' by {artist_name} on Spotify."

    except Exception as e:
        return f"An error occurred: {e}"