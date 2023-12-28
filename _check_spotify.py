import requests
import base64
import random

def get_spotify_access_token(client_id, client_secret):
    # Spotify URL for obtaining access token
    token_url = 'https://accounts.spotify.com/api/token'

    # Encode as Base64
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    # Headers
    token_headers = {
        "Authorization": f"Basic {client_creds_b64.decode()}"  # Basic <base64 encoded client_id:client_secret>
    }

    # Data
    token_data = {
        "grant_type": "client_credentials"
    }

    # POST request
    r = requests.post(token_url, headers=token_headers, data=token_data)
    token_response_data = r.json()
    return token_response_data.get("access_token")

def get_random_songs(client_id, client_secret):
    token = get_spotify_access_token(client_id, client_secret)

    if token:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # For randomness, you might pick a random genre/artist/album, etc.
        # For simplicity, let's use a broad search term like 'year:2020'
        random_year = random.randint(2000, 2023)
        query = f'year:{random_year}'
        endpoint = f"https://api.spotify.com/v1/search?type=track&q={query}&limit=10"

        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            tracks_data = response.json()['tracks']['items']
            return [{'name': track['name'], 'spotify_id': track['id']} for track in tracks_data]
        else:
            print("Error fetching tracks:", response.status_code, response.text)
            return []
    else:
        print("Error obtaining access token")
        return []








# def get_diverse_songs_from_playlists(sp, playlist_ids):
#     selected_tracks = []
#     genre_count = defaultdict(int)

#     for playlist_id in playlist_ids:
#         # Get all tracks from the playlist
#         results = sp.playlist_tracks(playlist_id)
#         tracks = results['items']

#         # Keep fetching tracks until we have them all
#         while results['next']:
#             results = sp.next(results)
#             tracks.extend(results['items'])

#         # Map tracks to their genres
#         track_genres = {}
#         for track in tracks:
#             if track['track']:
#                 artist_id = track['track']['artists'][0]['id']
#                 artist_info = sp.artist(artist_id)
#                 genres = artist_info['genres']
#                 track_genres[track['track']['uri']] = (track['track'], genres)

#         # Select a track with a less represented genre
#         print("Steem")
#         least_represented_genre_track = None
#         min_genre_count = float('inf')
#         for track_uri, (track, genres) in track_genres.items():
#             if genres:
#                 genre = genres[0]  # Consider the first genre listed
#                 if genre_count[genre] < min_genre_count:
#                     min_genre_count = genre_count[genre]
#                     least_represented_genre_track = (track, genres)
#         print("Steem2")
#         if least_represented_genre_track:
#             track, genres = least_represented_genre_track
#             selected_tracks.append((track['name'], track['artists'][0]['name'], track['uri'], genres))
#             genre_count[genres[0]] += 1

#     return selected_tracks







# def get_random_songs_from_playlist(sp, playlist_id, num_songs=3):
#     # Get tracks from the playlist
#     results = sp.playlist_tracks(playlist_id)
#     tracks = results['items']
    
#     # Keep fetching tracks until we have them all
#     while results['next']:
#         results = sp.next(results)
#         tracks.extend(results['items'])
    
#     # Extract track names and artists, and then shuffle
#     all_tracks = [(track['track']['name'], track['track']['artists'][0]['name'], track['track']['uri']) for track in tracks if track['track']]
#     random.shuffle(all_tracks)
    
#     # Return the specified number of random songs
#     return all_tracks[:num_songs]