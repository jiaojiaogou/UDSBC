import os
import math
import string
import numpy as np
import pandas as pd
import xarray as xr

## function

def filter_nan(s, o):

    count = len(o) - np.isnan(o).sum()
    s1 = np.empty(count)
    o1 = np.empty(count)
    k=0
    for i in range(len(o)):
        if np.isnan(o[i]):
            continue
        else:
            o1[k] = o[i]
            s1[k] = s[i]
            k = k+1

    return s1, o1


def pc_bias(s, o):
    """
        Percent Bias
        input:
        s: simulated
        o: observed
        output:
        pc_bias: percent bias
        """
    return 100.0*np.sum(s-o)/np.sum(o)


def apb(s, o):
    """
        Absolute Percent Bias
        input:
        s: simulated
        o: observed
        output:
        apb_bias: absolute percent bias
        """
    return 100.0*np.sum(np.abs(s-o))/np.sum(o)


def rmse(s, o):
    """
        Root Mean Squared Error
        input:
        s: simulated
        o: observed
        output:
        rmses: root mean squared error
        """

    return np.sqrt(np.mean((s-o)**2))


def mae(s, o):
    """
        Mean Absolute Error
        input:
        s: simulated
        o: observed
        output:
        maes: mean absolute error
        """

    return np.mean(np.abs(s-o))


def bias(s, o):
    """
        Bias
        input:
        s: simulated
        o: observed
        output:
        bias: bias
        """
    return np.mean(s-o)


def NS(s, o):
    """
        Nash Sutcliffe efficiency coefficient
        input:
        s: simulated
        o: observed
        output:
        ns: Nash Sutcliffe efficient coefficient
        """
    return 1 - np.sum((s-o)**2)/np.sum((o-np.mean(o))**2)


def L(s, o, N=5):
    """
        Likelihood
        input:
        s: simulated
        o: observed
        output:
        L: likelihood
        """
    return np.exp(-N*np.sum((s-o)**2)/np.sum((o-np.mean(o))**2))


def correlation(s, o):
    """
        correlation coefficient
        input:
        s: simulated
        o: observed
        output:
        correlation: correlation coefficient
        """
    if s.size == 0:
        corr = np.NaN
    else:
        corr = np.corrcoef(o, s)[0, 1]
    return corr


def index_agreement(s, o):
    """
        index of agreement
        input:
        s: simulated
        o: observed
        output:
        ia: index of agreement
        """
    # s,o = filter_nan(s,o)
    ia = 1 - (np.sum((o-s)**2)) /\
             (np.sum((np.abs(s-np.mean(o))+np.abs(o-np.mean(o)))**2))
    return ia


def KGE(s, o):
    """
        Kling-Gupta Efficiency
        input:
        s: simulated
        o: observed
        output:
        kge: Kling-Gupta Efficiency
        cc: correlation
        alpha: ratio of the standard deviation
        beta: ratio of the mean
        """
    # s,o = filter_nan(s, o)
    cc = correlation(s, o)
    alpha = np.std(s)/np.std(o)
    beta = np.sum(s)/np.sum(o)
    kge = 1 - np.sqrt((cc-1)**2 + (alpha-1)**2 + (beta-1)**2)
    return kge, cc, alpha, beta


## this script writed by Jiaojiao Gou to caculate the Gof (goodness of fit) of the GS streamflow data 

## read station position 

station = pd.read_csv('./gauge_id.csv')['station']
gauge_id = pd.read_csv("./gauge_id.csv")['gaugeid']

# read obs

obs = np.empty([480,len(gauge_id)])
obs_file = pd.read_csv("./Q_obs.csv")
for i in range(len(gauge_id)):
    #print(station[i])
    obs[:,i] = obs_file[station[i]]

# read Qout simulation

Qout = xr.open_dataset('./Qbc_month1.nc').load()['qout'] #Qbc_month.nc
Rivers = xr.open_dataset("./Qmon.nc").load()['rivers']
sim = np.empty([480,len(gauge_id)])

for i in range(len(gauge_id)):
    k = np.where(Rivers == gauge_id[i])[0][0]
    #print(Qout[0:480,k])
    sim[:,i] = Qout[0:480,k]

#print(sim[108:228,9])
#np.savetxt("./yanshou_sim.csv",sim[:,1],delimiter=',')
# cal gof

gof = np.empty([len(gauge_id),10])

for i in range(len(gauge_id)):
    s1,o1 = filter_nan(sim[0:480,i], obs[0:480,i])   #0:108 108:228 0:228
    if len(o1) == 0:
        gof[i,:] = 'NaN'
    else:
        gof[i,0] = pc_bias(s1, o1)
        gof[i,1] = apb(s1, o1)
        gof[i,2] = rmse(s1, o1)
        gof[i,3] = mae(s1, o1)
        gof[i,4] = bias(s1, o1)
        gof[i,5] = NS(s1, o1)
        gof[i,6] = L(s1, o1, N=5)
        gof[i,7] = correlation(s1, o1)
        gof[i,8] = index_agreement(s1, o1)
        gof[i,9] = KGE(s1, o1)[0]
#print(gof[52,5])
np.savetxt("./gof.csv",gof,delimiter=',')

