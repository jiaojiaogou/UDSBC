import numpy as np

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




