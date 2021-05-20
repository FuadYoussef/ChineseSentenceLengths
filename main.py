from __future__ import division

import re
import numpy as np
import matplotlib.pyplot as plt
import numpy
from matplotlib import pyplot
from MFDFA import MFDFA

import pycwt as wavelet
from pycwt.helpers import find
# encoding=utf-8
import jieba



# these are the Unicode ranges in which any Chinese characters would exist
cjk_ranges = [
                (0x4E00, 0x62FF),
                (0x6300, 0x77FF),
                (0x7800, 0x8CFF),
                (0x8D00, 0x9FCC),
                (0x3400, 0x4DB5),
                (0x20000, 0x215FF),
                (0x21600, 0x230FF),
                (0x23100, 0x245FF),
                (0x24600, 0x260FF),
                (0x26100, 0x275FF),
                (0x27600, 0x290FF),
                (0x29100, 0x2A6DF),
                (0x2A700, 0x2B734),
                (0x2B740, 0x2B81D),
                (0x2B820, 0x2CEAF),
                (0x2CEB0, 0x2EBEF),
                (0x2F800, 0x2FA1F)
            ]

# when given the name of a text file excluding the extension, this function reads the text and returns a string
def readText(name):
    f = open(name + ".txt", "r", encoding='utf-8')
    text = f.read()
    f.close()
    return text

# this function calculates the sentence by only counting Chinese characters that aren't punctuation or spacing
def lenSentence(sentence):
    strLen = 0
    for c in sentence:
        if is_cjk(c) and c != "，" and c != "“" and c != " " and c != "：" and c != "；" and c != "-" and c != "\n" and c != "\t":
            strLen += 1
    return strLen

# a boolean function that checks if a given character is a Chinese character or not by seeing if it is within the ranges defined earlier
def is_cjk(char):
    char = ord(char)
    for bottom, top in cjk_ranges:
        if char >= bottom and char <= top:
            return True
    return False

def copyFunc(y):
    x = np.linspace(0, 1, len(y))
    p = np.poly1d(np.polyfit(x, y,3))  # fitting to a 3rd degree polynomial
    t = np.linspace(0, 1, 200)
    plt.plot(x, y, 'o-', t, p(t), '-')
    plt.show()#plot sentence lengths with fitted curve


def multifractal(sls):
    data = numpy.array(sls)
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

def simple_sample(sls):
    # Then, we load the dataset and define some data related parameters. In this
    # case, the first 19 lines of the data file contain meta-data, that we ignore,
    # since we set them manually (*i.e.* title, units).
    # url = 'http://paos.colorado.edu/research/wavelets/wave_idl/nino3sst.txt'
    # dat = numpy.genfromtxt(url, skip_header=19)

    title = 'Sentence Length'
    label = 'Zhufu Sentence Length'
    units = 'Characters'
    t0 = 1
    dt = 1  # In years
    dat = numpy.array(sls)
    # We also create a time array in years.
    N = dat.size
    t = numpy.arange(0, N) * dt + t0

    # We write the following code to detrend and normalize the input data by its
    # standard deviation. Sometimes detrending is not necessary and simply
    # removing the mean value is good enough. However, if your dataset has a well
    # defined trend, such as the Mauna Loa CO\ :sub:`2` dataset available in the
    # above mentioned website, it is strongly advised to perform detrending.
    # Here, we fit a one-degree polynomial function and then subtract it from the
    # original data.
    p = numpy.polyfit(t - t0, dat, 1)
    dat_notrend = dat - numpy.polyval(p, t - t0)
    std = dat_notrend.std()  # Standard deviation
    var = std ** 2  # Variance
    dat_norm = dat_notrend / std  # Normalized dataset

    # The next step is to define some parameters of our wavelet analysis. We
    # select the mother wavelet, in this case the Morlet wavelet with
    # :math:`\omega_0=6`.
    mother = wavelet.Morlet(6)
    s0 = 2 * dt  # Starting scale, in this case 2 * 0.25 years = 6 months
    dj = 1 / 12  # Twelve sub-octaves per octaves
    J = 7 / dj  # Seven powers of two with dj sub-octaves
    alpha, _, _ = wavelet.ar1(dat)  # Lag-1 autocorrelation for red noise

    # The following routines perform the wavelet transform and inverse wavelet
    # transform using the parameters defined above. Since we have normalized our
    # input time-series, we multiply the inverse transform by the standard
    # deviation.
    wave, scales, freqs, coi, fft, fftfreqs = wavelet.cwt(dat_norm, dt, dj, s0, J,
                                                          mother)
    iwave = wavelet.icwt(wave, scales, dt, dj, mother) * std

    # We calculate the normalized wavelet and Fourier power spectra, as well as
    # the Fourier equivalent periods for each wavelet scale.
    power = (numpy.abs(wave)) ** 2
    fft_power = numpy.abs(fft) ** 2
    period = 1 / freqs

    # We could stop at this point and plot our results. However we are also
    # interested in the power spectra significance test. The power is significant
    # where the ratio ``power / sig95 > 1``.
    signif, fft_theor = wavelet.significance(1.0, dt, scales, 0, alpha,
                                             significance_level=0.95,
                                             wavelet=mother)
    sig95 = numpy.ones([1, N]) * signif[:, None]
    sig95 = power / sig95

    # Then, we calculate the global wavelet spectrum and determine its
    # significance level.
    glbl_power = power.mean(axis=1)
    dof = N - scales  # Correction for padding at edges
    glbl_signif, tmp = wavelet.significance(var, dt, scales, 1, alpha,
                                            significance_level=0.95, dof=dof,
                                            wavelet=mother)

    # We also calculate the scale average between 2 years and 8 years, and its
    # significance level.
    sel = find((period >= 2) & (period < 8))
    Cdelta = mother.cdelta
    scale_avg = (scales * numpy.ones((N, 1))).transpose()
    scale_avg = power / scale_avg  # As in Torrence and Compo (1998) equation 24
    scale_avg = var * dj * dt / Cdelta * scale_avg[sel, :].sum(axis=0)
    scale_avg_signif, tmp = wavelet.significance(var, dt, scales, 2, alpha,
                                                 significance_level=0.95,
                                                 dof=[scales[sel[0]],
                                                      scales[sel[-1]]],
                                                 wavelet=mother)

    # Finally, we plot our results in four different subplots containing the
    # (i) original series anomaly and the inverse wavelet transform; (ii) the
    # wavelet power spectrum (iii) the global wavelet and Fourier spectra ; and
    # (iv) the range averaged wavelet spectrum. In all sub-plots the significance
    # levels are either included as dotted lines or as filled contour lines.

    # Prepare the figure
    pyplot.close('all')
    pyplot.ioff()
    figprops = dict(figsize=(11, 8), dpi=72)
    fig = pyplot.figure(**figprops)


    # First sub-plot, the original time series anomaly and inverse wavelet
    # transform.
    ax = pyplot.axes([0.1, 0.75, 0.65, 0.2])
    ax.plot(t, iwave, '-', linewidth=1, color=[0.5, 0.5, 0.5])
    ax.plot(t, dat, 'k', linewidth=1.5)
    ax.set_title('a) {}'.format(title))
    ax.set_ylabel(r'{} [{}]'.format(label, units))

    # Second sub-plot, the normalized wavelet power spectrum and significance
    # level contour lines and cone of influece hatched area. Note that period
    # scale is logarithmic.
    bx = pyplot.axes([0.1, 0.37, 0.65, 0.28], sharex=ax)
    levels = [0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16]
    bx.contourf(t, numpy.log2(period), numpy.log2(power), numpy.log2(levels),
                extend='both', cmap=pyplot.cm.viridis)
    extent = [t.min(), t.max(), 0, max(period)]
    bx.contour(t, numpy.log2(period), sig95, [-99, 1], colors='k', linewidths=2,
               extent=extent)
    bx.fill(numpy.concatenate([t, t[-1:] + dt, t[-1:] + dt,
                               t[:1] - dt, t[:1] - dt]),
            numpy.concatenate([numpy.log2(coi), [1e-9], numpy.log2(period[-1:]),
                               numpy.log2(period[-1:]), [1e-9]]),
            'k', alpha=0.3, hatch='x')
    bx.set_title('b) {} Wavelet Power Spectrum ({})'.format(label, mother.name))
    bx.set_ylabel('Period (years)')
    #
    Yticks = 2 ** numpy.arange(numpy.ceil(numpy.log2(period.min())),
                               numpy.ceil(numpy.log2(period.max())))
    bx.set_yticks(numpy.log2(Yticks))
    bx.set_yticklabels(Yticks)

    # Third sub-plot, the global wavelet and Fourier power spectra and theoretical
    # noise spectra. Note that period scale is logarithmic.
    cx = pyplot.axes([0.77, 0.37, 0.2, 0.28], sharey=bx)
    cx.plot(glbl_signif, numpy.log2(period), 'k--')
    cx.plot(var * fft_theor, numpy.log2(period), '--', color='#cccccc')
    cx.plot(var * fft_power, numpy.log2(1. / fftfreqs), '-', color='#cccccc',
            linewidth=1.)
    cx.plot(var * glbl_power, numpy.log2(period), 'k-', linewidth=1.5)
    cx.set_title('c) Global Wavelet Spectrum')
    cx.set_xlabel(r'Power [({})^2]'.format(units))
    cx.set_xlim([0, glbl_power.max() + var])
    cx.set_ylim(numpy.log2([period.min(), period.max()]))
    cx.set_yticks(numpy.log2(Yticks))
    cx.set_yticklabels(Yticks)
    pyplot.setp(cx.get_yticklabels(), visible=False)


    # Third sub-plot, the global wavelet and Fourier power spectra and theoretical
    # noise spectra. Note that period scale is logarithmic.
    dx = pyplot.axes([0.1, 0.07, 0.65, 0.2])
    dx.plot(numpy.log2(fftfreqs), numpy.log2(fft_power), 'k')
    dx.plot(numpy.log2(freqs), var * fft_theor, '--', color='#cccccc')
    dx.plot(numpy.log2(1. / fftfreqs), var * fft_power, '-', color='#cccccc',
            linewidth=1.)
    dx.plot(fftfreqs, fft_power, 'k-', linewidth=1.5)
    dx.set_title('d) Global Wavelet Spectrum')
    dx.set_ylabel(r'Power [({})^2]'.format(units))
    dx.set_xlim([0, 2*fftfreqs.max()])

    Yticks = 2 ** numpy.arange(numpy.ceil(numpy.log2(fft_power.min())),
                               numpy.ceil(numpy.log2(fft_power.max())))
    dx.set_ylim(numpy.log2([fft_power.min(), fft_power.max()]))
    dx.set_yticks(numpy.log2(Yticks))
    dx.set_yticklabels(Yticks)
    pyplot.setp(dx.get_yticklabels(), visible=False)


    pyplot.show()

if __name__ == '__main__':
    # we run the split function on the result of reading a text (in this case 祝福)  using a regex with the sentence markers
    # add characters to this regex to add more sentence markers
    res = re.split('。|！|？|……', readText('乌云遇皎月'))
    finalSentences = []
    sentenceLengths = []
    # this loop removes sentences with a length of 0 if any exist
    for r in res:
        if lenSentence(r) > 0:
            finalSentences.append(r)
    for s in finalSentences:
        print(lenSentence(s))
        sentenceLengths.append(lenSentence(s))
    print(len(finalSentences))
    multifractal(sentenceLengths)

    # simple_sample(sentenceLengths)

    """
    copyFunc(sentenceLengths)
    #jieba.enable_paddle()  # 启动paddle模式。 0.40版之后开始支持，早期版本不支持
    strs = ["我来到北京清华大学", "乒乓球拍卖完了", "中国科学技术大学"]
    for str in strs:
        seg_list = jieba.cut(str, use_paddle=True)  # 使用paddle模式
        print("Paddle Mode: " + '/'.join(list(seg_list)))

    seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
    print("Full Mode: " + "/ ".join(seg_list))  # 全模式

    seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
    print("Default Mode: " + "/ ".join(seg_list))  # 精确模式

    seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
    print(", ".join(seg_list))

    seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
    print(", ".join(seg_list))
    """


