# ================爬虫爬取气象站===============
from selenium import webdriver
from translate import Translator
import pandas as pd

firFox = webdriver.Firefox(executable_path='./tool/geckodriver.exe')
firFox.get('http://tf.tianqi.com/')

Ty_detail = firFox.find_element_by_class_name("tfxq")
Ty_detail.click()

def get_message(typoon_names):

    firFox.find_elements_by_id('TypoonList')
    tbody_ = firFox.find_element_by_tag_name('tbody')
    
    trs = tbody_.find_elements_by_tag_name("tr")
    
    for i in range(1,len(trs)+1):
        td = firFox.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[{}]/td[3]".format(i))
        try:
            find_td_class_name = firFox.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[{}]".format(i))
            td_class_name = find_td_class_name.get_attribute("class")
            for typoon_name in typoon_names:
                if (td.text == typoon_name):
                    if(td_class_name == "active"):
                        name_find()
                    else:
                        input_click = firFox.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[{}]/td[1]/input".format(i))
                        input_click.click()
                        name_find()

            
        except:
            print("null of message  "+ str(typoon_names))
    
    firFox.quit()

          
def name_find():
    mes = firFox.find_elements_by_class_name('tf_name')
    for name in mes:
        print(name.text)
    tbody_ = firFox.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div[2]/div[1]/div[2]/div/table/tbody")
    trs = tbody_.find_elements_by_tag_name("tr")
    with open("typhoon.csv","w",encoding="utf-8") as f:
        for tr in trs:
            tr = tr.text.replace(" ",",")
            f.write(tr+"\n")



def get_typhoon_name():
    typhoon_list = []
    firFox.find_elements_by_id('TypoonList')
    tbody_ = firFox.find_element_by_tag_name('tbody')
    trs = tbody_.find_elements_by_tag_name("tr")
    for i in range(2,len(trs)+1):
        td = firFox.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[{}]/td[3]".format(i))
        typhoon_list.append(td.text)
    
    return typhoon_list


def file_data_solve():
    data = pd.read_csv("typhoon.csv",encoding="utf-8")
    E_ = [] #坐标
    N_ = [] #坐标
    the_center = data["中心位置"].str.split("|")[:50]
    for i in the_center:
        E_.append(i[0][:-2])
        N_.append(i[1][:-2])
    return [E_,N_]
        
if __name__== "__main__":
    data = get_typhoon_name()
    get_message(data)
