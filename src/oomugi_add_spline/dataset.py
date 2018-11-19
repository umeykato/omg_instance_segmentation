import numpy as np
import cv2
import glob
import os

import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader


class SSSDataset(Dataset):
    def __init__(self, train, n_sticks=8, data_size=5000):
        super().__init__()
        self.train = train
        self.n_sticks = n_sticks
        self.data_size = data_size
        self.height = 256
        self.width = 256

        # #ver1.0
        # self.img_path = 'I:/ykato_git/datasets/oomugi_blender/train/o/20/'
        # self.sem_path = 'I:/ykato_git/datasets/oomugi_blender/train/f/20/'
        # self.ins_path = 'I:/ykato_git/datasets/oomugi_blender/train/s/20/'

        #ver2.0
        # self.img_path = 'I:/ykato_git/datasets/oomugi_blender/train2/image/'
        # self.sem_path = 'I:/ykato_git/datasets/oomugi_blender/train2/semantic/'
        # self.ins_path = 'I:/ykato_git/datasets/oomugi_blender/train2/instance/'
        # self.spline_path = 'I:/ykato_git/datasets/oomugi_blender/train2/spline/'
        
        # ver3.0
        root = '../../../datasets/oomugi_blender/dataset_ver3/dataset_SemInsSpline'
        self.img_path = root + '/image/'
        self.sem_path = root + '/semantic/'
        self.ins_path = root + '/instance_segment/'
        self.spline_path = root + '/spline/'

        self.png_name = os.listdir(self.img_path)


    def __len__(self):
        return self.data_size

    '''
    img (ch=1, height, width)
        白背景に全スティック領域の黒枠（前後関係を考慮済み）
    sem (ch=1, height, width)
        背景0 スティック領域1
    ins (ch=スティックの本数, height, width)
        背景0 スティック領域1，スティック本数を８に固定
    

    変更後
    img オオムギ画像 3ch
    sem オオムギ領域画像 1ch
    ins 大麦オブジェクト画像，オブジェクト数30～60 = 30~60ch
    spline (葉60本×8点(制御点数)×2点(x,y)) = 960
    '''

    def __getitem__(self, index):
        
        # print(self.png_name[index])

        # カラー画像と同サイズのarray生成
        img = np.ones((3, self.height, self.width), dtype=np.uint8)
        # カラー画像読み込み
        img_temp = cv2.imread(self.img_path + self.png_name[index])
        # カラー画像リサイズ
        img_temp = cv2.resize(img_temp, (self.height, self.width), interpolation= cv2.INTER_NEAREST)
        # デバッグ保存
        # cv2.imwrite('./img_temp.png', img_temp)
        # カラー画像トランスポーズ
        img = img_temp.transpose(2, 0, 1)

        # instance画像と同サイズのarray生成（ｃｈ数＝最大オブジェクト数）
        ins = np.zeros((60, self.height, self.width), dtype=np.uint8)
        # instance画像のパス生成
        ins_dir = self.ins_path + self.png_name[index].rstrip('.png') + '/'
        # オブジェクト数を格納
        ins_num = len(os.listdir(ins_dir))
        # 現在のオブジェクト数初期化
        object_num = 0
        # 白色画像生成
        ins_one = np.ones((self.height, self.width), dtype=np.uint8) * 255

        # instance画像をnumpyに格納
        for i in range(1, ins_num):
            # instance画像生成
            ins_temp = cv2.imread(ins_dir + '{}.png'.format(i), 0)
            # デバッグ用
            # cv2.imwrite('./ins_{}_org.png'.format(i), ins_temp)
            # instance画像リサイズ
            ins_temp = cv2.resize(ins_temp, (self.height, self.width), interpolation= cv2.INTER_NEAREST)
            # リサイズした画像にラベルとなる部分が残っていれば
            if(np.sum(ins_temp == ins_one) != 0):
                # デバッグ用
                # cv2.imwrite('./ins_{}.png'.format(object_num), ins_temp)
                # 255で割って正規化したやつを（現在のオブジェクト数）chとして代入
                ins[object_num] = ins_temp / 255
                # 現在のオブジェクト数をインクリメント
                object_num += 1

        # semantic画像と同サイズarrayを生成
        sem = np.zeros((self.height, self.width), dtype=bool)
        # instanceで塗った所をラベル（True）にする
        sem[np.sum(ins, axis=0) != 0] = True
        # デバッグ用
        # cv2.imwrite('./sem_temp.png', sem.astype(np.uint8)*255)
        # semantic画像と反転した画像(2ch)の配列にする
        sem = np.stack([~sem, sem]).astype(np.uint8)

        # splineのarrayを生成 8*60*2
        spline = np.zeros((960), dtype=np.float32)
        # ８点のply読み込み
        num = 0
        for line in open(self.spline_path + self.png_name[index].replace('.png', '.txt')):
            spline[num] = float(line)
            # print(float(line))
            num += 1
        spline = spline.reshape((60, 8, 2))

        # print('obj_num', ins_num)
        # print('spline_num', num//16)

        spline /= 500.0


        # splineの形に成形
        # [[x1, y2],        
        #  [x2, y2],        
        #  ,          -->   [x1, y1, x2, y2,,, xn, yn]
        #  ,                
        #  [xn, yx]]

        # 3 * height * width
        img = torch.Tensor(img.astype(np.uint8))
        # 2 * height * width
        sem = torch.Tensor(sem)
        # 60 * height * width
        ins = torch.Tensor(ins) 
        # 960
        spline = torch.Tensor(spline)

        return img, sem, ins, object_num, spline, num//16




        ###############################################################

        # while True:
        #     img = np.ones((self.height, self.width), dtype=np.uint8) * 255
        #     ins = np.zeros((0, self.height, self.width), dtype=np.uint8)
        #     for _ in range(self.n_sticks):
        #         x = np.random.randint(30, 225)
        #         y = np.random.randint(30, 225)
        #         w = 15
        #         h = np.random.randint(80, 100)
        #         theta = np.random.randint(-90, 90)
        #         rect = ([x, y], [w, h], theta)
        #         box = np.int0(cv2.boxPoints(rect))

        #         gt = np.zeros_like(img)
        #         gt = cv2.fillPoly(gt, [box], 1)
        #         ins[:, gt != 0] = 0
        #         ins = np.concatenate([ins, gt[np.newaxis]])
        #         img = cv2.fillPoly(img, [box], 255)
        #         img = cv2.drawContours(img, [box], 0, 0, 2)

        #     # minimum area of stick
        #     if np.sum(np.sum(ins, axis=(1, 2)) < 400) == 0:
        #         break

        # if self.train:
        #     sem = np.zeros_like(img, dtype=bool)
        #     sem[np.sum(ins, axis=0) != 0] = True
        #     sem = np.stack([~sem, sem]).astype(np.uint8)

        #     print(img[np.newaxis].shape)
        #     print(sem.shape)
        #     print(ins.shape)

        #     # 1 * height * width
        #     img = torch.Tensor(img[np.newaxis])
        #     # 2 * height * width
        #     sem = torch.Tensor(sem)
        #     # n_sticks * height * width
        #     ins = torch.Tensor(ins)
        #     return img, sem, ins
        # else:
        #     # 1 * height * width
        #     img = torch.Tensor(img[np.newaxis])
        #     return img


if __name__=='__main__':
    dataset = SSSDataset(train=True, n_sticks=8)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=False, num_workers=0, pin_memory=True)

    img, sem, ins = dataloader

    # for epoch in range(10):
    #     for batched in dataloader:
    #         img, sem, ins = batched


