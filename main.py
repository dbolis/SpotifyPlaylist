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
        self.features=""
        self.new_playlist_id=""

    def find_songs(self):
        print("Finding Songs")

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(DJ_playlist)

        response = requests.get(query,
        headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.spotify_token)})

        response_json = response.json()
        
        for i in response_json["items"]:
            self.tracks += (i["track"]["id"] + ",")
        self.tracks = self.tracks[:-1]
        
        print(self.tracks)  
        
        self.get_song_features()

    def get_song_features(self):
        
        print("Getting Track Feautres")

        query = "https://api.spotify.com/v1/audio-features?{}".format("ids=" + self.tracks)

        response = requests.get(query,
        headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.spotify_token)})

        self.features = response.json()["audio_features"]
        print(self.features)

        self.filter('n','n','n','n','n','n')


    def filter(self, dance, energy, acoustic, instrumental, valence, tempo):

        inputs = [dance, energy, acoustic, instrumental, valence]
        ranges = [] # [dance, energy, acoustic, instrumental, valance, tempo]
        for i in inputs:
            if i == "l":
                ranges.append([0,0.33])
            elif i == "m":
                ranges.append([0.33,0.66])
            elif i == "h":
                ranges.append([0.66,1])
            else:
                ranges.append([0,1])

        if tempo == "l":
            ranges.append([0,90])
        elif tempo == "m":
            ranges.append([90,125])
        elif tempo == "h":
            ranges.append([125,200])
        else:
            ranges.append([0,200])


        print(ranges)
        print(self.features)
        print(len(self.features))
        for track in self.features:
            print(track["id"])
            print("danceability: " + str(track["danceability"]))
            print("energy: " + str(track["energy"]))
            print("acousticness: " + str(track["acousticness"]))
            print("instrumentalness: " + str(track["instrumentalness"]))
            print("valence: " + str(track["valence"]))
            print("tempo: " + str(track["tempo"]))
            print("--------")

        out = ""
        for track in self.features:
            if ranges[0][0]<=track["danceability"]<=ranges[0][1] and ranges[1][0]<=track["energy"]<=ranges[1][1] and \
            ranges[2][0]<=track["acousticness"]<=ranges[2][1] and ranges[3][0]<=track["instrumentalness"]<=ranges[3][1] and \
            ranges[4][0]<=track["valence"]<=ranges[4][1] and ranges[5][0]<=track["tempo"]<=ranges[5][1]:

                out += track["uri"] + ","

        out = out[:-1]
        print (out)
        self.tracks=out

        self.add_to_playlist()

    def create_playlist(self):
        print("creating playlist")
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)

        request_body = json.dumps({
            "name": "playlist name",
            "description": "test playlist",
            "public": True
        })

        response = requests.post(query, data=request_body,  headers={
            "Content-Type": "application/json", 
            "Authorization": "Bearer {}".format(self.spotify_token)
        })
            
        response_json = response.json()
        return response_json["id"]

    def add_to_playlist(self):

        self.new_playlist_id = self.create_playlist()
        print(self.tracks)
        print(self.new_playlist_id)
        query ="https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(self.new_playlist_id, self.tracks)

        response = requests.post(query,  headers={
            "Content-Type": "application/json", 
            "Authorization": "Bearer {}".format(self.spotify_token)
        })
    
        print(response.json)

    def call_refresh(self):
        refreshCaller = Refresh()

        self.spotify_token = refreshCaller.refresh()

    
        


a=SaveSongs()
a.call_refresh()
a.find_songs()


