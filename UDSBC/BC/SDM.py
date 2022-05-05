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
from scipy.stats import gamma


def gamma_qm(mod_data,obs_data,sce_data):
    cdf_threshold = .99999999
    lower_limit = 0.1
    min_samplesize = 10
    
    obs_raindays = obs_data[obs_data >= lower_limit]
    mod_raindays = mod_data[mod_data >= lower_limit]

    if obs_raindays.size < min_samplesize \
        or mod_raindays.size < min_samplesize:
        print('samplesize<10')

    obs_frequency = 1. * obs_raindays.shape[0] / obs_data.shape[0]
    mod_frequency = 1. * mod_raindays.shape[0] / mod_data.shape[0]
    obs_gamma = gamma.fit(obs_raindays, floc=0)
    mod_gamma = gamma.fit(mod_raindays, floc=0)

    obs_cdf = gamma.cdf(np.sort(obs_raindays), *obs_gamma)
    mod_cdf = gamma.cdf(np.sort(mod_raindays), *mod_gamma)
    obs_cdf[obs_cdf > cdf_threshold] = cdf_threshold
    mod_cdf[mod_cdf > cdf_threshold] = cdf_threshold

    
    sce_raindays = sce_data[sce_data >= lower_limit]
    if sce_raindays.size < min_samplesize:
        print('samplesize<10')

    sce_frequency = 1. * sce_raindays.shape[0] / sce_data.shape[0]
    sce_argsort = np.argsort(sce_data)
    sce_gamma = gamma.fit(sce_raindays, floc=0)
    expected_sce_raindays = min(
        int(np.round(
            len(sce_data) * obs_frequency * sce_frequency
            / mod_frequency)),
        len(sce_data))

    sce_cdf = gamma.cdf(np.sort(sce_raindays), *sce_gamma)
    sce_cdf[sce_cdf > cdf_threshold] = cdf_threshold

    # interpolate cdf-values for obs and mod to the length of the
    # scenario
    obs_cdf_intpol = np.interp(
        np.linspace(1, len(obs_raindays), len(sce_raindays)),
        np.linspace(1, len(obs_raindays), len(obs_raindays)),
        obs_cdf)
    mod_cdf_intpol = np.interp(
            np.linspace(1, len(mod_raindays), len(sce_raindays)),
            np.linspace(1, len(mod_raindays), len(mod_raindays)),
            mod_cdf)
    # adapt the observation cdfs
    obs_inverse = 1. / (1 - obs_cdf_intpol)
    mod_inverse = 1. / (1 - mod_cdf_intpol)
    sce_inverse = 1. / (1 - sce_cdf)
    adapted_cdf = 1 - 1. / (obs_inverse * sce_inverse / mod_inverse)
    adapted_cdf[adapted_cdf < 0.] = 0.

    # correct by adapted observation cdf-values
    xvals = gamma.ppf(np.sort(adapted_cdf), *obs_gamma) *\
        gamma.ppf(sce_cdf, *sce_gamma) /\
        gamma.ppf(sce_cdf, *mod_gamma)

    # interpolate to the expected length of future raindays
    correction = np.zeros(len(sce_data))
    if len(sce_raindays) > expected_sce_raindays:
        xvals = np.interp(
            np.linspace(1, len(sce_raindays), expected_sce_raindays),
            np.linspace(1, len(sce_raindays), len(sce_raindays)),
            xvals)
    else:
        xvals = np.hstack(
            (np.zeros(expected_sce_raindays -
                       len(sce_raindays)), xvals))
    correction[sce_argsort[-expected_sce_raindays:]] = xvals
    return correction