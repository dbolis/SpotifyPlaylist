from django.shortcuts import render
from django.http import HttpResponse
from . import main



# Create your views here.




def index(request):

    
    return render(request, 'index.html',{"name":39}) 

def success(request):
    
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
    
    spotifyObject.call_refresh()
    # a.get_user_playlists()
    spotifyObject.find_songs()
    print(spotifyObject.get_status())

    if spotifyObject.get_status():
        return render(request, 'success.html', {"status":"Success! '"+playlistName+"' has been created.","subtext":"Check your Spotify App!","color":"border-success"})
    else:
        return render(request, 'success.html', {"status":"No tracks fit your specified ranges!","subtext":"Expand your ranges and try again.","color":"border-danger"})