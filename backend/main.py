import json
import requests
import random

from .secrets import spotify_user_id, DJ_playlist, tommy_user_id
from .refresh import Refresh
from django.shortcuts import render, redirect

class SaveSongs:
    def __init__(self, max_playlist_length, playlist_name, user_features):
        self.spotify_user_id = ""
        self.spotify_token = ""
        self.DJ_playlist = DJ_playlist
        self.tommy_user_id = tommy_user_id
        self.tracks = []
        self.new_tracks=[]
        self.features=""
        self.new_playlist_id=""
        self.header = ""
        self.max_playlist_length = max_playlist_length
        self.playlist_name = playlist_name
        self.user_features = user_features
        self.status = False
        self.error = False

    def find_songs(self):

        queryUserId = "https://api.spotify.com/v1/me"
        
        responseUserId = requests.get(queryUserId, headers=self.header)

        

        if not responseUserId.ok:
            self.error = True
            return False


        

        self.spotify_user_id = responseUserId.json()["id"]

        print("Finding Songs")
        
        tracks=[]
        
        ## get playlists 

        queryPlaylists = "https://api.spotify.com/v1/users/{}/playlists?limit={}".format(self.spotify_user_id,50) # fix limit
        responsePlaylists = requests.get(queryPlaylists, headers=self.header)
        
        print(responsePlaylists)

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

        self.filter(self.user_features)


    def filter(self, inputs):

        # inputs = [dance, energy, acoustic, instrumental, valence]
        ranges = [] # [dance, energy, acoustic, instrumental, valance, length]
        # for i in inputs[:-1]:
        #     if i == "l":
        #         ranges.append([0,0.33])
        #     elif i == "m":
        #         ranges.append([0.33,0.66])
        #     elif i == "h":
        #         ranges.append([0.66,1])
        #     else:
        #         ranges.append([0,1])

        # if inputs[5] == "l": # Song length
        #     ranges.append([0,90000])
        # elif inputs[5] == "m":
        #     ranges.append([90000,300000])
        # elif inputs[5] == "h":
        #     ranges.append([300000,3000000])
        # else:
        #     ranges.append([0,3000000])


        rangeDict = {
            "dance":{
                    0:[0,0.33],
                    1:[0.33,0.66],
                    2:[0.66,1]
                },
                    
            "energy":{
                    0:[0,0.33],
                    1:[0.33,0.66],
                    2:[0.66,1]
                },
            "acoustic":{
                    0:[0,0.33],
                    1:[0.33,0.66],
                    2:[0.66,1]
                },
            "instrument":{
                    0:[0,0.33],
                    1:[0.33,0.66],
                    2:[0.66,1]
                },
            "valence":{
                    0:[0,0.33],
                    1:[0.33,0.66],
                    2:[0.66,1]
                },
            "length":{
                    0:[0,90000],
                    1:[90000,300000],
                    2:[300000,3000000]
                }
        }

        for feature in inputs:
            for i in range(0,3):
                if inputs[feature][i]=="1":
                    ranges.append(rangeDict[feature][i])
                else:
                    ranges.append([0,0])


        print(ranges)
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
            if (ranges[0][0]<=track["danceability"]<=ranges[0][1] or ranges[1][0]<=track["danceability"]<=ranges[1][1] or ranges[2][0]<=track["danceability"]<=ranges[2][1]) and \
            (ranges[3][0]<=track["energy"]<=ranges[3][1] or ranges[4][0]<=track["energy"]<=ranges[4][1] or ranges[5][0]<=track["energy"]<=ranges[5][1]) and \
            (ranges[6][0]<=track["acousticness"]<=ranges[6][1] or ranges[7][0]<=track["acousticness"]<=ranges[7][1] or ranges[8][0]<=track["acousticness"]<=ranges[8][1]) and \
            (ranges[9][0]<=track["instrumentalness"]<=ranges[9][1] or ranges[10][0]<=track["instrumentalness"]<=ranges[10][1] or ranges[11][0]<=track["instrumentalness"]<=ranges[11][1]) and \
            (ranges[12][0]<=track["valence"]<=ranges[12][1] or ranges[13][0]<=track["valence"]<=ranges[13][1] or ranges[14][0]<=track["valence"]<=ranges[14][1]) and \
            (ranges[15][0]<=track["duration_ms"]<=ranges[15][1] or ranges[16][0]<=track["duration_ms"]<=ranges[16][1] or ranges[17][0]<=track["duration_ms"]<=ranges[17][1]):
                
                out.append(track["uri"])
        # for track in self.features:
        #     if ranges[0][0]<=track["danceability"]<=ranges[0][1] and ranges[1][0]<=track["energy"]<=ranges[1][1] and \
        #     ranges[2][0]<=track["acousticness"]<=ranges[2][1] and ranges[3][0]<=track["instrumentalness"]<=ranges[3][1] and \
        #     ranges[4][0]<=track["valence"]<=ranges[4][1] and ranges[5][0]<=track["duration_ms"]<=ranges[5][1]:

        #         out.append(track["uri"])



        print(out, len(out))
        self.new_tracks=out
        
        if len(self.new_tracks)!=0:
            self.add_to_playlist()

    def create_playlist(self):
        print("creating playlist")
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)

        request_body = json.dumps({
            "name": self.playlist_name,
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

        self.status = True

    def get_status(self):
        return self.status

    def call_refresh(self,access_token):
        # refreshCaller = Refresh()

        # self.spotify_token = refreshCaller.refresh()
        self.spotify_token = access_token
        self.header = {"Content-Type": "application/json", "Authorization": "Bearer "+ self.spotify_token}
        print(self.header)
        print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiii")

    
        


# a=SaveSongs(20)
# a.call_refresh()
# a.get_user_playlists()
# a.find_songs()


