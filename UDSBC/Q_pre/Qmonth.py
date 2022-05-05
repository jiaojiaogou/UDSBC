## writed by Jiaojiao Gou   2022-05-05

import os
import pandas as pd
import xarray as xr
import numpy as np

def creat_Q(basin_id,Q_file,Q_file1,Qmon):

    rivers = np.loadtxt(basin_id,delimiter=",", usecols=(0,),skiprows=0,ndmin=1, dtype=np.int32)
    dates = pd.date_range('1/1/1961', '31/12/2018')
    shape = (len(dates),len(rivers))
    dims = ('time','rivers', )

    coords = {'time': dates, 'rivers': rivers}
    state = xr.Dataset(coords=coords)
    state.attrs['title'] = 'River reaches discharge'
    state.attrs['history'] = 'created by jiaojiaogou, 2021-01-18'
    state.attrs['user_comment'] = 'RAPID output river discharge (driving by CNRD v1.0)'
    state.attrs['source'] = 'generated from a well-trained VIC model coupled with RAPID model'

    for varname in ['qout']:
        state[varname] = xr.DataArray(data=np.full(shape, np.nan),
                                   coords=coords, dims=dims,
                                   name=varname)

    Qout = xr.open_dataset(Q_file).load()['Qout']
    river_id =xr.open_dataset(Q_file).load()['rivid']

    for i in range(len(rivers)):
        state['qout'].values[:,i] = Qout[366:21550,int(np.where(river_id==rivers[i])[0])] #7305 61-79
        if np.any(state['qout'][:,i].values<0):
            kk = state['qout'][:,i].values
            kk1 = np.where(kk<0,0,kk)
            state['qout'].values[:,i] = kk1
        if np.any(np.isnan(state['qout'][:,i].values)):
            kk = state['qout'][:,i].values
            kk1 = np.where(np.isnan(kk),0,kk)
            state['qout'].values[:,i] = kk1

    state.qout.attrs['units'] = 'm3 s-1'
    state.qout.attrs['longname'] = 'Discharge at each river reach'
    state.to_netcdf(Q_file1)
    state

    return


