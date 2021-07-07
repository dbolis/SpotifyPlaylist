from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import main
from requests import Request, post
from .access import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI



# Create your views here.

# User logs into their account. Redirects to URI and returns access code
def auth(request):
    scopes = "playlist-modify-public playlist-modify-private playlist-read-private user-library-read user-read-private"

    url = Request('GET', "https://accounts.spotify.com/authorize", params={
        'scope':scopes,
        'response_type':'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID

    }).prepare().url

    return redirect(url)

# Landing page
def login(request):
    return render(request, 'login.html') 

# track feature selection page. Access code is saved in hidden input field
def select(request):

    code = request.GET.get('code')
    error = request.GET.get('error')

    return render(request, 'select.html',{"code":code, "error":error}) 



def success(request):
    
    # get access code
    code = request.POST.get('code', False)

    # check if code not valid and redirect to login again if so 
    if code == "None" or not code:
        return redirect("login")
    
    # get access token
    response = post("https://accounts.spotify.com/api/token", data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()
 
    
    access_token = response.get("access_token")
    token_type = response.get("token_type")

    # if access token == None (happnes when you try to use access code twice)
    if access_token==None:
        return redirect("login")

    # user selected song features

    playlistName = request.POST["name"]
    playlistLength = int(request.POST["playlistLength"])

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

    user_features = {"dance": [dance_l, dance_m, dance_h], 
                "energy": [energy_l, energy_m, energy_h],
                "acoustic": [acoustic_l, acoustic_m, acoustic_h], 
                "instrument": [instrument_l, instrument_m, instrument_h],
                "valence": [valence_l, valence_m, valence_h], 
                "length": [length_l, length_m, length_h]}
    
    # create spotifyObject

    spotifyObject=main.SaveSongs(playlistLength,playlistName, user_features)

    # add access token to object
    spotifyObject.call_refresh(access_token)
    
    # run playlist generator 
    spotifyObject.find_songs()

    # if access is denied, redirect to login
    if spotifyObject.error:
        return redirect("login")

    # if at least one song found for specs return success message, otherwise return ask to expand ranges
    if spotifyObject.get_status():
        return render(request, 'success.html', {"status":"Success! '"+playlistName+"' has been created.","subtext":"Check your Spotify App!","color":"border-success"})
    else:
        return render(request, 'success.html', {"status":"No tracks fit your specified ranges!","subtext":"Expand your ranges and try again.","color":"border-danger"})