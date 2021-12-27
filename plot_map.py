import folium


def plot_points(map_view,gf_pick,gf_drop):
    for i in range(gf_pick.shape[0]):
        map_view.add_child(folium.Marker(location = [gf_pick.geometry[i].y,gf_pick.geometry[i].x],
                            popup =
                            "ID: " + str(i)+ '<br>' +
                            "Community: " + str(gf_pick['Pickup Community Area'][i]) + '<br>',
                            icon = folium.Icon(color = "blue")))
        map_view.add_child(folium.Marker(location = [gf_drop.geometry[i].y,gf_drop.geometry[i].x],
                            popup =
                            "ID: " + str(i)+ '<br>' +
                            "Community: " + str(gf_drop['Dropoff Community Area'][i]) + '<br>',
                            icon = folium.Icon(color = "red")))


def plot_edge(map_view,gf_pick,gf_drop):
    for i in range(gf_pick.shape[0]):
        hi = [(gf_pick.geometry[i].y,gf_pick.geometry[i].x)]
        hi.append((gf_drop.geometry[i].y,gf_drop.geometry[i].x))
        print(str(gf_pick.geometry[i])+' --> ' + str(gf_drop.geometry[i]))
        folium.PolyLine(hi,
                        color='skyblue',
                        weight=7,
                        opacity=0.6).add_to(map_view)
        hj = []
        for j in range(gf_drop.shape[0]):
            if i!=j:
                hj = [(gf_pick.geometry[i].y,gf_pick.geometry[i].x)]
                hj.append((gf_drop.geometry[j].y,gf_drop.geometry[j].x))
                print(str(gf_pick.geometry[i])+' --> ' + str(gf_drop.geometry[j]))
                folium.PolyLine(hj,
                    color='pink',
                    weight=7,
                    opacity=0.6).add_to(map_view)
        print(str(gf_pick.geometry[i])+' --> ' + str(gf_pick.geometry[(i+1)%gf_pick.shape[0]]))
        hz = [(gf_pick.geometry[i].y,gf_pick.geometry[i].x)]
        hz.append((gf_pick.geometry[(i+1)%gf_pick.shape[0]].y,gf_pick.geometry[(i+1)%gf_pick.shape[0]].x))
        folium.PolyLine(hz,
                        color='yellow',
                        weight=7,
                        opacity=0.6).add_to(map_view)
    for k in range(gf_drop.shape[0]):
        hk = [(gf_drop.geometry[k].y,gf_drop.geometry[k].x)]
        hk.append((gf_drop.geometry[(k+1)%gf_drop.shape[0]].y,gf_drop.geometry[(k+1)%gf_drop.shape[0]].x))
        print(str(gf_drop.geometry[k])+' --> ' + str(gf_drop.geometry[(k+1)%gf_drop.shape[0]]))
        folium.PolyLine(hk,
            color='purple',
            weight=7,
            opacity=0.6).add_to(map_view)