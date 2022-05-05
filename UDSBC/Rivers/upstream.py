## 1. Count the level of gauges
## 2. Sout the gauges by level
## 3. Automatic bias correction from upstreams to downstreams at monthly scale
## 4. Take each gauge delta Q added to downstreams  
## 5. Bias correction for the ungauged river at monthly scale
## 6. Bias scale mapping at daily scle 
## Input: fast_connectivity1.csv; Qout_61_18_daily.nc, Qmon.nc, Qbc_61_18_daily.nc, Qbc_month.nc
##        gauge_id.csv; Q_obs.csv.
## Output: revised Qbc_month.nc and Qbc_61_18_daily.nc
## writed by Jiaojiao Gou   2021-05-26

import pandas as pd
import numpy as np

def find_upstream(river,connet_file):
    connect = pd.read_csv(connet_file)
    COMID = connect['COMID']
    maxup = connect['maxup']
    init = river
    river1=[]
    river1.append(river)
    index = 0
    while True:
        k = np.where(COMID == river)[0][0]
        p=maxup[k]
        if p!=0 :
            for m in range(p):
                name = 'upid'+str(m+1)
                river1.append(connect[name][k])
        index= index+1
        if index==len(river1):
            break
        else:
            river = river1[index]
    river1.remove(init)
    return river1




