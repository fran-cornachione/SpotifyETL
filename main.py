import spotipy
import os
import re
import polars as pl
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id = os.getenv("SPOTIFY_CLIENT_ID"), # Spotify Client (Replace with yours)
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET"), # Spotify Client Secret (Replace with yours)
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI"), # Redirect URI (I used http://127.0.0.1:8888/callback)
    scope=( 
    "playlist-read-private "
    "playlist-read-collaborative "
    "user-library-read " 
    # Add more scopes if you need to
)
))

user = sp.current_user() # My user 
playlists = sp.current_user_playlists() # All my playlists (Owned and Saved)
my_playlists = [pla for pla in playlists['items'] if pla['owner']['id'] == user['id']] # All my playlists (Created by me)

for playlist in my_playlists: # In case you want all your playlists (created and saved) use the variable playlists
    playlist_id = playlist['id']
    playlist_name = playlist['name']
    track_data = [] # Initializes the list where the data for all the songs in this playlist will be saved.

    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    for item in tracks:
        try:
            track = item['track']
            if not track: 
                continue

            artists_names = [artist['name'] for artist in track['artists'] if artist['name']]

            # Add song data to the list
            track_data.append({
                'track_name': track['name'],
                'artists': ', '.join(artists_names), # Artist 1, Artist 2, ...
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'duration_m': round(track['duration_ms'] / 60000, 2),
                'explicit': track['explicit'],
                'id': track['id']
                # 'track_number': track['track_number'] Track number in the album, remove the "#" in order to add this column to your playlist dataset
            })
        except Exception as e:
            print(f"Error processing a song in {playlist_name}: {e}") # If something goes wrong with a track, the error is displayed but it continues

    if track_data:
        invalid_chars = r'[<>:"/\\|?*\'@]' # Some tracks names might contain invalid characters (<, >, @, etc)
        safe_filename = re.sub(invalid_chars, '_', playlist_name) # If that happens, we replace them with an underscore (_)
        filename = os.path.join("data", f"{safe_filename}.csv")

        playlist_df = pl.DataFrame(track_data)
        playlist_df.write_csv(filename) # Write data to a csv file. You can choose Parquet, Excel, etc. 
            
print("-" * 30)
print(f"{len(my_playlists)} playlists saved!") # Returns the number of playlists saved