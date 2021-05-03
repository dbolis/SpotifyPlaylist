from django.shortcuts import render
from django.http import HttpResponse
from . import main



# Create your views here.




def index(request):

    
    return render(request, 'index.html',{"name":39}) 

def success(request):
    
    playlistName = request.POST["name"]

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

    valance_l = request.POST["valance_l"]
    valance_m = request.POST["valance_m"]
    valance_h = request.POST["valance_h"]

    length_l = request.POST["length_l"]
    length_m = request.POST["length_m"]
    length_h = request.POST["length_h"]

    print([playlistName, dance_l, dance_m, dance_h, energy_l, energy_m, energy_h,\
        acoustic_l, acoustic_m, acoustic_h, instrument_l, instrument_m, instrument_h, \
        valance_l, valance_m, valance_h, length_l, length_m, length_h])

    # user_features = [dance, energy, acoustic, instrumental, valance, length]
    
    

    # a=main.SaveSongs(50,playlistName, user_features)
    
    # a.call_refresh()
    # # a.get_user_playlists()
    # a.find_songs()
    return render(request, 'success.html')