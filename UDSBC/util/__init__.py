__all__ = ["filter_nan"]
import numpy as np

def filter_nan(sim, obs):

    count = len(obs) - np.isnan(obs).sum()
    s1 = np.empty(count)
    o1 = np.empty(count)
    k=0
    for i in range(len(obs)):
        if np.isnan(obs[i]):
            continue
        else:
            o1[k] = obs[i]
            s1[k] = sim[i]
            k = k+1
    return s1, o1

