## Bias scale mapping at daily scle 
## foresteps: cdo monsum Qout_61_18_daily.nc Qmonsum.nc; cdo sub Qbc_month.nc Qmon.nc Qdelta.nc
## Input: Qout_61_18_daily.nc, Qmonsum.nc, Qdelta.nc
## Output: revised Qbc_61_18_daily.nc
## writed by Jiaojiao Gou   2022-05-5

import pandas as pd
import xarray as xr
import numpy as np
import datetime
import os

Q_daily_file = './output/Qout_61_18_daily.nc'
Q_month_file = './output/Qmon.nc'
Q_monsum_file = './output/Qmonsum.nc'
bc_daily_file = './output/Qbc_61_18_daily.nc'
bc_monthly_file = './output/Qbc_month.nc'

sysComm1 = "cdo monsum ./output/Qout_61_18_daily.nc ./output/Qmonsum.nc"
os.system(sysComm1)
np.seterr(divide='ignore', invalid='ignore')

Qout = xr.open_dataset(Q_daily_file).load()['qout'] ##original
Rivers = xr.open_dataset(bc_monthly_file).load()['rivers']
Qbc = xr.open_dataset(Q_daily_file).load()['qout']

monsum = xr.open_dataset(Q_monsum_file).load()['qout'] 

delta = xr.open_dataset(bc_monthly_file).load()['qout']-xr.open_dataset(Q_month_file).load()['qout'] 
dates = pd.date_range('1/1/1961', '31/12/2018')
dates1 = pd.date_range('1/1/1961', '31/12/2018', freq='1M')
ndays = dates1.day

bc = np.empty([len(dates),len(Rivers)])
for i in range(len(Rivers)):
    bc[:,i] = np.repeat(np.multiply(delta[:,i].values/monsum[:,i].values,ndays),ndays)


######### River BC at daily scale  #########

dates = pd.date_range('1/1/1961', '31/12/2018')

for i in range(len(Rivers)):
    print('**** Finished '+str(int(i/len(Rivers)*100))+'% *****')
    Qbc[:,i] = Qout[:,i]+np.multiply(Qout[:,i],bc[:,i])
    if np.any(Qbc[:,i].values<0):
        kk = Qbc[:,i].values
        kk1 = np.where(kk<0,0,kk)
        Qbc[:,i].values = kk1
    if any(np.isnan(Qbc[:,i].values)):
        kk = Qbc[:,i].values
        kk[np.isnan(kk)]=0
        Qbc[:,i].values = kk
    if any(Qbc[:,i].values<0):
        print("find<0")
        print(i)
    if any(np.isnan(Qbc[:,i].values)):
        print("find nan")
        print(i)

shape = (len(dates),len(Rivers))
dims = ('time','rivers', )
coords = {'time': dates, 'rivers': Rivers}
state = xr.Dataset(coords=coords)
state.attrs['title'] = 'River reaches discharge'
state.attrs['history'] = 'created by jiaojiaogou, 2021-01-18'
state.attrs['user_comment'] = 'RAPID output river discharge (driving by CNRD v1.0)'
state.attrs['source'] = 'generated from a well-trained VIC model coupled with RAPID model'
for varname in ['qout']:
    state[varname] = xr.DataArray(data=np.full(shape, np.nan),
                           coords=coords, dims=dims,
                           name=varname)
state['qout'].values = Qbc.values
state.to_netcdf(bc_daily_file)
state
