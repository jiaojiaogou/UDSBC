## this script writed to caculate the Gof (goodness of fit) of the GS streamflow data 
## writed by Jiaojiao Gou   2022-05-05

import os
import math
import string
import numpy as np
import pandas as pd
import xarray as xr
from UDSBC.util import filter_nan
from UDSBC.Postprocess import gof_index

## read station position 

station = pd.read_csv('./input/gauge_id.csv')['station']
gauge_id = pd.read_csv('./input/gauge_id.csv')['gaugeid']

# read obs

obs = np.empty([480,len(gauge_id)])
obs_file = pd.read_csv("./input/Q_obs.csv")
for i in range(len(gauge_id)):
    obs[:,i] = obs_file[station[i]]

# read Qout simulation

Qout = xr.open_dataset('./output/Qbc_month1.nc').load()['qout']
Rivers = xr.open_dataset('./output/Qmon.nc').load()['rivers']
sim = np.empty([480,len(gauge_id)])

for i in range(len(gauge_id)):
    k = np.where(Rivers == gauge_id[i])[0][0]
    sim[:,i] = Qout[0:480,k]

# cal gof

gof = np.empty([len(gauge_id),10])

for i in range(len(gauge_id)):
    s1,o1 = filter_nan(sim[0:480,i], obs[0:480,i])   #0:108 108:228 0:228
    if len(o1) == 0:
        gof[i,:] = 'NaN'
    else:
        gof[i,0] = gof_index.pc_bias(s1, o1)
        gof[i,1] = gof_index.apb(s1, o1)
        gof[i,2] = gof_index.rmse(s1, o1)
        gof[i,3] = gof_index.mae(s1, o1)
        gof[i,4] = gof_index.bias(s1, o1)
        gof[i,5] = gof_index.NS(s1, o1)
        gof[i,6] = gof_index.L(s1, o1, N=5)
        gof[i,7] = gof_index.correlation(s1, o1)
        gof[i,8] = gof_index.index_agreement(s1, o1)
        gof[i,9] = gof_index.KGE(s1, o1)[0]
np.savetxt("./output/gof1.csv",gof,delimiter=',')
