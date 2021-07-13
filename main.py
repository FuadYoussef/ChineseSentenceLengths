from __future__ import division

from file_reader import getSentenceLengths, getSLEnglish, getSentenceLengthsFullRegex, getSentenceLengthsByWord, getSentenceLengthsByWordFullRegex
from dr_yuan import splitSentencesByWords
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
from dr_yuan import paddleTest
from LAC import LAC
# encoding=utf-8

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
    lag, dfa = MFDFA(data, lag=lag, q=2, order=order)
    # To uncover the Hurst index, lets get some log-log plots
    plt.loglog(lag[20:len(sls)//5], dfa[20:len(sls)//5], 'o', label='fOU: MFDFA q=2')

    # And now we need to fit the line to find the slope. We will
    # fit the first points, since the results are more accurate
    # there. Don't forget that if you are seeing in log-log
    # scales, you need to fit the logs of the results
    # print(len(sls)//5)
    # slopes = np.polyfit(np.log(lag[20:len(sls)//5]), np.log(dfa[20:len(sls)//5]), 1)[0]
    for x in range(0, len(dfa)):
        for y in range(0, len(dfa[x])):
            if dfa[x,y] == 0:
                dfa[x,y] += .000000000001
    # slopes = np.polyfit(np.log(lag), np.log(dfa), 1)[0]
    slopes = np.polyfit(np.log(lag[20:len(sls)//5]), np.log(dfa[20:len(sls)//5]), 1)[0]
    slopes = slopes.tolist()
    # print(slopes)
    hExponents = []
    for slope in slopes:
        hExponents.append(slope)
    print(hExponents)

    # Now what you should obtain is: slope = H + 1
    #plt.show()

if __name__ == '__main__':
    title = '射雕英雄传金庸'
    sentenceLengths0 = getSentenceLengths(title) #split text by sentence enders, length by characters
    sentenceLengths1 = getSentenceLengthsFullRegex(title)  # split text by all punctuation, length by characters
    sentenceLengths2 = getSentenceLengthsByWord(title)  # split text by sentence enders, length by characters
    sentenceLengths3 = getSentenceLengthsByWordFullRegex(title)  # split text by all punctuation, length by words
    # sentenceLengths = getSLEnglish("Great Expectations")
    mfdfatest(sentenceLengths0)
    mfdfatest(sentenceLengths1)
    mfdfatest(sentenceLengths2)
    mfdfatest(sentenceLengths3)

