from __future__ import division

from file_reader import getSentenceLengths
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
# encoding=utf-8


def multifractal(sls):
    data = np.array(sls)
    lag = np.unique(np.logspace(0.5, 3, 100).astype(int))

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

def mfdfatest(sls):
    data = np.array(sls)
    # Select a band of lags, which are ints
    lag = np.unique(np.logspace(0.5, 3, 100).astype(int))

    # Select a list of powers q
    q_list = np.linspace(-4, 4, 9)
    q_list = q_list[q_list != 0.0]

    # The order of the polynomial fitting
    order = 2

    # Obtain the (MF)DFA as
    lag, dfa = MFDFA(data, lag=lag, q=q_list, order=order)
    # To uncover the Hurst index, lets get some log-log plots
    plt.loglog(lag, dfa, 'o', label='fOU: MFDFA q=2')

    # And now we need to fit the line to find the slope. We will
    # fit the first points, since the results are more accurate
    # there. Don't forget that if you are seeing in log-log
    # scales, you need to fit the logs of the results
    # print(len(sls)//5)
    # slopes = np.polyfit(np.log(lag[20:len(sls)//5]), np.log(dfa[20:len(sls)//5]), 1)[0]
    for x in range(0, len(dfa)):
        for y in range(0, len(dfa[x])):
            if dfa[x,y] == 0:
                print("made it")
                dfa[x,y] += .000000000001
    slopes = np.polyfit(np.log(lag), np.log(dfa), 1)[0]
    slopes = slopes.tolist()
    hExponents = []
    for slope in slopes:
        hExponents.append(slope - 1)
    print(hExponents)

    # Now what you should obtain is: slope = H + 1
    plt.show()

if __name__ == '__main__':
    sentenceLengths = getSentenceLengths('射雕英雄传 金庸 1')
    # multifractal(sentenceLengths)
    mfdfatest(sentenceLengths)
    #difs = []
    #for i in range(0, len(mine)):
    #    difs.append(mine[i] - col[i])
    #print(difs)
    # simple_sample(sentenceLengths)

