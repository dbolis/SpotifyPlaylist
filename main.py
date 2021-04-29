import json
import requests
import random

from secrets import spotify_user_id, DJ_playlist, tommy_user_id
from refresh import Refresh

class SaveSongs:
    def __init__(self, max_playlist_length):
        self.spotify_user_id = spotify_user_id
        self.spotify_token = ""
        self.DJ_playlist = DJ_playlist
        self.tommy_user_id = tommy_user_id
        self.tracks = []
        self.new_tracks=[]
        self.features=""
        self.new_playlist_id=""
        self.header = ""
        self.max_playlist_length = max_playlist_length

    def find_songs(self):
        print("Finding Songs")
        
        tracks=[]
        
        ## get playlists 

        queryPlaylists = "https://api.spotify.com/v1/users/{}/playlists?limit={}".format(self.spotify_user_id,50) # fix limit
        responsePlaylists = requests.get(queryPlaylists, headers=self.header)
        

        for playlist in responsePlaylists.json()["items"]:
            print(playlist["name"])
            
            queryPlaylistTracks = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist["id"])

            responsePlaylistTracks = requests.get(queryPlaylistTracks, headers=self.header)
            print(responsePlaylistTracks)
            for track in responsePlaylistTracks.json()["items"]:
                
                tracks.append(track["track"]["id"])


        ## get albums

        queryAlbums = "https://api.spotify.com/v1/me/albums?limit={}".format(50)
        responseAlbums = requests.get(queryAlbums, headers=self.header) # add limit
        print(responseAlbums)
        
        for album in responseAlbums.json()["items"]:

            for track in album["album"]["tracks"]["items"]:
                tracks.append(track["id"])
                
            
        ## get saved tracks
        offset = 50
        querySavedTracks = "https://api.spotify.com/v1/me/tracks?limit={}".format(50)

        responseSavedTracks = requests.get(querySavedTracks,headers=self.header) 
        print(responseSavedTracks)
        
        for track in responseSavedTracks.json()["items"]:
            tracks.append(track["track"]["id"])
            
        total = responseSavedTracks.json()["total"]
        print(total)
        while total-offset>0:
            print(total-offset)
            querySavedTracks = "https://api.spotify.com/v1/me/tracks?limit={}&offset={}".format(50,offset)

            responseSavedTracks = requests.get(querySavedTracks,headers=self.header) 

            for track in responseSavedTracks.json()["items"]:
                tracks.append(track["track"]["id"])
                print(track["track"]["name"])
            offset+=50 
            
        

        tracks = set(tracks)
        
        if None in tracks:
            tracks.remove(None)
        tracks=list(tracks)

        self.tracks=tracks
        
        # tracks_str = ""
        # for i in range(99):
        #     tracks_str += (tracks[i] + ",")
        # tracks_str = tracks_str[:-1]
        

        # self.tracks = tracks_str

        # print(len(self.tracks), self.tracks)
        # response = requests.get(query,
        # headers=self.header)

        # response_json = response.json()
        
        # for i in response_json["items"]:
        #     self.tracks += (i["track"]["id"] + ",")
        # self.tracks = self.tracks[:-1]
        
        # print(self.tracks)  
        
        self.get_song_features()

    def get_user_playlists(self):
        print("getting public playlists")

        query = "https://api.spotify.com/v1/users/{}/playlists?limit={}".format(self.spotify_user_id,50)

        response = requests.get(query, headers=self.header)


        print(response.json())

    def get_song_features(self):
        
        print("Getting Track Feautres")
        features = []
        i=0
        while i<len(self.tracks):
            tracks_str = ""
            if len(self.tracks)-i<99:
                remain = len(self.tracks)-i
            else:
                remain = 99

            for j in range(i,i+remain):
                tracks_str += (self.tracks[j] + ",")
            tracks_str = tracks_str[:-1]


            query = "https://api.spotify.com/v1/audio-features?{}".format("ids=" + tracks_str)

            response = requests.get(query, headers=self.header)

            features += response.json()["audio_features"]
            i+=99
            print("while loop", i)
        
        clean_features = [] # get rid of None
        for feature in features:
            if feature != None:
                clean_features.append(feature)
        
        self.features = clean_features

        self.filter('n','n','m','n','m','m')


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


        # print(ranges)
        # print(self.features)
        # print(len(self.features))
        # for track in self.features:
        #     print(track["id"])
        #     print("danceability: " + str(track["danceability"]))
        #     print("energy: " + str(track["energy"]))
        #     print("acousticness: " + str(track["acousticness"]))
        #     print("instrumentalness: " + str(track["instrumentalness"]))
        #     print("valence: " + str(track["valence"]))
        #     print("tempo: " + str(track["tempo"]))
        #     print("--------")

        out = []
        for track in self.features:
            if ranges[0][0]<=track["danceability"]<=ranges[0][1] and ranges[1][0]<=track["energy"]<=ranges[1][1] and \
            ranges[2][0]<=track["acousticness"]<=ranges[2][1] and ranges[3][0]<=track["instrumentalness"]<=ranges[3][1] and \
            ranges[4][0]<=track["valence"]<=ranges[4][1] and ranges[5][0]<=track["tempo"]<=ranges[5][1]:

                out.append(track["uri"])


        self.new_tracks=out
        
        self.add_to_playlist()

    def create_playlist(self):
        print("creating playlist")
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)

        request_body = json.dumps({
            "name": "New Playlist",
            "description": "test playlist",
            "public": True
        })

        response = requests.post(query, data=request_body,  headers=self.header)
            
        response_json = response.json()
        return response_json["id"]

    def add_to_playlist(self):

        self.new_playlist_id = self.create_playlist()
        
        if len(self.new_tracks)>self.max_playlist_length:
            self.new_tracks = random.sample(self.new_tracks, self.max_playlist_length) # need to require user input to be max 100!
        


        query ="https://api.spotify.com/v1/playlists/{}/tracks".format(self.new_playlist_id)

        request_body = json.dumps({
            "uris":self.new_tracks
        })
        response = requests.post(query, data=request_body, headers=self.header)
        
        print(len(self.new_tracks))
        print(response)
        print(self.max_playlist_length)

    def call_refresh(self):
        refreshCaller = Refresh()

        self.spotify_token = refreshCaller.refresh()
        self.header = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.spotify_token)}

    
        


a=SaveSongs(20)
a.call_refresh()
a.get_user_playlists()
# a.find_songs()


