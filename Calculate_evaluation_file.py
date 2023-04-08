import pandas as pd
import numpy as np


def calculate_assessment_file(_in_file, split_symbol=","):
    df = pd.read_excel(_in_file)
    df = df["正确/错误/遗漏"]
    df.dropna(axis=0, inplace=True)
    df_array = np.array(df)      # 将df转化为array
    df_list = df_array.tolist()  # 转化为list形式
    list1 = [i.strip("'") for i in df_list]

    list_correct = [eval(i.split(split_symbol)[0]) for i in list1]
    list_error = [eval(i.split(split_symbol)[1]) for i in list1]
    list_lost = [eval(i.split(split_symbol)[2]) for i in list1]

    TP, FP, FN = sum(list_correct), sum(list_error), sum(list_lost)
    Precision = TP / (TP + FP)
    Recall = TP / (TP + FN)
    F1_score = 2 * Precision * Recall / (Precision + Recall)

    print(TP, FP, FN)
    print(Precision, Recall, F1_score)  # 精确率、召回率、F1_score


if __name__ == '__main__':
    in_file = r'IE记录1.xlsx' # 人工评估后的文件
    calculate_assessment_file(in_file)
