import jieba
import numpy as np
import matplotlib.pyplot as plt
# encoding=utf-8

# this file contains unused code taken from Dr. Yuan's document. If we decide we need it, we can reference it later



def copyFunc(y):
    x = np.linspace(0, 1, len(y))
    p = np.poly1d(np.polyfit(x, y,3))  # fitting to a 3rd degree polynomial
    t = np.linspace(0, 1, 200)
    plt.plot(x, y, 'o-', t, p(t), '-')
    plt.show()


    # plot sentence lengths with fitted curve

def paddleTest():
   # jieba.enable_paddle()  # 启动paddle模式。 0.40版之后开始支持，早期版本不支持
   # paddle.enable_static()
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

def splitSentencesByWords(sentences):
    for sentence in sentences:
        seg_list = jieba.cut(sentence, use_paddle=True)  # 使用paddle模式
        print("Paddle Mode: " + '/'.join(list(seg_list)))