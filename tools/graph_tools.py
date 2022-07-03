import matplotlib.pyplot as plt
import geopandas as gpd
import networkx as nx
import numpy as np

def distance_matrix(geoPick: gpd.GeoDataFrame,geoDrop: gpd.GeoDataFrame):
    gpick = geoPick.to_crs('EPSG:5234')
    gdrop = geoDrop.to_crs('EPSG:5234')
    pick_drop_origin = gpick.distance(gdrop)/1000
    pick_drop_origin = pick_drop_origin.to_list()
    print(pick_drop_origin)
    pick_drop_not_origin = []
    pick_pick_origin = []
    drop_drop_origin = []
    for i in range(gpick.shape[0]):
        for j in range(gdrop.shape[0]):
            if i!=j:
                pick_drop_not_origin.append(gpick.geometry[i].distance(gdrop.geometry[j])/1000)
    for i in range(gpick.shape[0]):
            pick_pick_origin.append(gpick.geometry[i].distance(gpick.geometry[(i+1)%gpick.shape[0]])/1000)
    
    for i in range(gdrop.shape[0]):
        drop_drop_origin.append(gdrop.geometry[i].distance(gdrop.geometry[(i+1)%gdrop.shape[0]])/1000)
    
    return pick_drop_origin,pick_drop_not_origin,pick_pick_origin, drop_drop_origin

def graph_points_matrix(g_pick: gpd.GeoDataFrame,g_drop: gpd.GeoDataFrame):
    pck_drp , pck_ndrp , pck_pck, drp_drp = distance_matrix(g_pick,g_drop)
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
            matrix_graph[4][(i*2)%4] = pck_pck[i]
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
                matrix[i][j] = 0.00001

def cleanDropPick(matrix):
    r = 0
    for i in range(3):
        matrix[i+1+r][i+r] = 0
        r=r+1
    return matrix

def get_sub(x): 
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    sub_s = "ₐ₈CDₑբGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥwₓᵧZₐ♭꜀ᑯₑբ₉ₕᵢⱼₖₗₘₙₒₚ૧ᵣₛₜᵤᵥwₓᵧ₂₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"
    x = str(x)
    res = x.maketrans(''.join(normal), ''.join(sub_s)) 
    return x.translate(res)

def graph_points_net(g_pick,g_drop,spring=False):
    ady_graph = graph_points_matrix(g_pick,g_drop)
    refineZeroPoint(ady_graph)
    ady_graph = cleanDropPick(ady_graph)
    point_graph = nx.from_numpy_matrix(ady_graph, create_using=nx.DiGraph())
    label_mapping = {
        0: f'pick{get_sub(1)}', 
        1: f'drop{get_sub(1)}', 
        2: f'pick{get_sub(2)}',
        3: f'drop{get_sub(2)}',
        4: f'pick{get_sub(3)}',
        5: f'drop{get_sub(3)}'
        }
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

def get_graph_mat(g_pick,g_drop):
    coords = []
    for i in range(3):
        #print("pick")
        coords.append([g_pick['geometry'][i].x,g_pick['geometry'][i].y])
        #print("drop")
        coords.append([g_drop['geometry'][i].x,g_drop['geometry'][i].y])            
    dist_mat = graph_points_matrix(g_pick,g_drop)
    return np.array(coords), dist_mat

def graph_points_matrix_sec(g_pick,g_drop,sol):
    matrix_graph = graph_points_matrix(g_pick,g_drop)
    sec_vec = []
    for i in range(len(sol)):
        if i<len(sol)-1:
            sec_vec.append([sol[i],sol[i+1]])
    ady_r = np.zeros((6,6))
    refineZeroPoint(matrix_graph)
    for k in sec_vec:
        ady_r[k[0]][k[1]] = matrix_graph[k[0]][k[1]]

    return ady_r

def solutionGraph(sol=[],ady_graph=[]):
    for i in range(ady_graph.shape[0]):
        for j in range(ady_graph.shape[0]):
            if i not in sol:
                ady_graph[i][j]=0
                ady_graph[j][i]=0
    return ady_graph

def graph_points_net(g_pick,g_drop,sol=[],spring=False):
    ady_graph = graph_points_matrix_sec(g_pick,g_drop,sol)    
    #solutionGraph2(sol,ady_graph)
    point_graph = nx.from_numpy_matrix(ady_graph, create_using=nx.DiGraph())
    label_mapping = {
        0: f'pick{get_sub(1)}', 
        1: f'drop{get_sub(1)}', 
        2: f'pick{get_sub(2)}',
        3: f'drop{get_sub(2)}',
        4: f'pick{get_sub(3)}',
        5: f'drop{get_sub(3)}'
    }
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