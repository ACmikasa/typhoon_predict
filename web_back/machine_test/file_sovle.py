import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,MinMaxScaler
import select_typhoon
def Processing_data():
    data_all = pd.read_csv("typhoon.csv")
    data_all["中心位置"] = data_all["中心位置"].str.replace("°E","").str.replace("°N","")
    target_data = data_all["中心位置"].str.replace("|","").str.replace(".","")
    data_all["中心位置"] = data_all["中心位置"].str.split("|")
    data_all["时间"] = data_all["时间"].str.replace(":","")
    lat = []
    lng = []
    for data in data_all["中心位置"]:
        lat.append(data[0])
        lng.append(data[1])
    
    # data_all.loc[:,"lat"] = lat
    # data_all.loc[:,"lng"] = lng
    data_all.loc[:,"target"] = target_data
    data_all = data_all.drop("中心位置",axis=1)
    return data_all

def Strand_data(data):
    for col in data.columns:
        data[col] = data[col].astype(float)
    Stand_transform = StandardScaler()
    the_data = Stand_transform.fit_transform(data)
    return the_data




if __name__ == "__main__":
    name = select_typhoon.get_typhoon_name()
    # select_typhoon.get_message("三巴")
    # data = Processing_data()
    # print(data)
    # stand_data = Strand_data(data)
    # print(stand_data)
    print_data()