import librosa.feature
import numpy as np
import torch
from torch import nn

from pipeline.data_util import get_seq


class Rnn(nn.Module):
    def __init__(self):
        super(Rnn, self).__init__()
        self.gru = nn.GRU(600, 32, bidirectional=True, batch_first=True)
        self.linear = nn.Linear(32 * 2, 64)

    def forward(self, x):
        x, _ = self.gru(x)
        out = self.linear(x[-1, :])
        return out


class Cnn(nn.Module):
    def __init__(self):
        super(Cnn, self).__init__()
        self.conv1 = nn.Conv2d(3, 4, kernel_size=3, padding=1)
        self.act1 = nn.ReLU()
        self.bn1 = nn.BatchNorm2d(4)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv2 = nn.Conv2d(4, 4, kernel_size=3, padding=1)
        self.act2 = nn.ReLU()
        self.bn2 = nn.BatchNorm2d(4)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv3 = nn.Conv2d(4, 8, kernel_size=3, padding=1)
        self.act3 = nn.ReLU()
        self.bn3 = nn.BatchNorm2d(8)

        self.conv4 = nn.Conv2d(8, 8, kernel_size=3, padding=1)
        self.act4 = nn.ReLU()
        self.bn4 = nn.BatchNorm2d(8)
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv5 = nn.Conv2d(8, 16, kernel_size=3, padding=1)
        self.act5 = nn.ReLU()
        self.bn5 = nn.BatchNorm2d(16)

        self.conv6 = nn.Conv2d(16, 16, kernel_size=3, padding=1)
        self.act6 = nn.ReLU()
        self.bn6 = nn.BatchNorm2d(16)
        self.pool6 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv7 = nn.Conv2d(16, 24, kernel_size=3, padding=1)
        self.act7 = nn.ReLU()
        self.bn7 = nn.BatchNorm2d(24)

        self.conv8 = nn.Conv2d(24, 24, kernel_size=3, padding=1)
        self.act8 = nn.ReLU()
        self.bn8 = nn.BatchNorm2d(24)
        self.pool8 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.fc = nn.Linear(117120 // 4, 64)

    def forward(self, x):
        x = x.unsqueeze(0)
        x = x.detach().cpu().numpy()
        x = librosa.feature.melspectrogram(y=x, sr=200, n_mels=128)
        x = torch.tensor(x)
        x = x.expand(x.shape[0], 3, -1, -1)

        x = self.conv1(x)
        x = self.act1(x)
        x = self.bn1(x)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.act2(x)
        x = self.bn2(x)
        x = self.pool2(x)

        x = self.conv3(x)
        x = self.act3(x)
        x = self.bn3(x)

        x = self.conv4(x)
        x = self.act4(x)
        x = self.bn4(x)
        x = self.pool4(x)

        x = self.conv5(x)
        x = self.act5(x)
        x = self.bn5(x)

        x = self.conv6(x)
        x = self.act6(x)
        x = self.bn6(x)
        x = self.pool6(x)

        x = self.conv7(x)
        x = self.act7(x)
        x = self.bn7(x)

        x = self.conv8(x)
        x = self.act8(x)
        x = self.bn8(x)
        x = self.pool8(x)

        x = x.view(x.shape[0], -1)
        out = self.fc(x)
        return out


class ConcatBlockCls(nn.Module):
    def __init__(self):
        super(ConcatBlockCls, self).__init__()
        self.cnn_model = Cnn()
        self.rnn_model = Rnn()
        self.regression = nn.Linear(128, 64)

    def forward(self, x):
        x1 = self.cnn_model(x)
        x = torch.tensor(np.array(get_seq(x, 600, 200)))
        x2 = self.rnn_model(x).unsqueeze(0)
        out = self.regression(torch.cat([x1, x2], dim=1))
        return out


class ConcatBlockReg(nn.Module):
    def __init__(self):
        super(ConcatBlockReg, self).__init__()
        self.rnn_model = Rnn()
        self.regression = nn.Linear(64, 64)

    def forward(self, x):
        x = torch.tensor(np.array(get_seq(x, 600, 200)))
        x2 = self.rnn_model(x)
        out = self.regression(x2)
        return out


class Classificator(nn.Module):
    def __init__(self):
        super(Classificator, self).__init__()
        self.blocks = nn.ModuleList([ConcatBlockCls() for _ in range(6)])
        self.table_regression = nn.Sequential(nn.LayerNorm(8),
                                              nn.Linear(8, 64),
                                              nn.ReLU(),
                                              nn.Dropout(0.3),
                                              nn.Linear(64, 64),
                                              nn.Dropout(0.4))
        self.output_regression = nn.Sequential(nn.LayerNorm(128),
                                               nn.Linear(128, 32),
                                               nn.ReLU(),
                                               nn.Dropout(0.3),
                                               nn.Linear(32, 32),
                                               nn.LayerNorm(32),
                                               nn.ReLU(),
                                               nn.Dropout(0.2),
                                               nn.Linear(32, 1))

    def forward(self, x_table, x_channels):
        channels_out = torch.zeros((1, 64))
        for channel in range(6):
            if x_channels[channel, :].sum() == 0:
                continue
            channels_out += self.blocks[channel](x_channels[channel, :])

        table_out = self.table_regression(x_table)
        out = self.output_regression(torch.cat([channels_out, table_out.unsqueeze(0)], dim=1))
        return torch.nn.Sigmoid()(out)


class Regression(nn.Module):
    def __init__(self):
        super(Regression, self).__init__()
        self.blocks = nn.ModuleList([ConcatBlockReg() for _ in range(6)])
        self.table_regression = nn.Sequential(nn.LayerNorm(8),
                                              nn.Linear(8, 32),
                                              nn.ReLU(),
                                              nn.Dropout(0.3),
                                              nn.Linear(32, 64),
                                              nn.Dropout(0.4))
        self.output_regression = nn.Sequential(nn.LayerNorm(128),
                                               nn.Linear(128, 32),
                                               nn.ReLU(),
                                               nn.Dropout(0.3),
                                               nn.Linear(32, 32),
                                               nn.LayerNorm(32),
                                               nn.ReLU(),
                                               nn.Dropout(0.2),
                                               nn.Linear(32, 1))

    def forward(self, x_table, x_channels):
        channels_out = torch.zeros((1, 64))
        for channel in range(6):
            if x_channels[channel, :].sum() == 0:
                continue
            channels_out += self.blocks[channel](x_channels[channel, :])

        table_out = self.table_regression(x_table)
        out = self.output_regression(torch.cat([channels_out, table_out.unsqueeze(0)], dim=1))
        return out

