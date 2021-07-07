import json
import requests
import random

# from .refresh import Refresh


class SaveSongs:
    def __init__(self, max_playlist_length, playlist_name, user_features):
        self.spotify_user_id = ""
        self.spotify_token = ""
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
        print("finding songs")

        # get user id 
        queryUserId = "https://api.spotify.com/v1/me"
        
        responseUserId = requests.get(queryUserId, headers=self.header)

        # if access denied (response not in 200-299) exit function and Views.py redirects to login
        if not responseUserId.ok:
            self.error = True
            return False


        self.spotify_user_id = responseUserId.json()["id"]

        tracks=[]
        
        # get playlists 

        queryPlaylists = "https://api.spotify.com/v1/users/{}/playlists?limit={}".format(self.spotify_user_id,50) # fix limit
        responsePlaylists = requests.get(queryPlaylists, headers=self.header)
        

        # get tracks in playlists
        for playlist in responsePlaylists.json()["items"]:
            
            
            queryPlaylistTracks = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist["id"])

            responsePlaylistTracks = requests.get(queryPlaylistTracks, headers=self.header)
            
            for track in responsePlaylistTracks.json()["items"]:
                
                tracks.append(track["track"]["id"])


        # get albums

        queryAlbums = "https://api.spotify.com/v1/me/albums?limit={}".format(50)
        responseAlbums = requests.get(queryAlbums, headers=self.header) # add limit
        
        
        # get tracks in albums
        for album in responseAlbums.json()["items"]:

            for track in album["album"]["tracks"]["items"]:
                tracks.append(track["id"])
                
            
        # get saved tracks
        offset = 50
        querySavedTracks = "https://api.spotify.com/v1/me/tracks?limit={}".format(50)

        responseSavedTracks = requests.get(querySavedTracks,headers=self.header) 
        
        # loop through until all saved tracks found (can only return 50 at a time)
        
        for track in responseSavedTracks.json()["items"]:
            tracks.append(track["track"]["id"])
            
        total = responseSavedTracks.json()["total"]
        while total-offset>0:
            querySavedTracks = "https://api.spotify.com/v1/me/tracks?limit={}&offset={}".format(50,offset)

            responseSavedTracks = requests.get(querySavedTracks,headers=self.header) 

            for track in responseSavedTracks.json()["items"]:
                tracks.append(track["track"]["id"])
                
            offset+=50 
            
        # delete duplicates and create hash map

        tracks = set(tracks)
        
        if None in tracks:
            tracks.remove(None)
        tracks=list(tracks)

        self.tracks=tracks
        
        self.get_song_features()


    def get_song_features(self):
        
        # get track features (100 at a time)
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
            
        
        clean_features = [] # get rid of None
        for feature in features:
            if feature != None:
                clean_features.append(feature)
        
        self.features = clean_features

        self.filter(self.user_features)


    def filter(self, inputs):

        print("filtering songs")
        ranges = [] # [dance, energy, acoustic, instrumental, valance, length]
        
        # define ranges for spotify features
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

        # match spotify feature ranges to user inputed ranges
        for feature in inputs:
            for i in range(0,3):
                if inputs[feature][i]=="1":
                    ranges.append(rangeDict[feature][i])
                else:
                    ranges.append([0,0])

        out = []

        # filter tracks (intersection of all selected track features for each song)
        for track in self.features:
            if (ranges[0][0]<=track["danceability"]<=ranges[0][1] or ranges[1][0]<=track["danceability"]<=ranges[1][1] or ranges[2][0]<=track["danceability"]<=ranges[2][1]) and \
            (ranges[3][0]<=track["energy"]<=ranges[3][1] or ranges[4][0]<=track["energy"]<=ranges[4][1] or ranges[5][0]<=track["energy"]<=ranges[5][1]) and \
            (ranges[6][0]<=track["acousticness"]<=ranges[6][1] or ranges[7][0]<=track["acousticness"]<=ranges[7][1] or ranges[8][0]<=track["acousticness"]<=ranges[8][1]) and \
            (ranges[9][0]<=track["instrumentalness"]<=ranges[9][1] or ranges[10][0]<=track["instrumentalness"]<=ranges[10][1] or ranges[11][0]<=track["instrumentalness"]<=ranges[11][1]) and \
            (ranges[12][0]<=track["valence"]<=ranges[12][1] or ranges[13][0]<=track["valence"]<=ranges[13][1] or ranges[14][0]<=track["valence"]<=ranges[14][1]) and \
            (ranges[15][0]<=track["duration_ms"]<=ranges[15][1] or ranges[16][0]<=track["duration_ms"]<=ranges[16][1] or ranges[17][0]<=track["duration_ms"]<=ranges[17][1]):
                
                out.append(track["uri"])

        self.new_tracks=out
        
        if len(self.new_tracks)!=0:
            self.add_to_playlist()

    def create_playlist(self):
        print("creating playlist")

        # create playlist
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.spotify_user_id)

        request_body = json.dumps({
            "name": self.playlist_name,
            "description": "",
            "public": True
        })

        response = requests.post(query, data=request_body,  headers=self.header)
            
        response_json = response.json()
        return response_json["id"]

    def add_to_playlist(self):

        #create new playlist and add tracks to it

        self.new_playlist_id = self.create_playlist()

        # select random songs if more songs available than user specified length
        
        if len(self.new_tracks)>self.max_playlist_length:
            self.new_tracks = random.sample(self.new_tracks, self.max_playlist_length) # need to require user input to be max 100!
        

        query ="https://api.spotify.com/v1/playlists/{}/tracks".format(self.new_playlist_id)

        request_body = json.dumps({
            "uris":self.new_tracks
        })
        response = requests.post(query, data=request_body, headers=self.header)
        
        self.status = True

    def get_status(self):
        return self.status

    def call_refresh(self,access_token):
        # add new access token

        # refreshCaller = Refresh()

        # self.spotify_token = refreshCaller.refresh()
        self.spotify_token = access_token
        self.header = {"Content-Type": "application/json", "Authorization": "Bearer "+ self.spotify_token}


    
        


# a=SaveSongs(20)
# a.call_refresh()
# a.get_user_playlists()
# a.find_songs()


