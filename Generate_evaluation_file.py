import pandas as pd


def generate_assessment_file(_in_file, _out_file):
    Sentences = []
    SRL = []
    tag_srl = False
    srl = ""

    with open(_in_file, mode='r', encoding='utf-8') as f:
        for i in f:  # 直接遍历法
            if i:
                if i == "@开始\n":
                    tag_srl = False
                    if srl:  # 写入srl
                        srl = srl.strip()
                        # print(srl)
                        SRL.append(srl)
                    continue
                else:
                    if not tag_srl:
                        # 写入句子
                        # print(i)
                        i = i.strip()
                        Sentences.append(i)
                        tag_srl = True
                        srl = ""
                    else:
                        srl += i
        srl = srl.strip()
        # print(srl)
        SRL.append(srl)

    df = pd.DataFrame()
    df["Sentences"] = Sentences
    df["SRL Results"] = SRL
    df["正确/错误/遗漏"] = ""
    df.to_excel(_out_file, sheet_name="Sheet1", index=False, encoding='utf-8')


if __name__ == '__main__':
    in_file = r'IE记录.log'  # print 定向输出到 log 日志文件
    out_file = r"IE记录.xlsx"
    generate_assessment_file(in_file, out_file)
