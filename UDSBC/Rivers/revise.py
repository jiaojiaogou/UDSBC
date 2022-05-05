import pandas as pd
import numpy as np

def river_revise(connect_file,out_file):
    data = pd.read_csv(connect_file)
    COMID = data['COMID']
    maxup = data['maxup']
    for i in range(len(COMID)):
        data['maxup'][i]=0
        if data['upid1'][i] !=0:
            data['maxup'][i] +=1
        if data['upid2'][i] !=0:
            data['maxup'][i] +=1
        if data['upid3'][i] !=0:
            data['maxup'][i] +=1
        if data['upid4'][i] !=0:
            data['maxup'][i] +=1
    data.to_csv(out_file,index=False)
    return

