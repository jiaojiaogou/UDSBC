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

import os
import pandas as pd
import xarray as xr
import numpy as np
from UDSBC.Q_pre import Qmonth
from UDSBC.Rivers import fast_connectivity,revise,upstream,downstream
from UDSBC.util import filter_nan
from UDSBC.BC import EQM,SDM


############### input_output_file ###############

river_shp = './input/liao.shp'
basin_id = './input/basin_id.csv'
rapid_Qout = './input/Qout.nc'
gauge_file = './input/gauge_id.csv'
obs_file = './input/Q_obs.csv'

river_connect = './output/fast_connectivity.csv'
river_connect1 = './output/fast_connectivity1.csv'
Q_daily_file = './output/Qout_61_18_daily.nc'
Q_month_file = './output/Qmon.nc'
bc_daily_file = './output/Qbc_61_18_daily.nc'
bc_monthly_file = './output/Qbc_month.nc'

############### creat_Qfile ###############
Qmonth.creat_Q(basin_id,rapid_Qout,Q_daily_file,Q_month_file)
sysComm1 = "cdo monmean ./output/Qout_61_18_daily.nc ./output/Qmon.nc"
os.system(sysComm1)

############### creat_Qbcfile ###############
sysComm2 = "cp ./output/Qout_61_18_daily.nc ./output/Qbc_61_18_daily.nc"
sysComm3 = "cp ./output/Qmon.nc ./output/Qbc_month.nc"
os.system(sysComm2)
os.system(sysComm3)

############### River_connet ###############
fast_connectivity.connectivity(river_shp,river_connect)
revise.river_revise(river_connect,river_connect1)

############### BC producer ##############

Qout_m = xr.open_dataset(Q_month_file).load()['qout'] ##original
Rivers = xr.open_dataset(Q_month_file).load()['rivers']
dates = xr.open_dataset(Q_month_file).load()['time']
Qbc_m = xr.open_dataset(Q_month_file).load()['qout']   ##need to BC

print('**** Read gauges file *****')
gauges =  pd.read_csv(gauge_file)

#### count the gauges level ###
print('**** Count the gauges level *****')
gauge_level = np.empty(len(gauges['gaugeid']))
for i in range(len(gauge_level)):
    uprivers = upstream.find_upstream(gauges['gaugeid'][i],river_connect1)
    gauge_level[i] = len(list(set(uprivers).intersection(set(gauges['gaugeid']))))

print('**** Sort the gauges(ascending) *****')

levels = pd.DataFrame({'level':gauge_level})
gauges[['level']] = levels[['level']]
sort_gauges = gauges.sort_values(by = 'level')  ## level_ascending
sort_gauges.reset_index(drop=True, inplace=True)

gaugeid = sort_gauges['gaugeid']

######### Read the obs file #########
print('**** Read the obs file *****')
Qobs = pd.read_csv(obs_file)
obs = np.empty([480,len(gaugeid)])
for i in range(len(gaugeid)):
    obs[:,i] = Qobs[sort_gauges['station'][i]]

######### Begin to BC at monthly scale #########
print('**** Begin to BC at monthly scale *****')
bc_rivers = []
Qsum = np.zeros(696)
delta_sum = np.zeros(696)
gauge_bc = np.zeros(696)
for i in range(len(gaugeid)):
    print('**** Finished '+str(int(i/len(gaugeid)*100))+'% *****')
    ## gauge eqm
    k = np.where(Rivers == gaugeid[i])[0][0]
    obs_cal = obs[:,i]
    sim_cal = Qout_m[0:480,k]
    [s,o] = filter_nan(sim_cal, obs_cal)
    alldata = np.array(Qout_m[:,k])
    alldata1 = np.array(Qout_m[:,k])
    [s,o] = filter_nan(sim_cal, obs_cal)
    gauge_bc = SDM.gamma_qm(s,o,alldata)
    if any(gauge_bc<0):
        gauge_bc[gauge_bc<0] = alldata1[gauge_bc<0]
    delta_gauge = gauge_bc-np.array(Qout_m[:,k])
    #mean = mean+delta_gauge/Qout_m[:,k])
    Qsum = Qsum+np.array(Qout_m[:,k])
    delta_sum = delta_sum+delta_gauge
    Qbc_m[:,k] = gauge_bc
    bc_rivers.append(gaugeid[i])
    ## downstream revise 
    downstreams = downstream.find_downstream(gaugeid[i],river_connect1)
    for j in range(len(downstreams)):
        m = np.where(Rivers == downstreams[j])[0][0]
        Qout_m[:,m] = Qout_m[:,m]+np.multiply(Qout_m[:,m],(np.sum(delta_gauge)/np.sum(Qout_m[:,m])))

    ## upstreams BC
    upstreams = upstream.find_upstream(gaugeid[i],river_connect1)
    gauge_level = sort_gauges['level'][i]
    if gauge_level==0:
        for j in range(len(upstreams)):
            p = np.where(Rivers == upstreams[j])[0][0]
            correct = Qout_m[:,p]/Qout_m[:,k]*delta_gauge
            Qbc_m[:,p] = Qout_m[:,p]+np.multiply(Qout_m[:,p],(np.sum(correct)/np.sum(Qout_m[:,p])))
            bc_rivers.append(upstreams[j])
    else:
        dntrivers = []                 ## dont need to bc rivers
        for j in range(int(gauge_level)):
            nest_gauge = list(set(upstreams).intersection(set(gauges['gaugeid'])))
            for p in range(len(nest_gauge)):
                dntrivers.append(nest_gauge[p])
                dntrivers.extend(upstream.find_upstream(nest_gauge[p],river_connect1))
        interrivers = list(set(upstreams).difference(set(dntrivers)))
        print(len(interrivers))
        for j in range(len(interrivers)):
            p = np.where(Rivers == interrivers[j])[0][0]
            correct = Qout_m[:,p]/Qout_m[:,k]*delta_gauge
            Qbc_m[:,p] = Qout_m[:,p]+np.multiply(Qout_m[:,p],(np.sum(correct)/np.sum(Qout_m[:,p])))
            bc_rivers.append(interrivers[j])

######### The number of ungauged rivers  #########
print('**** The number of ungauged rivers *****')

rest_river = list(set(Rivers.values).difference(set(bc_rivers)))
print(len(set(rest_river)))

######### Ungauged river BC at monthly scale  #########

mean = delta_sum/Qsum

for i in range(len(rest_river)):
    print('**** Ungauged Finished '+str(int(i/len(rest_river)*100))+'% *****')
    p = np.where(Rivers == rest_river[i])[0][0]
    Qbc_m[:,p] = Qout_m[:,p]+Qout_m[:,p]*mean

for i in range(len(Rivers)):
    if any(Qbc_m[:,i].values<0):
        print("find<0")
        print(i)
    if any(np.isnan(Qbc_m[:,i].values)):
        print("find nan")


shape = (len(dates),len(Rivers))
dims = ('time','rivers', )
coords = {'time': dates, 'rivers': Rivers}
state = xr.Dataset(coords=coords)
state.attrs['title'] = 'River reaches discharge'
state.attrs['history'] = 'created by jiaojiaogou, 2021-05-27'
state.attrs['user_comment'] = 'RAPID output river discharge (driving by CNRD v1.0)'
state.attrs['source'] = 'generated from a well-trained VIC model coupled with RAPID model'
for varname in ['qout']:
    state[varname] = xr.DataArray(data=np.full(shape, np.nan),
                           coords=coords, dims=dims,
                           name=varname)
state['qout'].values = Qbc_m.values
state.to_netcdf(bc_monthly_file)
state

