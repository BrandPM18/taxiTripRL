import geopandas as gpd
import numpy as np
from sqlalchemy import create_engine
import networkx as nx
import folium


def sql_pickup(count,offset,start='',id = ''):
    start_time=''
    trip_id = ''
    query = ''
    it = 0
    if start!='':
        start_time = r' "Trip Start Timestamp" LIKE'  + f" '%{start}%' "
        it = it + 1
    if id!= '':
        trip_id = r' "Trip ID" =  ' + f" '{id}' "
        it = it + 1
    if it>1:
        query = f'WHERE {trip_id} AND {start_time}'        
    elif it!=0:
        query = f'WHERE {trip_id} {start_time}'
    return f'SELECT \"Pickup Community Area\",\"geometry\" FROM public.pickup_points {query} LIMIT {count} OFFSET {offset}'

def sql_dropoff(count,offset,start='',id = ''):
    start_time=''
    trip_id = ''
    query = ''
    it = 0
    if start!='':
        start_time = r' "Trip Start Timestamp" LIKE'  + f" '%{start}%' "
        it = it + 1
    if id!= '':
        trip_id = r' "Trip ID" =  ' + f" '{id}' "
        it = it + 1
    if it>1:
        query = f'WHERE {trip_id} AND {start_time}'        
    elif it!=0:
        query = f'WHERE {trip_id} {start_time}'

    return f'SELECT \"Dropoff Community Area\",\"geometry\" FROM public.dropoff_points  {query} LIMIT {count} OFFSET {offset}'

def sql_area(count,offset,id = 0):
    area_num = ''
    if id!=0:
        area_num = f'WHERE \"AREA_NUMBE\" = {id}'
        
    return f'SELECT \"AREA_NUMBE\",\"COMMUNITY\",\"geometry\" FROM commun_area {area_num} LIMIT {count} OFFSET {offset}'

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
    type_color = ["green","skyblue","orange", "pink","silver","maroon","olive"]
    for i in range(gf_pick.shape[0]):
        hi = [(gf_pick.geometry[i].y,gf_pick.geometry[i].x)]
        hi.append((gf_drop.geometry[i].y,gf_drop.geometry[i].x))
        print(str(gf_pick.geometry[i])+' --> ' + str(gf_drop.geometry[i]))
        folium.PolyLine(hi,
                        color=type_color[i%9],
                        weight=7,
                        opacity=0.6).add_to(map_view)
        hj = []
        for j in range(gf_drop.shape[0]):
            if i!=j:
                hj = [(gf_pick.geometry[i].y,gf_pick.geometry[i].x)]
                hj.append((gf_drop.geometry[j].y,gf_drop.geometry[j].x))
                print(str(gf_pick.geometry[i])+' --> ' + str(gf_drop.geometry[j]))
                folium.PolyLine(hj,
                    color='purple',
                    weight=7,
                    opacity=0.6).add_to(map_view)

        print(str(gf_pick.geometry[i])+' --> ' + str(gf_pick.geometry[(i+1)%gf_pick.shape[0]]))
        hz = [(gf_pick.geometry[i].y,gf_pick.geometry[i].x)]
        hz.append((gf_pick.geometry[(i+1)%gf_pick.shape[0]].y,gf_pick.geometry[(i+1)%gf_pick.shape[0]].x))
        folium.PolyLine(hz,
                        color='yellow',
                        weight=7,
                        opacity=0.6).add_to(map_view)
        
def distan_matrix(geoPick,geoDrop):
    gpick = geoPick.to_crs('EPSG:5234')
    gdrop = geoDrop.to_crs('EPSG:5234')
    pick_drop_origin = gpick.distance(gdrop)/1000
    pick_drop_origin = pick_drop_origin.to_list()
    pick_drop_norigin = []
    pick_pick_origin = []
    for i in range(gpick.shape[0]):
        for j in range(gdrop.shape[0]):
            if i!=j:
                # print(str(gpick.geometry[i])+' --> ' + str(gdrop.geometry[j]))
                pick_drop_norigin.append(gpick.geometry[i].distance(gdrop.geometry[j])/1000)
    for i in range(gpick.shape[0]):
            #print(str(gpick.geometry[i])+' --> ' + str(gpick.geometry[(i+1)%gpick.shape[0]]))
            pick_pick_origin.append(gpick.geometry[i].distance(gpick.geometry[(i+1)%gpick.shape[0]])/1000)
            
    return pick_drop_origin,pick_drop_norigin,pick_pick_origin


def graph_points_matrix(g_pick,g_drop):
    pck_drp , pck_ndrp , pck_pck = distan_matrix(g_pick,g_drop)
    matrix_graph = np.zeros((6,6))
    r = 0
    for i in range(len(pck_drp)):
        matrix_graph[i+1+r][i+r] = pck_drp[i]
        r=r+1
    for i in range(len(pck_ndrp)):
        if i <= 1:
            #print(2*i+3)
            matrix_graph[2*i+3][0] = pck_ndrp[i]
        elif i <= 3:
            #print(i+2*(i%2))
            matrix_graph[i+2*(i%2)][i-1] = pck_ndrp[i]
        else:
            #print((i%2)*2+1)
            matrix_graph[4][(i%2)*2+1] = pck_ndrp[i]
    for i in range(len(pck_pck)):
        if i == 0:
            matrix_graph[2][(i%2)] = pck_pck[i]
        else:
            matrix_graph[4][(i%2)] = pck_pck[i]            
    return matrix_graph + matrix_graph.T

def graph_points_net(g_pick,g_drop):
    point_graph = nx.from_numpy_matrix(graph_points_matrix(g_pick,g_drop), create_using=nx.DiGraph())
    label_mapping = {0: f'pick{get_sub(1)}', 
                     1: f'drop{get_sub(1)}', 
                     2: f'pick{get_sub(2)}',
                     3: f'drop{get_sub(2)}',
                     4: f'pick{get_sub(3)}',
                     5: f'drop{get_sub(3)}'}
    pick_label = [
    f'pick{get_sub(1)}',
    f'pick{get_sub(2)}',
    f'pick{get_sub(3)}'
    ]

    drop_label = [
        f'drop{get_sub(1)}',
        f'drop{get_sub(2)}',
        f'drop{get_sub(3)}'
    ]
    point_graph = nx.relabel_nodes(point_graph, label_mapping)
    labels = nx.get_edge_attributes(point_graph, "weight")
    pos = nx.circular_layout(point_graph,scale=10)
    print(pos)
    fig, ax = plt.subplots(figsize=(15, 14))
    options = {"edgecolors": "tab:gray", "node_size": 4000, "alpha": 0.9}
    nx.draw(point_graph,pos=pos,**options,arrowsize=20)
    nx.draw_networkx_nodes(point_graph, pos, nodelist=pick_label, node_color="tab:green", **options)
    nx.draw_networkx_nodes(point_graph, pos, nodelist=drop_label, node_color="tab:red", **options)
    nx.draw_networkx_edges(point_graph,pos = pos, width=2, alpha=0.5)
    nx.draw_networkx_edge_labels(point_graph,pos = pos,edge_labels=labels,font_size=13)
    nx.draw_networkx_labels(point_graph, pos, font_size=20, font_color="whitesmoke")
    plt.show()