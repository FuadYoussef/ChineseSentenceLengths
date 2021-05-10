import re

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

def readText(name):
    f = open(name + ".txt", "r", encoding='utf-8')
    text = f.read()
    f.close()
    return text

def lenSentence(sentence):
    strLen = 0
    for c in sentence:
        if is_cjk(c) and c != "，" and c != "“" and c != " " and c != "……" and c != "\n" and c != "\t":
            strLen += 1
    return strLen

def is_cjk(char):
    char = ord(char)
    for bottom, top in cjk_ranges:
        if char >= bottom and char <= top:
            return True
    return False


if __name__ == '__main__':
    test_str = "我正。在！做？一个，考。试。"
    res = re.split('。|！|？', readText('祝福'))
    for r in res:
        print(lenSentence(r))
    print(len(res))


