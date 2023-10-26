import torch
import torch.nn as nn

from ..utils.layers import BayesLinear

class LSTM_RNN(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=[128, 32, 8], batch_size=1024):
        super(LSTM_RNN, self).__init__()
         # Intialize dimensions -- 为了兼容
        self.batch = batch_size
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # Weights
        self.w_ih = BayesLinear(input_dim, hidden_dim[0])
        self.w_hh1 = BayesLinear(hidden_dim[0], hidden_dim[1])
        self.w_hh2 = BayesLinear(hidden_dim[1], hidden_dim[2])
        self.w_ho = BayesLinear(hidden_dim[2], output_dim)

        # self.hidden_sizes = hidden_dim
        self.num_layers = len(hidden_dim)
        self.lstm_layers = nn.ModuleList()
        self.lstm_layers.append(nn.LSTM(input_dim, hidden_dim[0], batch_first=True)) 
        self.dropout = nn.Dropout(p=0.1)
        for i in range(1, self.num_layers):
            self.lstm_layers.append(nn.LSTM(hidden_dim[i-1], hidden_dim[i], batch_first=True))
        self.fc = nn.Linear(self.hidden_dim[-1], output_dim) 

    def forward(self, x, sampling=False):

        # h0 = self.init_zero_hidden(self.hidden_dim[0]).to(x.device)
        # c0 = self.init_zero_hidden(self.hidden_dim[0]).to(x.device)
        h0 = torch.zeros(1, x.size(0), self.hidden_dim[0]).to(x.device)
        c0 = torch.zeros(1, x.size(0), self.hidden_dim[0]).to(x.device)

        # print(f'layering : {self.lstm_layers}')
        # print(h0)
        # print(len(h0[0][0]))
        out, (hn, cn) = self.lstm_layers[0](x, (h0, c0))
        for i in range(1, self.num_layers):
            out = self.dropout(out)
            # print(f'now layer: {i}')
            # print(hn)
            # print(len(hn[0][0]))
            # print(i)
            # out, (hn, cn) = self.lstm_layers[i]((hn.unsqueeze(0), cn.unsqueeze(0)))
            out, (hn, cn) = self.lstm_layers[i](out)
        out = self.dropout(out) # 观察是否结果会变差
        out = self.fc(out[:, -1, :])
        return out
    
    def init_zero_hidden(self, hidden, batch_size=1024) -> torch.Tensor:
        """
                Helper function.
        Returns a hidden state with specified batch size. Defaults to 1
        """
        return torch.zeros(1, batch_size, hidden, requires_grad=False)
    
    def log_prior(self):
        return (
            self.w_ih.log_prior + 
            self.w_hh1.log_prior + 
            self.w_hh2.log_prior + 
            self.w_ho.log_prior
        )
    
    def log_variational_posterior(self):
        return (
            self.w_ih.log_variational_posterior + 
            self.w_hh1.log_variational_posterior +
            self.w_hh2.log_variational_posterior +
            self.w_ho.log_variational_posterior
        )