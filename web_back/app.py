import os
import pandas as pd
import csv
import torch
from flask import Flask, request,jsonify
from flask_cors import CORS
from solve_file import load_csv
from werkzeug.utils import secure_filename
from utils.dataset import CycloneTracksDataset
from utils.markov_sampler import MarkovSamplingLoss

from selenium import webdriver

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = r'C:\Users\DELL\Desktop\typhoon_predict\web_back\static\files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def read_user_data():
    with open("/home/wf/gxb/user/data.txt", "r") as f:
        line = f.readline().strip()
        username, password = line.split(" ")
        return username, password

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("name")
    password = data.get("pwd")

    true_username, true_password = read_user_data()

    if username == true_username and password == true_password:
        return jsonify(status='success')
    else:
        return jsonify(status='fail')


# 获取Message信息
@app.route('/get_message', methods=['GET'])
def get_message():
    result_list = []
    try:
        with open('/home/wf/gxb/out/coordinates.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(',')
                station_date_str = parts[0]
                time_range = parts[1].replace(" S", "")
                freq_range = parts[2].replace(" HZ", "")
                
                station, date_str = station_date_str.split("_")[0:2]
                formatted_date = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:8]}"
                result_list.append([station, formatted_date, time_range, freq_range])
        file.close()
    except:
        print("noen of this txt")
    return jsonify({'data': result_list})




# 文件上传接口


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024  # Max upload size: 16MB


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    print(request)
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        print(filename)
        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename})

@app.route('/send_data',methods = ['GET'])
def get_data():
    filePath = UPLOAD_FOLDER
    files = os.listdir(filePath)
    return jsonify({"file":files})

CORS(app,origins="*")




# 文件处理 文件夹管理部分
@app.route('/post_file',methods = ['POST'])
def post_file():
    rightfiles = []
    leftfiles = []
    path = UPLOAD_FOLDER # 注意最后路径加个/
    filelist = os.listdir(path)
    dicfiles = filelist
    data = request.json.get('rightValue')
    print(data)
    try:
        for file in data:
            rightfiles.append(file['label'])
        set_right = set(rightfiles)
        set_total = set(dicfiles)
        difference_files = set_total.difference(set_right)
        if difference_files:
            leftfiles = list(difference_files)
            print("left files : ",leftfiles)
            print("right files is : ",rightfiles)
        app.right = rightfiles
        app.left = leftfiles
    except:
        for leftfile in dicfiles:
            leftfiles.append(leftfile)
            app.left = leftfiles
        print("app.left : ",app.left)
    return jsonify(data),200


@app.route("/del_file",methods=['POST'])
def del_files():
    path = UPLOAD_FOLDER
    print(app.left)
    try:
        for file in app.left:
            file_path = os.path.join(path, file)
            os.remove(file_path)
        print("移除:")
    except:
        print("没有移除？")
    
    return jsonify(path),200

# 开始识别接口
@app.route('/progress')
def progress():
    pass


@app.route("/typhoon_messge")
def Processing_data():
    
    the_data = []
    data_all = pd.read_csv("typhoon.csv")
    for data in range(0,data_all.shape[0]):
        the_list = []
        the_list.append(data_all['时间'][data])
        the_list.append(data_all['中心位置'][data])
        the_list.append(int(data_all['最大风速(m/s)'][data]))
        the_list.append(int(data_all['最低气压(pa)'][data]))
        the_data.append(the_list)
        
    
    return jsonify({"data":the_data}),200


@app.route("/typhoon_latLen")
def Lat_len():
    
    data_all = pd.read_csv(f"typhoon.csv")
    data_all["中心位置"] = data_all["中心位置"].str.replace("°E","").str.replace("°N","")
    
    data_all["中心位置"] = data_all["中心位置"].str.split("|")
    data_all["时间"] = data_all["时间"].str.replace(":","")
    lat = []
    lng = []
    for data in data_all["中心位置"]:
        lat.append(data[0])
        lng.append(data[1])
    
    return jsonify([lat,lng]),200

if __name__ == '__main__':
    app.run(debug=True)

