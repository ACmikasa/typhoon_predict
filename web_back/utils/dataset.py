#coding=utf-8
import torch

import numpy as np
import pandas as pd
import scipy.io as sio

from torch.utils.data import Dataset

def myload(filepath):

    data = pd.read_csv(filepath).values.tolist()
    print("读到文件没")
    print(data)

    tagID = 0
    tmplist = []
    result = []
    for one in data:
        if not tagID: tagID = one[0]
        if one[0]!=tagID:
            print(tmplist)
            result.append(np.array(tmplist))
            tagID = one[0]
            tmplist = [one]
        else:
            tmplist.append(one)

    if data[-1][0] == tagID: result.append(np.array(tmplist)) # mark 对于一个文件仅一条台风需要这一行

    print(result)
    print("=*" * 30)

    return result

class CycloneTracksDataset(Dataset):

    def __init__(self, data_path, train, window_size=4, dims=(1, 2, 3), min_=None, max_=None, device='cpu',
                 loadway=False):
        # Initialize
        super(CycloneTracksDataset, self).__init__()
        self.data_path = data_path
        self.window_size = window_size
        self.dims = dims
        self.loadway = loadway
        if train:
            self.data_split = 'train'
        else:
            self.data_split = 'test'

        # 自己的load
        self.data = myload(data_path)

        # Min-max
        self.min, self.max = min_, max_

        # Extract tensors from data
        print("way:" + data_path)
        print("data:")
        print(self.data)
        self.X, self.y, self.track_id = self.extract_data(self.data)

        # check track_id
        max_id = self.track_id.max().item()
        min_id = self.track_id.min().item()
        print(f"Track ID range: {min_id} - {max_id}")

    def create_sequences(self, X, track_id):
        # Create empyty sequences
        Xs, ys = [], []

        # Filter selected dims
        X = X[:, self.dims]

        # Scale the data
        X = self.normalize(X)

        # Add sequences to Xs and ys
        for i in range(len(X) - self.window_size):
            Xs.append(X[i: (i + self.window_size)])
            ys.append(X[i + self.window_size])

        # Track id
        track_ids = np.full(len(Xs), track_id)
        # if track_id==131 or track_id==132: print(Xs)

        # if len(Xs) < 4: return [1],[1],[1]
        return np.array(Xs), np.array(ys), track_ids

    def extract_data(self, data):

        # Min-max scaling 特征缩放至0-1
        data_stacked = np.concatenate(data, axis=0)[:, self.dims]
        # data_stacked = data

        if self.min is None:
            self.min = data_stacked.min(axis=0)
            self.max = data_stacked.max(axis=0)

        # Scale and create sequences
        data = [self.create_sequences(data[track_idx], track_id=track_idx + 1) for track_idx in range(len(data))]
        X, y, track_id = list(zip(*data))

        # if not self.loadway:
        if self.loadway:
            # X在处理过程中有空出来的, 先直接删掉
            newX = []
            newy = []
            newTrackid = []
            for one in range(len(X)):
                if len(X[one]) != 4:
                    continue
                newX.append(X[one])
                newy.append(y[one])
                newTrackid.append(track_id[one])

            # print(type(y))
            # print(type(y[6]))
            X = torch.tensor(np.concatenate(newX, axis=0)).type(torch.float)
            y = torch.tensor(np.concatenate(newy, axis=0)).type(torch.float)
            track_id = torch.tensor(np.concatenate(newTrackid, axis=0)).type(torch.int)
        else:
            # Concatenate tracks
            X = torch.tensor(np.concatenate(X, axis=0)).type(torch.float)
            y = torch.tensor(np.concatenate(y, axis=0)).type(torch.float)
            track_id = torch.tensor(np.concatenate(track_id, axis=0)).type(torch.int)
        # print(track_id)

        return X, y, track_id

    def get_track_data(self, track_id):
        """Get data for given track_id
        """
        indices = np.where(self.track_id == track_id)
        # print(f'id: {indices}')
        assert len(indices) != 0
        return self.X[indices], self.y[indices]
        # return self.X[track_id][indices], self.y[track_id][indices]

    def denormalize(self, X):
        """Unscale data to orginal scale from 0-1
        """
        return X * (self.max - self.min) + self.min

    def normalize(self, X):
        """Scale data between 0 and 1
        """
        return (X - self.min) / (self.max - self.min)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, index):
        return self.X[index].to(self.device), self.y[index].to(self.device), self.track_id[index].to(self.device)

