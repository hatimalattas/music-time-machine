from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint
import os

pp = pprint.PrettyPrinter(indent=4)

date = input("What year would you like to travel to? Required format YYYY-MM-DD \n")

billboard_url = f"https://www.billboard.com/charts/hot-100/{date}"

response = requests.get(url=billboard_url)

hot_100_songs_web_page = response.text

soup = BeautifulSoup(hot_100_songs_web_page, 'html.parser')

scraped_songs = soup.select(".chart-element__information__song")

hot_100_songs = [song.string for song in scraped_songs]

# Spotify credentials
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get("REDIRECT_URI")

auth_manager = SpotifyOAuth(client_id=client_id,
                            client_secret=client_secret,
                            redirect_uri=redirect_uri,
                            scope="playlist-modify-private",
                            show_dialog=True,
                            cache_path="token.txt"
                            )
spotipy = spotipy.Spotify(auth_manager=auth_manager)

user_profile = spotipy.me()
user_id = user_profile["id"]

song_uris = []

for song in hot_100_songs:
    result = spotipy.search(q=f"{song}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = spotipy.user_playlist_create(user=user_id, name="python", public=False, description='Python project')
playlist_id = playlist["id"]

spotipy.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=song_uris)
