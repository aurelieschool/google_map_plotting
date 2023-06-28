import pandas as pd
import folium
import json
import googlemaps
import requests

### COMBINING THE TWO PARTS OF PLOTTER ###

## loading in the file and cleaning the data ##

with open('Records.json') as f:
        data = json.load(f)

df = pd.json_normalize(data, 'locations', errors='ignore')
df_clean = df.loc[:, df.columns!='activity'] # removing activity (temporarily) because it's a pain
df_clean = df.dropna(axis=1)

head = df_clean.head(100000)

lat = head['latitudeE7']
long = head['longitudeE7']

## getting the number of times gone to each place & their formatted address ## 

api_key = 'AIzaSyBc-EYEQItR7_r04TjfbYj7tmO5rZP-aLY'
url = ''

places = {}
latlong_cache = {}

multiplier = 10000000
lat_min = (lat.min() / multiplier)
lat_max = (lat.max() / multiplier)
long_min = (long.min() / multiplier)
long_max = (long.max() / multiplier)

m = folium.Map()
m.fit_bounds([[lat_min, long_min], [lat_max, long_max]])

# make a list of markers
# update them as neccessary 
# make a dictionary of format {'formatted address': [[latitude, longitude], times visited ]}
# at each 

for x, y in zip(lat, long):

    if ((x / multiplier, y / multiplier) in latlong_cache):
        addr = latlong_cache[((x / multiplier),(y / multiplier))]
        places[addr][1] += 1
    else:
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={x/multiplier},{y/multiplier}&key={api_key}'
        try: 
            response = requests.get(url)
            data = response.json()
            first_result = data['results'][0]
            formatted_address = first_result['formatted_address']
            
            latlong_cache[((x / multiplier), (y / multiplier))] = formatted_address
            places[formatted_address] = [[(x / multiplier), (y / multiplier)], 1]
        except:
            print("error: couldn't get data for location")

for p in places:
    mk = folium.Marker(places[p][0], popup = folium.Popup(f'{p} \n Number of visits: {places[p][1]}'))
    mk.add_to(m)

m.save("map.html")

