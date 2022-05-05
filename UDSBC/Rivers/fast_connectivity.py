## This fast connectivity script was developted by Lin et al. (2019). ref by Lin, P. R., et al. Global Reconstruction 
## of Naturalized River Flows at 2.94 Million Reaches. Water Resour. Res. 55: 6499–6516 (2019).
## This script generate RAPID connectivity file in a fast way
## Input file: river flowline shapefiles

import geopandas as gpd
import pandas as pd
import numpy as np
import pdb
from shapely.geometry import Point

def connectivity(line_file,out_file):
    print("ok1")
    #read line shapefile
    print("ok2")
    d = gpd.read_file(line_file)

    print('**** File '+line_file+' *****')
    lines = d['geometry'][:]

    linecoords = lines[0].coords[:]
    npt = len(linecoords)
    point1 = Point(linecoords[npt-1])
    point2 = Point(linecoords[0])
    print(point1)
    print(point2)
    fromnode = []
    tonode = []
    fromnode.append(str(point1.x)+','+str(point1.y))
    tonode.append(str(point2.x)+','+str(point2.y))
    print(fromnode)
    print(tonode)

    fromnode = []
    tonode = []
    print('... generating fromnode and tonode ...')
    for line in lines:
        #calculate actual length in km (multiple points)
        linecoords = line.coords[:]
        npt = len(linecoords)
        #calculate direct length in km (two points)
        point1 = Point(linecoords[npt-1])
        point2 = Point(linecoords[0])
        fromnode.append(str(point1.x)+','+str(point1.y))
        tonode.append(str(point2.x)+','+str(point2.y))
    d['fromnode'] = fromnode
    d['tonode'] = tonode
        
    #creating renamed DataFrame for calculating NextDownID
    print('--- creating DataFrame for NextDownID ---')
    df1 = d[['COMID','fromnode','tonode']]
    df2 = d[['COMID', 'fromnode']].copy().rename(columns={'COMID':'NextID','fromnode': 'tonode'})
    print('--- merging to find NextDownID ---')
    df_id = pd.merge(df1,df2,how='left',on='tonode') #merge
    df_id.fillna(0,inplace=True) #fill missing
    df_id.drop(['fromnode','tonode'],axis=1,inplace=True)
    df_id['NextID'] = df_id['NextID'].astype(int) #convert to integer

    #for calculating upstream IDs
    print('--- finding upids ---')
    df3 = df_id[['COMID','NextID']].copy()
    df4 = df_id[['COMID','NextID']].copy().rename(columns={'COMID': 'fromID','NextID':'COMID'})
    df_final = pd.merge(df3, df4, how='left', on='COMID')
    df_final.fillna(0,inplace=True)
    df_final['fromID'] = df_final['fromID'].astype(int)
    grouped = df_final.groupby(['COMID','NextID'])
    upid = grouped['fromID'].apply(lambda x: pd.Series(x.values[0:4])).unstack()
    nup = len(upid.columns)
    upid = upid.rename(columns={iup: 'upid{}'.format(iup + 1) for iup in range(nup)})
    upid.fillna(0,inplace=True)
    for iup in range(nup):
        upid['upid'+str(iup+1)] = upid['upid'+str(iup+1)].astype(int)
    for iup in range(nup,4):
        upid['upid'+str(iup+1)] = 0

    upid['maxup'] = grouped['fromID'].count()
    upid['maxup'][upid['maxup']==1] = 0
    tomerge = upid.reset_index()
    print('--- final merging ---')
    final = d[['COMID']].merge(tomerge[['COMID','NextID','maxup','upid1','upid2','upid3','upid4']],on='COMID',how='left')
    print('--- writing to csv file... wait ... ---')
    final.to_csv(out_file,index=False)
    return
