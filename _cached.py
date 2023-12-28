# client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# def replace_spaces_in_genres(genres_list):
#     return [genre.replace(" ", "_") for genre in genres_list]

# def get_random_song_from_each_playlist(sp, playlist_ids):
#     selected_tracks = []
#     featureLIST = []
#     for playlist_id in playlist_ids:
#         results = sp.playlist_tracks(playlist_id)
#         print("Sppppp")
#         tracks = results['items']
        
#         while results['next']:
#             results = sp.next(results)
#             tracks.extend(results['items'])
        
#         if tracks:
#             chosen_track = random.choice(tracks)
#             if chosen_track['track']:
#                 track_name = chosen_track['track']['name']
#                 track_uri = chosen_track['track']['id']
#                 audio_features = sp.audio_features(track_uri)[0]
#                 # features = sp.audio_features(track_uri)[0]

#                 # Fetch track details
#                 track_details = sp.track(track_uri)
#                 artist_id = track_details["artists"][0]["id"]
#                 track_name = track_details["name"]
#                 track_pop = track_details["popularity"]

#                 # Fetch artist details
#                 artist_details = sp.artist(artist_id)
#                 artist_name = artist_details["name"]
#                 artist_pop = artist_details["popularity"]
#                 artist_genres = artist_details["genres"]

#                 # Compile the desired information
#                 track_info = {
#                     "artist_name": artist_name,
#                     "id": track_uri,
#                     "track_name": track_name,
#                     "artist_pop": artist_pop,
#                     "genres": artist_genres,
#                     "track_pop": track_pop,
#                     "danceability": audio_features["danceability"],
#                     "energy": audio_features["energy"],
#                     "key": audio_features["key"],
#                     "loudness": audio_features["loudness"],
#                     "mode": audio_features["mode"],
#                     "speechiness": audio_features["speechiness"],
#                     "acousticness": audio_features["acousticness"],
#                     "instrumentalness": audio_features["instrumentalness"],
#                     "liveness": audio_features["liveness"],
#                     "valence": audio_features["valence"],
#                     "tempo": audio_features["tempo"],
#                     "time_signature": audio_features["time_signature"],
#                     "genres_list": artist_genres
#                 }
#                 featureLIST.append(track_info)
#                 selected_tracks.append({'name': track_name, 'spotify_id': track_uri})


#     return selected_tracks, featureLIST


# top_albums_id = ["37i9dQZF1DXcBWIGoYBM5M", "37i9dQZEVXbMDoHDwVN2tF", "37i9dQZF1DX0XUsuxWHRQd",
#                  "37i9dQZF1DX10zKzsJ2jva", "37i9dQZF1DWXRqgorJj26U", "37i9dQZF1DWY7IeIP1cdjF",
#                  "37i9dQZF1DX4o1oenSJRJd", "37i9dQZF1DWWMOmoXKqHTD", "37i9dQZF1DX4UtSsGT1Sbe", 
#                  "37i9dQZF1DX76Wlfdnj7AP", "37i9dQZF1DX4WYpdgoIcn6", "37i9dQZF1DX186v583rmzp", 
#                  "37i9dQZF1DXbTxeAdrVG2l", "37i9dQZF1DX08mhnhv6g9b", "37i9dQZF1DX3rxVfibe1L0",
#                  "37i9dQZF1DX1lVhptIYRda", "37i9dQZF1DXdSjVZQzv2tl", "37i9dQZF1DX4sWSpwq3LiO",
#                  "0vvXsWCC9xrXsKd4FyS8kM", "37i9dQZF1DXdxcBWuJkbcy", "37i9dQZF1DX6aTaZa0K6VA",
#                  "37i9dQZF1DWY4xHQp97fN6", "37i9dQZF1DX4SBhb3fqCJd", "37i9dQZF1DXdPec7aLTmlC",
#                  "37i9dQZF1DX1rVvRgjX59F", "37i9dQZF1DXcF6B6QPhFDv", "37i9dQZF1DXbrUpGvoi3TS",
#                  "37i9dQZF1DWWGFQLoP9qlv", "1nRNXjzFAF5uKK1586mfSZ", "00qcmuVkchZsWn3Sp4pFTJ"]





# diverse_songs, featureLIST = get_random_song_from_each_playlist(sp, top_albums_id)
# print("Diverse Songs")



# featureDF = pd.DataFrame(featureLIST)
# print("FeatureDF")
# print(featureDF.shape)
# print(featureDF.columns)
# featureDF['genres_list'] = featureDF['genres_list'].apply(replace_spaces_in_genres) 



# float_cols = featureDF.dtypes[featureDF.dtypes == 'float64'].index.values

# my_pl = create_feature_set(featureDF, float_cols=float_cols)

# print("Steem")
# my_db = pd.read_csv("complete_feature_final.csv")

# common_features = list(set(my_pl.columns) & set(my_db.columns))

# print("common_features")
# print(common_features)
    


# recommendations, rec_list = make_recommendations(my_pl, my_db, top_n=5)

# # Print recommendations for each song
# for song_id, recs in recommendations.items():
#     print(f"Recommendations for song ID {song_id}: {recs}")



# artist_name	
# id	
# track_name	
# artist_pop	
# genres	
# track_pop	
# danceability	
# energy	
# key	
# loudness	
# mode	
# speechiness	
# acousticness	
# instrumentalness	
# liveness	
# valence	
# tempo	
# time_signature	
# genres_list	
# subjectivity	
# polarity







# from sklearn.decomposition import PCA
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np


# def generate_playlist_feature(complete_feature_set, playlist_test):
    
#     complete_feature_set_playlist = complete_feature_set[complete_feature_set['id'].isin(playlist_test['id'].values)]
    
    
#     complete_feature_set_nonplaylist = complete_feature_set[~complete_feature_set['id'].isin(playlist_test['id'].values)]
#     #complete_feature_set_playlist_final = complete_feature_set_playlist.drop(columns = "id")

#     return complete_feature_set_playlist, complete_feature_set_nonplaylist


# complete_feature_set = pd.read_csv("complete_feature_final.csv")
# # print(complete_feature_set.shape)

# complete_feature_set_playlist, complete_feature_set_nonplaylist = generate_playlist_feature(complete_feature_set, featureDF)

# # print(complete_feature_set_playlist.shape)
# # # print(complete_feature_set_playlist.columns)
# # print(complete_feature_set_nonplaylist.shape)
# # # print(complete_feature_set_nonplaylist.columns)

# def make_recommendations(complete_feature_set_playlist, complete_feature_set_nonplaylist, n_components):
#     pca = PCA(n_components=n_components)
#     playlist_PCA = pca.fit_transform(complete_feature_set_playlist.drop(columns="id"))
#     features_PCA = pca.transform(complete_feature_set_nonplaylist.drop(columns="id"))

#     similarity_matrix = cosine_similarity(playlist_PCA, features_PCA)
    
#     top_n = 30 // n_components
#     if n_components > 30:
#         top_n = 2

#     # Initialize an empty DataFrame to store recommendations
#     recommendations_df = pd.DataFrame()
#     recommendations = []

#     # Iterate over each row (existing song) in the similarity matrix
#     for i in range(len(playlist_PCA)):
#         # Get the indices of the top N similar songs
#         top_indices = np.argsort(similarity_matrix[i])[-top_n:]

#         # Get the song information for the top recommended songs
#         recommended_songs = complete_feature_set_nonplaylist.iloc[top_indices]

#         # Append the recommendations to the DataFrame
#         recommendations.append(recommended_songs)
    
#     recommendations_df = pd.concat(recommendations, ignore_index=True)
    
    
#     return recommendations_df
    
# recommendation1 = make_recommendations(complete_feature_set_playlist, complete_feature_set_nonplaylist, n_components = complete_feature_set_playlist.shape[0])
# print(recommendation1['id'])




# def ari_to_features(ari):
#     # Fetch audio features

#     features = sp.audio_features(ari)[0]

#     # Fetch track details
#     track_details = sp.track(ari)
#     artist_id = track_details["artists"][0]["id"]
#     track_name = track_details["name"]
#     track_pop = track_details["popularity"]

#     # Fetch artist details
#     artist_details = sp.artist(artist_id)
#     artist_name = artist_details["name"]
#     artist_pop = artist_details["popularity"]
#     artist_genres = artist_details["genres"]

#     # Compile the desired information
#     track_info = {
#         "artist_name": artist_name,
#         "id": ari,
#         "track_name": track_name,
#         "artist_pop": artist_pop,
#         "genres": artist_genres,
#         "track_pop": track_pop,
#         "danceability": features["danceability"],
#         "energy": features["energy"],
#         "key": features["key"],
#         "loudness": features["loudness"],
#         "mode": features["mode"],
#         "speechiness": features["speechiness"],
#         "acousticness": features["acousticness"],
#         "instrumentalness": features["instrumentalness"],
#         "liveness": features["liveness"],
#         "valence": features["valence"],
#         "tempo": features["tempo"],
#         "time_signature": features["time_signature"],
#         "genres_list": artist_genres
#     }

#     return track_info

