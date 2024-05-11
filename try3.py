import geopy.geocoders
from geopy.geocoders import Nominatim
geolocator=Nominatim(user_agent="geoapiexercises")
place=input("enter city name")
location=geolocator.geocode(place)
print(location)