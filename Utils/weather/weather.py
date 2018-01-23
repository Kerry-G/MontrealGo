import urllib
import json
import math 
import sys
sys.path.append('../..')
from config import weatherAPI, APPID
# from  import weatherAPI, APPID

#give a city, return a dict with all the info
def receiveWeather(city):
    fp = None
    try:
        fp = urllib.request.urlopen(weatherAPI + "?q=" + city + "&units=metric" + APPID)
        mybytes = fp.read()
        encoding = fp.info().get_content_charset('utf-8')
        my_json = json.loads(mybytes.decode(encoding))
    except:
        return "Oops, I don't know that country, can you try again?"
    return toString(my_json)



#give a lattitude and a longitude, return a dict with all the info
def receiveWeatherFromLatLon(lat,lon):
    fp = None
    try:
        fp = urllib.request.urlopen(weatherAPI + "?lat=" + str(lat) +"&lon=" + str(lon) + "&units=metric" + APPID)
        mybytes = fp.read()
        encoding = fp.info().get_content_charset('utf-8')
        my_json = json.loads(mybytes.decode(encoding))
    except:
        return "Oops, I don't know that country, can you try again?"
    return toString(my_json)

def toString(my_json):
    ans = {}
    ans["location"] = my_json["name"]
    ans["country"] = my_json["sys"]["country"]
    ans["weather"] = my_json["weather"][0]["description"]
    ans["temp"] = my_json["main"]["temp"]
    ans["humidity"] = my_json["main"]["humidity"]
    ans["wind"] = my_json["wind"]["speed"]
    ans["sunrise"] = my_json["sys"]["sunrise"]
    ans["sunset"] = my_json["sys"]["sunset"]
    ans_str = "The condition in " + ans["location"] + " (" + ans["country"] + ")"+ " is " + ans["weather"] + ". The temperature is " \
              + str(int (math.floor(ans["temp"]))) + " degrees Celcius. The humidity level is " \
              + str(ans["humidity"]) + "%. The wind speed is " + str(ans["wind"]) +" m/s."
    return ans_str

