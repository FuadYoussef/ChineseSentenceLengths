import re

# encoding=utf-8
# all of the logic for reading a text to get the sentence lengths should be in this file

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
        if is_cjk(
                c) and c != "，" and c != "“" and c != " " and c != "：" and c != "；" and c != "-" and c != "\n" and c != "\t":
            strLen += 1
    return strLen


# a boolean function that checks if a given character is a Chinese character or not by seeing if it is within the
# ranges defined earlier
def is_cjk(char):
    char = ord(char)
    for bottom, top in cjk_ranges:
        if char >= bottom and char <= top:
            return True
    return False


def getSentenceLengths(title):
    # we run the split function on the result of reading a text using a regex with the sentence markers
    # add characters to this regex to add more sentence markers
    res = re.split('。|！|？|……', readText(title))
    finalSentences = []
    sentenceLengths = []
    # this loop removes sentences with a length of 0 if any exist
    for r in res:
        if lenSentence(r) > 0:
            finalSentences.append(r)
    for s in finalSentences:
        sentenceLengths.append(lenSentence(s))
    return sentenceLengths

def lenSentenceEnglish(sentence):
    sentences = sentence.split(" ")
    #print(sentences)
    #print(len(sentences))
    return len(sentences)

def getSLEnglish(title):
    # res = re.split(".", readText(title))
    res = readText(title).split('.')
    # print(res)
    finalSentences = []
    sentenceLengths = []
    for r in res:
        if lenSentenceEnglish(r) > 0:
            finalSentences.append(r)
    for s in finalSentences:
        sentenceLengths.append(lenSentenceEnglish(s))

    # print(sentenceLengths)
    return sentenceLengths