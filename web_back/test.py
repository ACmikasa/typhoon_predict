
import pandas as pd


# from select_typhoon import get_message

# get_message("海葵")

def print_data():
    the_data = []
    data_all = pd.read_csv("typhoon.csv")
    for data in range(0,data_all.shape[0]):
        the_list = []
        the_list.append(data_all['时间'][data])
        the_list.append(data_all['中心位置'][data])
        the_list.append(data_all['最大风速(m/s)'][data])
        the_list.append(data_all['最低气压(pa)'][data])
        the_data.append(the_list)
        
    print(the_data)
        
print_data()