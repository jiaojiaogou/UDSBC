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

import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF

def BC_eqm(sim_ref,obs_ref,sim_data):
    sim_ecdf = ECDF(sim_ref)
    p = sim_ecdf(sim_data) * 100
    corr = np.percentile(obs_ref, p) -np.percentile(sim_ref, p)
    sim_data += corr
    return sim_data




