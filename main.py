from __future__ import division

from file_reader import getSentenceLengths, getSLEnglish, getSentenceLengthsFullRegex, getSentenceLengthsByWord, getSentenceLengthsByWordFullRegex
from dr_yuan import splitSentencesByWords
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
import math
from cwt import simple_sample
from dr_yuan import paddleTest
#from LAC import LAC
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
    lag, dfa = MFDFA(data, lag=lag, q=q_list, order=order)
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
    plt.show()

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

    graphTitles = ["三体刘慈欣", "红楼梦","红高粱家族莫言", "聊斋志异fixed", "资治通鉴2 （汉记四十五起）","酒徒刘以鬯"]
    print("Graphing Titles")
    for title in graphTitles:
        print(title)
        sentenceLengths0 = getSentenceLengths(title)  # split text by sentence enders, length by characters
        """x = np.arange(0, len(sentenceLengths0))
        y = sentenceLengths0
        plt.title("Sentence Lengths of" + title)
        plt.xlabel("Sentence Index")
        plt.ylabel("Length of Sentence i")
        plt.plot(x, y)
        plt.show()"""
        simple_sample(sentenceLengths0)
        sentenceLengths1 = getSentenceLengthsFullRegex(title)  # split text by all punctuation, length by characters
        sentenceLengths2 = getSentenceLengthsByWord(title)  # split text by sentence enders, length by characters
        sentenceLengths3 = getSentenceLengthsByWordFullRegex(title)  # split text by all punctuation, length by words
        # sentenceLengths = getSLEnglish('Moby Dick')
        # print(sentenceLengths)
        print("H Values:")
        mfdfatest(sentenceLengths0)
        mfdfatest(sentenceLengths1)
        mfdfatest(sentenceLengths2)
        mfdfatest(sentenceLengths3)
        print("Beta Values:")
        getBeta(sentenceLengths0)
        getBeta(sentenceLengths1)
        getBeta(sentenceLengths2)
        getBeta(sentenceLengths3)
        print("***********************************")