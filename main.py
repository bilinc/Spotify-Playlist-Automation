'''
1. Log into YouTube
2. Find our liked videos
3. Create a Spotify playlist
4. Search for the liked songs
5. Add this song to the new Spotify playlist
'''
import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl
from spotify_secrets import spotify_user_id, spotify_OAuth_token

class CreatePlaylist:

	def __init__(self):
		self.user_id = spotify_user_id
		self.auth_token = spotify_OAuth_token
		self.get_youtube_client= self.get_youtube_client()
		self.all_song_info = {}


	# 1. Log into YouTube
	def get_youtube_client(self):
		# copied from YouTube Data PI

		# Disable OAuthlib's HTTPS verification when running locally.
		# *DO NOT* leave this option enabled in production.
		os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

		api_service_name = "youtube"
		api_version = "v3"
		client_secrets_file = "client_secret.json"

		# Get credentials and create an API client
		scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
		flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
			client_secrets_file, scopes)
		credentials = flow.run_console()

		# from the Youtube DATA API
		youtube_client = googleapiclient.discovery.build(
			api_service_name, api_version, credentials=credentials)

		return youtube_client

	# 2. Find our liked videos and creating a dictionary of important song information
	def get_liked_videos(self):
		requests = self.youtube_client.videos().list(
			part="snippet,contentDetails,statistics",
			myRating="like"
		)
		response = request.execute()

		# collect each video and get important information
		for item in response["items"]:
			video_title = item["snippet"]["title"]
			youtube_url = "https://www.youtube.com/watch?v{}".format(item["id"])

			# use youtube_dl to collect song & artist name
			video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)

			song_name = video["track"]
			artist = video["artist"]

			# save all important info
			self.all_song_info[video_title]={
				"youtube_url": youtube_url,
				"song_name": song_name,
				"artist": artist,

				# add the uri,
				"spotify_uri": self.get_spotify_uri(song_name, artist)
			}


	# 3. Create a Spotify playlist
	def create_playlist(self):
		
		request_body = json.dumps({
			"name": "Youtube Liked Videos",
			"description": "All Liked YouTube Videos",
			"public": True
		})
		
		query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
		response = requests.post(
			query,
			data=request_body,
			headers={
				"Authorization": "Bearer {}".format(self.auth_token),
				"Content-Type": "application/json"
			}
		)
		response_json = response.json()

		# playlist id
		return response_json["id"]

	# 4. Search for the liked songs in spotify
	def get_spotify_uri(self, song_name, artist):
		
		query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
			song_name,
			artist
		)
		response = requests.get(
			query,
			headers={
				"Content-Type": "application/json",
				"Authorization": "Bearer {}".format(self.auth_token)
			}
		)
		response_json = response.json()
		songs = response_json["tracks"]["items"]

		uri = songs[0]["uri"]

		return uri


	# 5. Add like song to the new Spotify playlist
	def add_song_to_playlist(self, song_name, artist):
		# populate our songs dictionary
		pass
		#

if __name__ == '__main__':
	my_app = CreatePlaylist()

	'''Test 1 - Creating playlists in spotify'''
	# my_playlist = my_app.create_playlist()
	# print(my_playlist)

	'''Test 2 - search for songs'''
	my_song = my_app.get_spotify_uri("Sugar", "Maroon 5")
	print(my_song)

	'''Test 3 - test youtube client authorization'''
	# my_yt_client = my_app.get_youtube_client()
	# print(my_yt_client)