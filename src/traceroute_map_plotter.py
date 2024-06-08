import folium

def plot_route(locations):
    #cream o harta folium
    map_obj = folium.Map(location=[0,0], zoom_start=2)

    #marcam fiecare locatie in lista
    for location in locations:
        lat, lon = location['latitude'], location['longitude']
        info = f"{location['city']}, {location['region']}, {location['country']}"
        folium.Marker(location=[lat,lon], popup=info).add_to(map_obj)

    #salvam harta intr un fisier Html
    map_obj.save('route_map.html')

    print("Map saved as 'route_map.html'")
