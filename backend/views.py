from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from . import main
from requests import Request, post
from .access import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI



# Create your views here.
def auth(request):
    scopes = "playlist-modify-public playlist-modify-private playlist-read-private user-library-read user-read-private"

    url = Request('GET', "https://accounts.spotify.com/authorize", params={
        'scope':scopes,
        'response_type':'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID

    }).prepare().url

    return redirect(url)


def login(request):
    return render(request, 'login.html') 


def select(request):

    code = request.GET.get('code')
    error = request.GET.get('error')

    return render(request, 'select.html',{"code":code, "error":error}) 



def success(request):
    
    code = request.POST.get('code', False)

    
    if code == "None" or not code:
        return redirect("login")
    
    
    response = post("https://accounts.spotify.com/api/token", data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()
    
    

    
    
    access_token = response.get("access_token")
    token_type = response.get("token_type")

    if access_token==None:
        return redirect("login")

    print("--------------------")
    print(access_token)
    print("--------------------")
    print(token_type)
    print("--------------------")
    
    

    playlistName = request.POST["name"]
    playlistLength = int(request.POST["playlistLength"])

    print(playlistLength)



    dance_l = request.POST["dance_l"]
    dance_m = request.POST["dance_m"]
    dance_h = request.POST["dance_h"]

    energy_l = request.POST["energy_l"]
    energy_m = request.POST["energy_m"]
    energy_h = request.POST["energy_h"]
    
    acoustic_l = request.POST["acoustic_l"]
    acoustic_m = request.POST["acoustic_m"]
    acoustic_h = request.POST["acoustic_h"]

    instrument_l = request.POST["instrument_l"]
    instrument_m = request.POST["instrument_m"]
    instrument_h = request.POST["instrument_h"]

    valence_l = request.POST["valence_l"]
    valence_m = request.POST["valence_m"]
    valence_h = request.POST["valence_h"]

    length_l = request.POST["length_l"]
    length_m = request.POST["length_m"]
    length_h = request.POST["length_h"]

    if dance_l=="0" and dance_m=="0" and dance_h=="0":
        dance_l,dance_m,dance_h = "1","1","1"

    if energy_l=="0" and energy_m=="0" and energy_h=="0":
        energy_l,energy_m,energy_h = "1","1","1"

    if acoustic_l=="0" and acoustic_m=="0" and acoustic_h=="0":
        acoustic_l,acoustic_m,acoustic_h = "1","1","1"

    if instrument_l=="0" and instrument_m=="0" and instrument_h=="0":
        instrument_l,instrument_m,instrument_h = "1","1","1"

    if valence_l=="0" and valence_m=="0" and valence_h=="0":
        valence_l,valence_m,valence_h = "1","1","1"

    if length_l=="0" and length_m=="0" and length_h=="0":
        length_l,length_m,length_h = "1","1","1"                

    print([playlistName, dance_l, dance_m, dance_h, energy_l, energy_m, energy_h,\
        acoustic_l, acoustic_m, acoustic_h, instrument_l, instrument_m, instrument_h, \
        valence_l, valence_m, valence_h, length_l, length_m, length_h])

    user_features = {"dance": [dance_l, dance_m, dance_h], 
                "energy": [energy_l, energy_m, energy_h],
                "acoustic": [acoustic_l, acoustic_m, acoustic_h], 
                "instrument": [instrument_l, instrument_m, instrument_h],
                "valence": [valence_l, valence_m, valence_h], 
                "length": [length_l, length_m, length_h]}
    
    

    spotifyObject=main.SaveSongs(playlistLength,playlistName, user_features)
    spotifyObject.call_refresh(access_token)
    
    

    

    
    # print(spotifyObject.get_status())

    # if not spotifyObject.get_status():
    #     return redirect("login")

    spotifyObject.find_songs()

    if spotifyObject.error:
        return redirect("login")

    

    if spotifyObject.get_status():
        return render(request, 'success.html', {"status":"Success! '"+playlistName+"' has been created.","subtext":"Check your Spotify App!","color":"border-success"})
    else:
        return render(request, 'success.html', {"status":"No tracks fit your specified ranges!","subtext":"Expand your ranges and try again.","color":"border-danger"})