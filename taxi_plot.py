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
    for i in range(tb_pick.shape[0]):
        hi = [(tb_pick.geometry[i].y,tb_pick.geometry[i].x)]
        hi.append((tb_drop.geometry[i].y,tb_drop.geometry[i].x))
        print(str(tb_pick.geometry[i])+' --> ' + str(tb_drop.geometry[i]))
        folium.PolyLine(hi,
                        color=type_color[i%9],
                        weight=7,
                        opacity=0.6).add_to(map_view)
        hj = []
        for j in range(tb_drop.shape[0]):
            if i!=j:
                hj = [(tb_pick.geometry[i].y,tb_pick.geometry[i].x)]
                hj.append((tb_drop.geometry[j].y,tb_drop.geometry[j].x))
                print(str(tb_pick.geometry[i])+' --> ' + str(tb_drop.geometry[j]))
                folium.PolyLine(hj,
                    color='pink',
                    weight=7,
                    opacity=0.6).add_to(map_view)
        print(str(tb_pick.geometry[i])+' --> ' + str(tb_pick.geometry[(i+1)%tb_pick.shape[0]]))
        hz = [(tb_pick.geometry[i].y,tb_pick.geometry[i].x)]
        hz.append((tb_pick.geometry[(i+1)%tb_pick.shape[0]].y,tb_pick.geometry[(i+1)%tb_pick.shape[0]].x))
        folium.PolyLine(hz,
                        color='yellow',
                        weight=7,
                        opacity=0.6).add_to(map_view)
    for k in range(tb_drop.shape[0]):
        hk = [(tb_drop.geometry[k].y,tb_drop.geometry[k].x)]
        hk.append((tb_drop.geometry[(k+1)%tb_drop.shape[0]].y,tb_drop.geometry[(k+1)%tb_drop.shape[0]].x))
        print(str(tb_drop.geometry[k])+' --> ' + str(tb_drop.geometry[(k+1)%tb_drop.shape[0]]))
        folium.PolyLine(hk,
            color='purple',
            weight=7,
            opacity=0.6).add_to(map_view)
        
def distan_matrix(geoPick,geoDrop):
    gpick = geoPick.to_crs('EPSG:5234')
    gdrop = geoDrop.to_crs('EPSG:5234')
    pick_drop_origin = gpick.distance(gdrop)/1000
    pick_drop_origin = pick_drop_origin.to_list()
    pick_drop_norigin = []
    pick_pick_origin = []
    drop_drop_origin = []
    for i in range(gpick.shape[0]):
        for j in range(gdrop.shape[0]):
            if i!=j:
                pick_drop_norigin.append(gpick.geometry[i].distance(gdrop.geometry[j])/1000)
    for i in range(gpick.shape[0]):
            pick_pick_origin.append(gpick.geometry[i].distance(gpick.geometry[(i+1)%gpick.shape[0]])/1000)
    
    for i in range(gdrop.shape[0]):
        drop_drop_origin.append(gdrop.geometry[i].distance(gdrop.geometry[(i+1)%gdrop.shape[0]])/1000)
    
    return pick_drop_origin,pick_drop_norigin,pick_pick_origin, drop_drop_origin


def graph_points_matrix(g_pick,g_drop):
    pck_drp , pck_ndrp , pck_pck, drp_drp = distan_matrix(g_pick,g_drop)
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
    for i in range(len(drp_drp)):
        if i == 0:
            matrix_graph[3][i+1] = drp_drp[i]
        else:
            matrix_graph[5][(2%(i+1))+1] = drp_drp[i]
            
    return matrix_graph + matrix_graph.T 

def refineZeroPoint(matrix):
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if i!=j and matrix[i][j]==0:
                matrix[i][j] = 0.0000001

def get_sub(x): 
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    sub_s = "ₐ₈CDₑբGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥwₓᵧZₐ♭꜀ᑯₑբ₉ₕᵢⱼₖₗₘₙₒₚ૧ᵣₛₜᵤᵥwₓᵧ₂₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"
    x = str(x)
    res = x.maketrans(''.join(normal), ''.join(sub_s)) 
    return x.translate(res)

def graph_points_net(g_pick,g_drop,spring=False):
    ady_graph = graph_points_matrix(g_pick,g_drop)
    refineZeroPoint(ady_graph)
    point_graph = nx.from_numpy_matrix(ady_graph, create_using=nx.DiGraph())
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
    if spring:
        pos = nx.spring_layout(point_graph,scale=100)
    else:
        pos = nx.circular_layout(point_graph,scale=10)

    fig, ax = plt.subplots(figsize=(15, 14))
    options = {"edgecolors": "tab:gray", "node_size": 4000, "alpha": 0.9}
    nx.draw(point_graph,pos=pos,**options,arrowsize=20)
    nx.draw_networkx_nodes(point_graph, pos, nodelist=pick_label, node_color="tab:green", **options)
    nx.draw_networkx_nodes(point_graph, pos, nodelist=drop_label, node_color="tab:red", **options)
    nx.draw_networkx_edges(point_graph,pos = pos, width=2, alpha=0.5)
    nx.draw_networkx_edge_labels(point_graph,pos = pos,edge_labels=labels,font_size=13)
    nx.draw_networkx_labels(point_graph, pos, font_size=20, font_color="whitesmoke")
    plt.show()