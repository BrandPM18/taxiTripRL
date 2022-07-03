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
