from collections import Counter

import jieba.analyse
import numpy as np
from scipy.stats import chi2_contingency

class_list = {'财经': 'Economics', '房产': 'House', '股票': 'Stock', '家居': 'Household', '教育': 'Education', '科技': 'Technology',
              '时政': 'Politics', '体育': 'PE', '游戏': 'Game', '娱乐': 'Entertainment'}
contents = {}
word_counters = {}


def init():
    for CLASS_NAME_EN in class_list.values():
        with open('data_train/' + CLASS_NAME_EN + '/all.txt', 'r', encoding='utf-8') as file:
            contents[CLASS_NAME_EN] = ''.join(file.readlines())
            # 实际上，基于Counter数据结构的word_counter就是词频统计结果
            word_counters[CLASS_NAME_EN] = Counter(contents[CLASS_NAME_EN].split())


def chi_square(word: str, class_str: str):
    parm_A = 0
    parm_B = 0
    parm_C = 0
    parm_D = 0
    for CLASS_NAME_EN in class_list.values():
        with open('data_train/' + CLASS_NAME_EN + '/all.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # all文件中，一行代表一个文件
            if CLASS_NAME_EN == class_str:
                for j in lines:
                    if word in j.split():
                        parm_A += 1
                    else:
                        parm_C += 1
            else:
                for j in lines:
                    if word in j.split():
                        parm_B += 1
                    else:
                        parm_D += 1
    # print('chisq-statistic=%.4f, p-value=%.4f, df=%i expected_frep=%s' % kf)
    # 仅需返回p值，p值越小，相关性越显著，p值越大，差异越显著，显然，p值越大说明该词在该类中越关键
    if parm_B == 0:
        return 1
    return chi2_contingency(np.array([[parm_A, parm_B], [parm_C, parm_D]]))[1]


if __name__ == '__main__':
    init()
    # 先利用jieba内置的TF/IDF方法加权，得到前1000个关键词(得到1000*2的一个矩阵)，其权值再与卡方检验值相乘，排序后的前500个词为关键词
    for class_name_en in class_list.values():
        topK = 1000
        if len(word_counters[class_name_en]) < 1000:
            topK = len(word_counters[class_name_en])
        tags = jieba.analyse.extract_tags(contents[class_name_en], topK=topK,
                                          withWeight=True)
        tags_dic = dict(tags)
        index = 0
        for tag, value in tags_dic.items():
            print("class: %s index: %d tag: %s\t\t weight: %f" % (class_name_en, index, tag, value))
            index += 1
            tags_dic[tag] = value * chi_square(tag, class_name_en)
        key_words = Counter(tags_dic).most_common(500)
        with open('data_train/' + class_name_en + '/dict.txt', 'w', encoding='utf-8') as f:
            for i in key_words:
                f.write(i[0] + ':' + str(i[1]) + '\n')