#coding=utf-8
import pandas as pd

def load_csv(filePath, select):
    """
    加载用户上传的指定格式csv文件 一个文件一条台风
    格式： id       lat     lon     intensity
    """

    file = pd.read_csv(filePath, header=None)
    return file[select]






# def detail_data(filePath):
#
#     datas = pd.read_csv(filePath,delimiter=' ')
#     select_col = [3,4]
#     next_datas = int(datas.columns[4])
#     select_lat = datas.iloc[:,select_col].astype(int)
#     # print(select_lat)
#     appen_lists = select_lat.values.T.tolist()
#     return appen_lists
