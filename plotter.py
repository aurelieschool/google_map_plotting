import pandas as pd
import folium 
import json
import googlemaps
import requests

with open("Records.json") as f:
    data = json.load(f)

df = pd.json_normalize(data, 'locations', errors='ignore')
# removing activity (temporarily) because it's a pain
df_clean = df.loc[:, df.columns!='activity']
df_clean = df.dropna(axis=1)

# taking the first 10000 data points
head = df_clean.head(10000)

### PART 1: DISPLAYING LOCATIONS ON MAP ###

lat = head['latitudeE7']
long = head['longitudeE7']

# googles coordinate system multiplies all the numbers by 10^7 from standard GPS
multiplier = 10000000
lat_min = (lat.min() / multiplier)
lat_max = (lat.max() / multiplier)
long_min = (long.min() / multiplier)
long_max = (long.max() / multiplier)

m = folium.Map()
m.fit_bounds([[lat_min, long_min], [lat_max, long_max]])

for x, y in zip(lat, long):
    folium.Marker(location=[(x / multiplier), (y / multiplier)]).add_to(m)

m.save("map.html")

### PART 2: LISTING THE NAMES OF LIKELY BUSINESSES AND ADDRESSES ###

api_key = 'AIzaSyBc-EYEQItR7_r04TjfbYj7tmO5rZP-aLY'
url = ''

smallhead = df_clean.head(10)
small_lat = smallhead['latitudeE7']
small_lon = smallhead['longitudeE7']

places = {}

for x, y in zip(small_lat, small_lon):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={x/multiplier},{y/multiplier}&key={api_key}'
    try: 
        response = requests.get(url) # turn this into a try catch
        data = response.json()
        first_result = data['results'][0]
        formatted_address = first_result['formatted_address']

        if (formatted_address in places):
            places[formatted_address] += 1
        else:
            places[formatted_address] = 1
    except:
        print("error: couldn't get data for location")
    '''data = response.json()
    first_result = data['results'][0]
    formatted_address = first_result['formatted_address'] # append to a new list rather than just printing it out as u go along, that way u can check if it's in there & also print them all at once
    # make a dictionary of key value pairs, where the key is the address and the value is the number of times you've visited'''

for p in places:
    print(f'Place: {p}, times visited: {places[p]}')
# TODO: how many times visited – very complicated :((
# TODO: add them as popups to the map1!!

