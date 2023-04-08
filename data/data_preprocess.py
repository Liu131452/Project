import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json

def sentence_preprocess(sentence):
    sentence = sentence.strip()
    pattern = re.compile(r"^\d+(.\d+)*")  # ^([0-9]+)(\.[0-9]+)*
    clause_number = pattern.match(sentence)
    if clause_number is not None:
        clause_number = clause_number.group()
        # print("clause_number:", clause_number)  # 条款号

        sentence1 = re.sub(pattern, "", sentence)
        sentence = sentence1.strip()
        # print("sentence1:", sentence)

    pattern1 = re.compile(r"[【\(（\[{<](.*?)[】\)）\]}>]", re.S)
    note = pattern1.search(sentence)
    if note is not None:
        note = note.group()
        # print("note:", note)  # 备注信息

        sentence2 = re.sub(pattern1, "", sentence)
        sentence = sentence2.strip()
        # print("sentence2:", sentence)

    return sentence, clause_number


def specification_analysize(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        lines = f.readlines()
        lengthList = []
        lengthList_pro = []
        for line in lines:
            line = line.strip("\n")
            lengthList.append(len(line))  # 原始长度
            # 去掉条款号及括号中的注释后，句子长度
            lengthList_pro.append(len(sentence_preprocess(line)[0]))

    y = sorted(lengthList_pro)  # 升序
    x = np.arange(0, len(y))

    """规范条文字符统计折线图"""
    plt.rcParams['font.family'] = 'Times New Roman'
    # 绘制坐标标题
    plt.title("Length_Statistics")
    # 绘制x、y轴备注
    plt.xlabel("Clause")
    plt.ylabel("Length")
    plt.plot(x, y, linestyle="dashdot", linewidth=1,
            label="Length")  # color="blue"
    plt.show()

    arry = np.array(lengthList_pro)  # 会将数组自动从小到大排序
    # 沿指定的轴计算数据的第 q 百分位数。返回数组元素的第 q 百分位数。
    percentile = np.percentile(arry, [0, 25, 50, 75, 100])
    percentile1 = np.percentile(arry, range(0, 101, 10))
    print(percentile)
    print(percentile1)

    """规范条文字符统计直方图"""
    a = np.array(lengthList_pro)
    # bin 数组中的连续元素用作每个 bin 的边界。
    hist, bins = np.histogram(
        a, [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, max(a)])
    print(hist)
    print(bins)

    nums, bins, patches = plt.hist(a, bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, max(a)], edgecolor='k',
                                histtype="bar", alpha=0.6)
    plt.title("histogram")
    plt.xticks(bins, bins)

    # plt.annotate()函数用于标注文字
    for num, bi in zip(nums, bins):
        plt.annotate("%.0f" % num, xy=(bi, num), xytext=(bi + 10, num + 10), weight='medium',
                    arrowprops=dict(facecolor="g", headlength=0.5,
                                    headwidth=0.6, width=0.6, shrink=1),
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', ec='k', lw=1, alpha=0.5))
    # plt.xlim(0)
    # plt.ylim(0)
    plt.show()


def clause_number_match(file_name):
    # 标题模式匹配
    # 一级  match pattern1 but not pattern2
    pattern1 = re.compile(r"^\d+(.\d+){0}")
    # 二级  match pattern2 but not pattern3
    pattern2 = re.compile(r"^\d+(.\d+){1}")
    # 三级   match pattern3 but not pattern4   承载内容
    pattern3 = re.compile(r"^\d+(.\d+){2}")
    pattern4 = re.compile(r"^\d+(.\d+){3}")

    # 存放标题
    Position_1 = []
    Position_2 = []
    Position_3 = []
    Position_4 = []

    with open(file_name, "r", encoding="utf-8") as f:
        for line in f.readlines():
            # line = line.strip("\n")
            title = pattern1.search(line)
            if title:
                title = pattern2.search(line)
                if not title:
                    Position_1.append(line)
                else:
                    title = pattern3.search(line)
                    if not title:
                        Position_2.append(line)
                    else:
                        title = pattern4.search(line)
                        if not title:
                            Position_3.append(line)
                        else:
                            Position_4.append(line)  # 四级标题、五级。。。（都属于复合标题）

    print("一级标题:", len(Position_1))
    print("一级标题:", len(Position_2))
    
    List1 = []
    for line in Position_4:
        title = pattern3.search(line)
        hao = title.group()
        if hao not in List1:
            List1.append(hao)
    print("父条款:", len(List1))  # 55 从252个四级标题的条款号中,分离出55个三级标题，这些三级标题属于复合型条文，四级标题为复合型子条文

    with open("复合类.txt", "w", encoding="utf-8") as f:
        for line in Position_3:
            title = pattern3.search(line)
            hao = title.group()
            if hao in List1:
                f.write(line)  # 属于复合型条文的三级标题

    return Position_1, Position_2


def sentence_filter(in_file_name, Position_1, Position_2, out_file_name=None):
    guolv = r"(.*符合.*表)|(.*式中)|(.*表.*确定.*)|^1.0.+" # [0-2]
    guolv_sentences = []

    with open(in_file_name, "r", encoding="utf-8") as f:
        for line in f.readlines():
            # line=line.strip("\n")
            cankao_search = re.search(guolv, line)
            if cankao_search:
                guolv_sentences.append(line)
                
        print("其他被过滤:", len(guolv_sentences))
        print()
        
    if out_file_name:
        with open(in_file_name, "r", encoding="utf-8") as f1:
            with open("复合类.txt", "r", encoding="utf-8") as f2:
                with open(out_file_name, "w", encoding="utf-8") as fw:
                    list_fuhe = f2.readlines()
                    for line in f1.readlines():
                        if (
                                (line in guolv_sentences)
                                or (line in Position_1)
                                or (line in Position_2)
                                or (line in list_fuhe)
                        ):
                            pass  # 跳过过滤项及标题类条款、复合类头条款（一般带冒号）
                        else:
                            fw.write(line)

    fouding = r".*不应|不得.*"
    fouding_sentences = []

    with open("test_pre.txt", "r", encoding="utf-8") as f:
        with open("否定.txt", "w", encoding="utf-8") as f1:
            for line in f.readlines():
                # line=line.strip("\n")
                _search = re.search(fouding, line)
                if _search:
                    fouding_sentences.append(line)

            for line in fouding_sentences:
                f1.write(line)
    print("否定类条款:", len(fouding_sentences))
    print()


def sentence_classify(file_name, sentence_categories, classification_rules):
    # Classification Rules matchPattern
    classification_sentences = []
    for i in range(len(sentence_categories)+1):
        classification_sentences.append([])
        
    # Classify
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f.readlines():
            line_processed = sentence_preprocess(line)[0]
            C = 0
            Flag = True
            while Flag and C < len(classification_rules):
                if re.search(classification_rules[C], line_processed):
                    classification_sentences[C].append(line)
                    Flag = False
                else:
                    C += 1
            if Flag is True:
                classification_sentences[-1].append(line)

    # Classify Results Writting
    sent_num = 0
    for i, _ in enumerate(sentence_categories):
        print("{}:".format(sentence_categories[i]), len(classification_sentences[i]))
        sent_num += len(classification_sentences[i])
        
    print("已分类条文数量:", sent_num)
    print("未分类条文数量:", len(classification_sentences[-1]))

    # 条文分类图
    plt.rc('font', family='SimSun')

    a_data = [len(i) for i in classification_sentences[:-1]]
    label_count = pd.Series(a_data, index = sentence_categories)
    label_count.plot.bar(rot=0, color=plt.cm.Paired(
    np.arange(len(label_count))))  # X轴上类别名称的旋转; 分配颜色, 相近色彩输出
    plt.show()
    

if __name__ == "__main__":
    specification_name = "原始规范文本.txt"
    specification_analysize(specification_name)
    m,n = clause_number_match(specification_name)
    sentence_filter(specification_name, m, n, out_file_name=None)
    
    def read_config():
        with open(r"../config.json",encoding="utf-8") as json_file:
            config = json.load(json_file)
        return config

    config = read_config() # 读取配置文件

    sentence_categories = config["categories"]
    classification_rules = [v for _, v in config["regex rules"].items()]
    
    # 条文分类
    file_name = "test_pre.txt"
    sentence_classify(file_name, sentence_categories, classification_rules)
    