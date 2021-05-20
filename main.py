from __future__ import division

from file_reader import getSentenceLengths
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
# encoding=utf-8


def multifractal(sls):
    data = np.array(sls)
    # Select a band of lags, which usually ranges from
    # very small segments of data, to very long ones, as
    lag = np.unique(np.logspace(0.5, 3, 100).astype(int))
    # Notice these must be ints, since these will segment
    # the data into chucks of lag size

    # Select the power q
    q = 5

    # The order of the polynomial fitting
    order = 1

    # Obtain the (MF)DFA as
    lag, dfa = MFDFA(data, lag=lag, q=q, order=order)
    # To uncover the Hurst index, lets get some log-log plots
    plt.loglog(lag, dfa, 'o', label='fOU: MFDFA q=5')

    # And now we need to fit the line to find the slope. We will
    # fit the first points, since the results are more accurate
    # there. Don't forget that if you are seeing in log-log
    # scales, you need to fit the logs of the results
    pol = np.polyfit(np.log(lag[:15]), np.log(dfa[:15]), 1)
    print(pol)
    plt.show()
    # Now what you should obtain is: slope = H + 1

if __name__ == '__main__':
    sentenceLengths = getSentenceLengths('乌云遇皎月')
    multifractal(sentenceLengths)

    # simple_sample(sentenceLengths)




