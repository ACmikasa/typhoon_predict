# import numpy as np


import torch
import torch.nn as nn
class LSTM_RNN(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_size = [128, 32, 8], num_layers = 3):
        super(LSTM_RNN, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_sizes = hidden_size

        self.num_layers = len(hidden_size)
        self.lstm_layers = nn.ModuleList([
            nn.LSTM(input_dim, hidden_size[0], batch_first=True)
        ])
        self.lstm_layers.extend([
            nn.LSTM(hidden_size[i-1], hidden_size[i], batch_first=True)
            for i in range(1, self.num_layers)
        ])
        self.fc = nn.Linear(hidden_size[-1], output_dim)

    def forward(self, x, sampling=False):
        h = [torch.zeros(x.size(0), self.hidden_sizes[i]) for i in range(self.num_layers)]
        c = [torch.zeros(x.size(0), self.hidden_sizes[i]) for i in range(self.num_layers)]
        
        for i in range(self.num_layers):
            x, (h[i], c[i]) = self.lstm_layers[i](x, (h[i].unsqueeze(0), c[i].unsqueeze(0)))
        
        out = self.fc(x[:, -1, :])
        # return out
        if sampling:
            return out
        else:
            return torch.sigmoid(out)

