import json
import requests

from secrets import spotify_user_id, DJ_playlist
from refresh import Refresh

class SaveSongs:
    def __init__(self):
        self.spotify_user_id = spotify_user_id
        self.spotify_token = ""
        self.DJ_playlist = DJ_playlist
        self.tracks = ""

    def find_songs(self):
        print("Finding Songs")

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(DJ_playlist)

        response = requests.get(query,
        headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.spotify_token)})

        response_json = response.json()
        print(response)
        out = []
        for i in response_json["items"]:
            self.tracks += (i["track"]["uri"] + ",")
        self.tracks = self.tracks[:-1]
        
        print(self.tracks)  
        
        

    def call_refresh(self):
        refreshCaller = Refresh()

        self.spotify_token = refreshCaller.refresh()

    
        


a=SaveSongs()
a.call_refresh()
a.find_songs()

