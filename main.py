from __future__ import division

from file_reader import getSentenceLengths, getSLEnglish, getSentenceLengthsFullRegex, getSentenceLengthsByWord, getSentenceLengthsByWordFullRegex
from dr_yuan import splitSentencesByWords
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
import math
from dr_yuan import paddleTest
#from LAC import LAC
# encoding=utf-8

def mfdfatest(sls, debug=False):

    # SAVE OUT DATA TO POTENTIALLY RUN IN MATLAB?

    np.savetxt("sentence_lens.csv", sls, delimiter=",")
    data = np.array(sls)
    # Select a band of lags, which are ints
    lag = np.unique(np.logspace(0.5, 3, 100).astype(int))

    # Select a list of powers q
    q = np.linspace(-4, 4, 41)
    q = q[q != 0.0]

    # The order of the polynomial fitting
    order = 2
    h_values = []
    for q_val in q:
        # Obtain the (MF)DFA as
        lag, dfa = MFDFA(data, lag=lag, q=q_val, order=order)
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
        h = np.polyfit(np.log(lag[20:len(sls)//5]), np.log(dfa[20:len(sls)//5]), 1)[0].tolist()
        h_values.append(h[0])

    t = np.multiply(q, h_values) - 1
    dT = np.diff(t)
    dQ = np.diff(q)   
    alpha = dT/dQ

    if debug:
        print("\nactual h")
        print(h_values)
        print("\nt")
        print(t)
        print("\ndt")
        print(dT)
        print("\ndq")
        print(dQ)
       
        print("\nALPHA HERE:")
        print(alpha)

        f_a = q[:-1]*alpha - t[:-1]
        print("\n f(alpha)")
        print(f_a)

        print("DELTA ALPHA")
        print(max(alpha) - min(alpha))

    return h_values, alpha

def getBeta(sls):
    # Calculates power spectrum

    data = np.array(sls)  # Converts data to numpy array
    data = data / np.std(data)  # Divides by standard deviation
    data = data-np.mean(data)  # Subtracts mean
    Fs = 1  # Sets Fs equal to 1
    nfft = 2**(math.ceil(np.log2(len(data))))  # Defines nfft
    fft_data = np.fft.fft(data, nfft)  # Calculates fast fourier transform
    NumUniquePts = math.ceil((nfft + 1) / 2)  # Calculates number of unique points
    fft_data = fft_data[0:NumUniquePts]  # Filters fft
    mx = abs(fft_data)  # Calculates mx
    mx = mx/len(data)  # Calculates mx
    mx = mx**2  # Calculates mx

    # Multiplies mx by 2, ignoring DC and Nyquist componentd

    if nfft % 2 == 1:
        mx[1:len(mx)] = mx[1:len(mx)]*2
    else:
        mx[1:(len(mx)-1)] = mx[1:(len(mx)-1)] * 2

    # Now, create a frequency vector:
    # This is an evenly spaced frequency vector with NumUniquePts points

    f = np.linspace(0, NumUniquePts-1, NumUniquePts)*Fs/nfft

    # Calculates and filters logarithms

    logf = np.log(f)
    logmx = np.log(mx)
    mask = logf < -2.75
    logf = logf[mask]
    logmx = logmx[mask]
    mask2 = logf > -100000000000000000000
    logf = logf[mask2]
    logmx = logmx[mask2]

    # Calculates and prints beta

    beta = np.polyfit(logf, logmx, 1)[0]
    print(beta)




if __name__ == '__main__':
    # nationalHistoryTitles = ["清朝秘史", "武宗逸史", "民国演义", "民国野史", "汉代宫廷艳史", "洪宪宫闱艳史演义", "清代宫廷艳史", "清史演义", "清朝三百年艳史演义",
    #                          "清朝前纪", "满清兴亡史", "留东外史", "留东外史续集", "秦朝野史", "西太后艳史演义", "西施艳史演义", "西汉野史", "貂蝉艳史演义",
    #                          "贵妃艳史演义", "隋代宫闱史", "雍正剑侠图", "顺治出家"]
    # print("National History Titles")
    tests = ["Moby Dick", "the_ambassadors"]
    for title in tests:
        print(title)
        # sentenceLengths0 = getSentenceLengths(title) #split text by sentence enders, length by characters
        # sentenceLengths1 = getSentenceLengthsFullRegex(title)  # split text by all punctuation, length by characters
        # sentenceLengths2 = getSentenceLengthsByWord(title)  # split text by sentence enders, length by characters
        # sentenceLengths3 = getSentenceLengthsByWordFullRegex(title)  # split text by all punctuation, length by words
        sentenceLengths = getSLEnglish(title)
        # print(sentenceLengths)
        print("\n\n---H Values of ", title)
        mfdfatest(sentenceLengths)
        # mfdfatest(sentenceLengths0)
        # mfdfatest(sentenceLengths1)
        # mfdfatest(sentenceLengths2)
        # mfdfatest(sentenceLengths3)
        # print("Beta Values:")
        # getBeta(sentenceLengths0)
        # getBeta(sentenceLengths1)
        # getBeta(sentenceLengths2)
        # getBeta(sentenceLengths3)
        # print("***********************************")

