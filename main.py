from __future__ import division

from file_reader import getSentenceLengths, getSLEnglish, getSentenceLengthsFullRegex, getSentenceLengthsByWord, getSentenceLengthsByWordFullRegex, get_texts, calculation5, calculation6
from dr_yuan import splitSentencesByWords
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
from spectrum import spectrum_analysis
import math
from dr_yuan import paddleTest
import pandas as pd
from matplotlib import font_manager

fontP = font_manager.FontProperties()
fontP.set_family('SimHei')
fontP.set_size(14)
#from LAC import LAC
# encoding=utf-8
import os
from pathlib import Path



def mfdfatest(sls, debug=False):

    # SAVE OUT DATA TO POTENTIALLY RUN IN MATLAB?

    # np.savetxt("sentence_lens.csv", sls, delimiter=",")
    data = np.array(sls)
    # Select a band of lags, which are ints
    lag = np.unique(np.logspace(0.5, 3, 100).astype(int))

    # Select a list of powers q
    q = np.linspace(-4, 4, 41)
    q = q[q != 0.0]

    # The order of the polynomial fitting
    order = 2
    h_values = []

    # Get hurst value over a range of q values so that we get a series of alphas. These alphas can be used to get the delta alpha
    for q_val in q:
        # Obtain the (MF)DFA as
        lag, dfa = MFDFA(data, lag=lag, q=q_val, order=order)
        # To uncover the Hurst index, lets get some log-log plots
        #plt.loglog(lag[20:len(sls)//5], dfa[20:len(sls)//5], 'o', label='fOU: MFDFA q=2')
        plt.plot(lag[20:len(sls) // 5], dfa[20:len(sls) // 5], 'o', label='fOU: MFDFA q=2')
        # float precision stuff? Don't want 0s?
        for x in range(0, len(dfa)):
            for y in range(0, len(dfa[x])):
                if dfa[x,y] == 0:
                    dfa[x,y] += .000000000001


        h = np.polyfit(np.log(lag[20:len(sls)//5]), np.log(dfa[20:len(sls)//5]), 1)[0].tolist()
        h_values.append(h[0])


    # derivate dT/dQ to ge alphas
    t = np.multiply(q, h_values) - 1
    dT = np.diff(t)
    dQ = np.diff(q)   
    alpha = dT/dQ
    delta_alpha = max(alpha) - min(alpha)

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
        print(delta_alpha)
    f_a = q[:-1] * alpha - t[:-1]
    return h_values, delta_alpha, alpha, f_a

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
    return beta
    print(beta)




if __name__ == '__main__':

    dir_to_read = "calculation1"
    texts = ["太阳照在桑干河上.txt", "酒徒刘以鬯.txt"]

    data = []
    for title in texts:
        print(title)
        sentence_lengths = getSentenceLengths(title)

        h, delta_alpha, alphas, f_a = mfdfatest(sentence_lengths)
        titleString = title.split(".")[0] + " " + "Qth Order Fluctuations"
        plt.title(titleString, fontproperties=fontP)
        plt.xlabel("s", fontproperties=fontP)
        plt.ylabel("f(s)", fontproperties=fontP)
        plt.show()
        plt.close()
        h_q_2 = h[29]
        beta = getBeta(sentence_lengths)
        data.append([title.split("/")[-1], len(sentence_lengths), delta_alpha, beta, h_q_2])
        titleString = title.split(".")[0] + " "+"Singularity Spectrum"
        plt.title(titleString, fontproperties=fontP)
        plt.xlabel(r'$\alpha$', fontproperties=fontP)
        plt.ylabel(r"f($\alpha$)", fontproperties=fontP)
        plt.plot(alphas, f_a)
        plt.show()

    delta_alpha_df = pd.DataFrame(data, columns=["Title", "Samples", "Delta Alpha", "Beta Value", "H Value Q = 2"])
    delta_alpha_df.to_csv(dir_to_read + ".csv", sep='\t')

    """

    dir_to_read = "calculation2"

    data = []
    for title in texts:
        print(title)
        sentence_lengths = getSentenceLengthsFullRegex(title)

        h, delta_alpha, alphas, f_a = mfdfatest(sentence_lengths)
        h_q_2 = h[29]
        beta = getBeta(sentence_lengths)
        data.append([title.split("/")[-1], len(sentence_lengths), delta_alpha, beta, h_q_2])
        plt.title("Singularity Spectrum")
        plt.xlabel("alpha")
        plt.ylabel("f(alpha)")
        plt.plot(alphas, f_a)
        plt.show()

    delta_alpha_df = pd.DataFrame(data, columns=["Title", "Samples", "Delta Alpha", "Beta Value", "H Value Q = 2"])
    delta_alpha_df.to_csv(dir_to_read + ".csv", sep='\t')

    dir_to_read = "calculation3"

    data = []
    for title in texts:
        print(title)
        sentence_lengths = getSentenceLengthsByWord(title)

        h, delta_alpha, alphas, f_a = mfdfatest(sentence_lengths)
        h_q_2 = h[29]
        beta = getBeta(sentence_lengths)
        data.append([title.split("/")[-1], len(sentence_lengths), delta_alpha, beta, h_q_2])
        plt.title("Singularity Spectrum")
        plt.xlabel("alpha")
        plt.ylabel("f(alpha)")
        plt.plot(alphas, f_a)
        plt.show()

    delta_alpha_df = pd.DataFrame(data, columns=["Title", "Samples", "Delta Alpha", "Beta Value", "H Value Q = 2"])
    delta_alpha_df.to_csv(dir_to_read + ".csv", sep='\t')

    dir_to_read = "calculation4"

    data = []
    for title in texts:
        print(title)
        sentence_lengths = getSentenceLengthsByWordFullRegex(title)

        h, delta_alpha, alphas, f_a = mfdfatest(sentence_lengths)
        h_q_2 = h[29]
        beta = getBeta(sentence_lengths)
        data.append([title.split("/")[-1], len(sentence_lengths), delta_alpha, beta, h_q_2])
        plt.title("Singularity Spectrum")
        plt.xlabel("alpha")
        plt.ylabel("f(alpha)")
        plt.plot(alphas, f_a)
        plt.show()

    delta_alpha_df = pd.DataFrame(data, columns=["Title", "Samples", "Delta Alpha", "Beta Value", "H Value Q = 2"])
    delta_alpha_df.to_csv(dir_to_read + ".csv", sep='\t')




    dir_to_read = "calculation5"

    data = []
    for title in texts:
        print(title)
        sentence_lengths = calculation5(title)

        h, delta_alpha, alphas, f_a = mfdfatest(sentence_lengths)
        h_q_2 = h[29]
        beta = getBeta(sentence_lengths)
        data.append([title.split("/")[-1], len(sentence_lengths), delta_alpha, beta, h_q_2])
        plt.title("Singularity Spectrum")
        plt.xlabel("alpha")
        plt.ylabel("f(alpha)")
        plt.plot(alphas, f_a)
        plt.show()

    delta_alpha_df = pd.DataFrame(data, columns=["Title", "Samples", "Delta Alpha", "Beta Value", "H Value Q = 2"])
    delta_alpha_df.to_csv(dir_to_read + ".csv", sep='\t')
    """

