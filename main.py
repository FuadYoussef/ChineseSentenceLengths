from __future__ import division

from file_reader import getSentenceLengths, getSLEnglish, getSentenceLengthsFullRegex, getSentenceLengthsByWord, getSentenceLengthsByWordFullRegex
from dr_yuan import splitSentencesByWords
import re
import numpy as np
import matplotlib.pyplot as plt
from MFDFA import MFDFA
from dr_yuan import paddleTest
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
    contemporaryTitles = ["三体刘慈欣","三重门韩寒","北妹","十三步莫言","单位刘震云","古炉","坚硬如水","尘埃落定","废都","活着","灵山高行健","狼图腾姜戎","玩的就是心跳王朔","穆斯林的葬礼","红高粱家族莫言","芳华严歌苓","金陵十三钗","长恨歌","陈忠实白鹿原","雍正皇帝二月河","额尔古纳河右岸迟子建","饥饿的女儿虹影","马桥词典韩少功"]
    print("Contemporary Titles")
    for title in contemporaryTitles:
        print(title)
        sentenceLengths0 = getSentenceLengths(title) #split text by sentence enders, length by characters
        sentenceLengths1 = getSentenceLengthsFullRegex(title)  # split text by all punctuation, length by characters
        sentenceLengths2 = getSentenceLengthsByWord(title)  # split text by sentence enders, length by characters
        sentenceLengths3 = getSentenceLengthsByWordFullRegex(title)  # split text by all punctuation, length by words
        # sentenceLengths = getSLEnglish("Great Expectations")
        mfdfatest(sentenceLengths0)
        mfdfatest(sentenceLengths1)
        mfdfatest(sentenceLengths2)
        mfdfatest(sentenceLengths3)
        print("***********************************")

    print("HK Titles")
    hkTitles = ["射雕英雄传金庸","玫瑰的故事","白发魔女传梁羽生", "秧歌张爱玲", "绝代双骄古龙", "胭脂扣李碧华", "酒徒刘以鬯", "鹿鼎记 full"]
    for title in hkTitles:
        print(title)
        sentenceLengths0 = getSentenceLengths(title) #split text by sentence enders, length by characters
        sentenceLengths1 = getSentenceLengthsFullRegex(title)  # split text by all punctuation, length by characters
        sentenceLengths2 = getSentenceLengthsByWord(title)  # split text by sentence enders, length by characters
        sentenceLengths3 = getSentenceLengthsByWordFullRegex(title)  # split text by all punctuation, length by words
        # sentenceLengths = getSLEnglish("Great Expectations")
        mfdfatest(sentenceLengths0)
        mfdfatest(sentenceLengths1)
        mfdfatest(sentenceLengths2)
        mfdfatest(sentenceLengths3)
        print("***********************************")
