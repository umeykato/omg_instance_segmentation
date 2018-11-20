"""
This implementation is based on following code:
https://github.com/milesial/Pytorch-UNet
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np


class double_conv(nn.Module):
    '''(conv => BN => ReLU) * 2'''
    def __init__(self, in_ch, out_ch):
        super(double_conv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        x = self.conv(x)
        return x


class inconv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(inconv, self).__init__()
        self.conv = double_conv(in_ch, out_ch)

    def forward(self, x):
        x = self.conv(x)
        return x


class down(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(down, self).__init__()
        self.mpconv = nn.Sequential(
            nn.MaxPool2d(2),
            double_conv(in_ch, out_ch)
        )

    def forward(self, x):
        x = self.mpconv(x)
        return x


class up(nn.Module):
    def __init__(self, in_ch, out_ch, bilinear=True):
        super(up, self).__init__()

        #  would be a nice idea if the upsampling could be learned too,
        #  but my machine do not have enough memory to handle all those weights
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear')
        else:
            self.up = nn.ConvTranspose2d(in_ch, out_ch, 2, stride=2)

        self.conv = double_conv(in_ch, out_ch)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        diffX = x1.size()[2] - x2.size()[2]
        diffY = x1.size()[3] - x2.size()[3]
        x2 = F.pad(x2, (diffX // 2, int(diffX / 2),
                        diffY // 2, int(diffY / 2)))
        x = torch.cat([x2, x1], dim=1)
        x = self.conv(x)
        return x


class outconv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(outconv, self).__init__()
        # self.conv = nn.Conv2d(in_ch, out_ch, 1)
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, in_ch//2, 1),
            nn.BatchNorm2d(in_ch//2),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_ch//2, out_ch, 1),
        )

    def forward(self, x):
        x = self.conv(x)
        return x

class outlinear(nn.Module):
    def __init__(self, in_ch, out_ch, img_size=256):
        super(outlinear, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, 1, 1),
            nn.BatchNorm2d(1),
            nn.ReLU(inplace=True),
        )
        self.linear = nn.Sequential(
            # nn.Linear(256*256, 4096),
            nn.Linear(img_size*img_size, 4096),
            nn.ReLU(inplace=True),
            # nn.Linear(4096, 4096),
            # nn.ReLU(inplace=True),
            nn.Linear(4096, out_ch),
        )

    def forward(self, x):
        x = self.conv(x)
        # print(x.size())
        x = x.view(x.size(0), -1)
        # print(x.size())
        x = self.linear(x)
        return x

class UNet(nn.Module):
    def __init__(self, img_size=256):
        super(UNet, self).__init__()
        # self.inc = inconv(1, 64)
        self.inc = inconv(3, 64)
        self.down1 = down(64, 128)
        self.down2 = down(128, 256)
        self.down3 = down(256, 512)
        self.down4 = down(512, 512)
        self.up1 = up(1024, 256)
        self.up2 = up(512, 128)
        self.up3 = up(256, 64)
        self.up4 = up(128, 64)
        self.sem_out = outconv(64, 2)
        # self.ins_out = outconv(64, 16)
        self.ins_out = outconv(64, 60)
        self.spline_out = outlinear(64, 60 * 8 * 2, img_size)

    def forward(self, x):
        x1 = self.inc(x)
        # print('x1 : ', x1.size())
        x2 = self.down1(x1)
        # print('x2 : ', x2.size())
        x3 = self.down2(x2)
        # print('x3 : ', x3.size())
        x4 = self.down3(x3)
        # print('x4 : ', x4.size())
        x5 = self.down4(x4)
        # print('x5 : ', x5.size())
        x = self.up1(x5, x4)
        # print('x : ', x.size())
        x = self.up2(x, x3)
        # print('x : ', x.size())
        x = self.up3(x, x2)
        # print('x : ', x.size())
        x = self.up4(x, x1)
        # print('x : ', x.size())
        sem = self.sem_out(x)
        # print('sem : ', sem.size())
        ins = self.ins_out(x)
        # print('ins : ', ins.size())
        spline = self.spline_out(x)
        return sem, ins, spline

if __name__=='__main__':
    model = outlinear(64, 60 * 8 * 2)

    a = np.empty((1, 64, 256, 256))
    b = model.forward(torch.Tensor(a))

    print(b.shape)