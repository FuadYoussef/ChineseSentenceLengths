from __future__ import division

from file_reader import getSentenceLengths, getSLEnglish, getSentenceLengthsFullRegex, getSentenceLengthsByWord, getSentenceLengthsByWordFullRegex
from dr_yuan import splitSentencesByWords
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
import math
import copy
from dr_yuan import paddleTest
#from LAC import LAC
# encoding=utf-8
def derivative(h_vals, q_vals):
    dhdq = np.diff(h_vals)/np.diff(q_vals)
    return dhdq

def mfdfatest(sls):
    data = np.array(sls)
    # Select a band of lags, which are ints
    lag = np.unique(np.logspace(0.5, 3, 100).astype(int))

    # Select a list of powers q
    q_list = np.linspace(0, 15, 15)
    q_list = q_list[q_list != 0.0]
    # q_val = 2
    # The order of the polynomial fitting
    order = 2
    h_vals = []
    for q_val in q_list:
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
        slopes = np.polyfit(np.log(lag[20:len(sls)//5]), np.log(dfa[20:len(sls)//5]), 1)[0]
        slopes = slopes.tolist()
        # print(slopes)
        hExponents = []
        for slope in slopes:
            hExponents.append(slope)
        # print("H exponents:", hExponents)
        tao_q=(q_val*hExponents[0])-1
        # print("\nTAO: ", tao_q)
        # alpha = tao_q/q_val
        # f_alpha = q_val*alpha - tao_q
        h_vals.append(hExponents[0])


    print("\n")
    # Now what you should obtain is: slope = H + 1
    # plt.show()
    alphas = []
    f_as = []
    for i in range(len(h_vals) - 1):
        q = q_list[i]
        h = h_vals[i]
        alpha = h + q*derivative(h_vals, q_list)[i]
        alphas.append(alpha)
        print("REAL ALHA", alpha)

        f_a = q*(alpha - h) + 1
        f_as.append(f_a)
        print("f(a): ", f_a)
    print("\nDelta alpha: ", max(alphas) - min(alphas))
    print("MAX ALPHA:", max(alphas))
    print("MIN ALPHAS", min(alphas))
    return h_vals, q_list


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
    # alpha = (beta+1)/2
    # print("ALPHA:", alpha)
    # alpha is this ^^ #TODO 
    # according to this: https://en.wikipedia.org/wiki/Detrended_fluctuation_analysis

    # Alternatively, can we do this? https://www.nature.com/articles/s41598-018-35032-z
    print(beta)




if __name__ == '__main__':
    nationalHistoryTitles = ["清朝秘史", "武宗逸史", "民国演义", "民国野史", "汉代宫廷艳史", "洪宪宫闱艳史演义", "清代宫廷艳史", "清史演义", "清朝三百年艳史演义",
                             "清朝前纪", "满清兴亡史", "留东外史", "留东外史续集", "秦朝野史", "西太后艳史演义", "西施艳史演义", "西汉野史", "貂蝉艳史演义",
                             "贵妃艳史演义", "隋代宫闱史", "雍正剑侠图", "顺治出家"]
    # nationalHistoryTitles = ["射雕英雄传 金庸 1"]
    nationalHistoryTitles = ["Dracula"]
    print("National History Titles")
    for title in nationalHistoryTitles:
        print(title)
        sentenceLengths0 = getSLEnglish(title) #split text by sentence enders, length by characters
        sentenceLengths1 = getSentenceLengthsFullRegex(title)  # split text by all punctuation, length by characters
        sentenceLengths2 = getSentenceLengthsByWord(title)  # split text by sentence enders, length by characters
        sentenceLengths3 = getSentenceLengthsByWordFullRegex(title)  # split text by all punctuation, length by words
        #sentenceLengths = getSLEnglish('Moby Dick')
        #print(sentenceLengths)
        # print("H Values:")
        h_vals = mfdfatest(sentenceLengths0)
        # mfdfatest(sentenceLengths1)
        # mfdfatest(sentenceLengths2)
        # mfdfatest(sentenceLengths3)
        # print("Beta Values:")
        # try:
        #     getBeta(sentenceLengths0)
        # except Exception:
        #     print("Cant get beta")
        # getBeta(sentenceLengths1)
        # getBeta(sentenceLengths2)
        # getBeta(sentenceLengths3)
        print("***********************************")

