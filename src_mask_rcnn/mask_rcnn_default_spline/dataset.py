#!/usr/bin/env python

import os
import os.path as osp
import sys
import csv

import chainer

import numpy as np

sys.path.append(osp.join(osp.dirname(__file__), '../..'))
# import chainer_mask_rcnn as cmr
from chainer_mask_rcnn_spline import utils

here = osp.dirname(osp.abspath(__file__))  # NOQA
sys.path.insert(0, osp.join(here, '..'))  # NOQA

import cv2


class OomugiDataset(chainer.dataset.DatasetMixin):

    def __init__(self, test=False):

        if os.name == 'nt':
            root = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_ver4/train'
        elif os.name == 'posix':
            root = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/mask_rcnn_dataset/train'


        if os.name == 'nt' and test:
            root = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_ver4/test'
        elif os.name == 'posix' and test:
            root = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/mask_rcnn_dataset/test'


        self.img_path = root + '/image/'
        self.sem_path = root + '/semantic/'
        self.ins_path = root + '/instance_segment/'
        self.spline_path = root + '/spline/'

        self.img_names = os.listdir(self.img_path)
        self.test = test


    def __len__(self):
        # print(len(self.img_names))
        return len(self.img_names)
        # return 100

    def get_example(self, i):
        fname = self.img_names[i]

        # print('fname ', fname)

        resize_size = 500

        img = cv2.imread(self.img_path + fname)
        img = cv2.resize(img, (resize_size, resize_size))

        # print('type img ', type(img))
        # print(img.dtype)
        # print(img.shape)

        # instance画像のパス生成
        ins_dir = self.ins_path + self.img_names[i].rstrip('.png') + '/'
        # オブジェクト数を格納
        # ins_num = len(os.listdir(ins_dir)) - 1
        ins_num = len(os.listdir(ins_dir))
        # print(ins_num)
        # instance画像と同サイズのarray生成（ｃｈ数＝最大オブジェクト数）
        ins = np.zeros((ins_num, img.shape[0], img.shape[1]), dtype=np.int32)
        ins_one = np.ones((resize_size, resize_size), dtype=np.uint8) * 255

        # instance画像をnumpyに格納
        offset = 0
        ins_fnames = os.listdir(ins_dir)
        num_list = []
        # for num in range(ins_num):
        for num, fname in enumerate(ins_fnames):
            # instance画像生成
            # print(ins_dir + fname)
            ins_temp = cv2.imread(ins_dir + fname, 0)
            ins_temp = cv2.resize(ins_temp, (resize_size, resize_size))

            # リサイズでラベル領域がつぶれたらパスする
            if (np.sum(ins_temp == ins_one) == 0):
                ins = np.delete(ins, num-offset, 0)
                offset += 1
                continue

            # バウンディングボックスがつぶれたらパスする
            index_temp = np.where(ins_temp == 255)
            # print(index_temp)
            index_temp = np.array([index_temp[0].min(), index_temp[1].min(), index_temp[0].max(), index_temp[1].max()])
            if (index_temp[2] - index_temp[0]) < 2 or (index_temp[3] - index_temp[1]) < 2:
                ins = np.delete(ins, num-offset, 0)
                offset += 1
                continue

            # 255で割って正規化したやつを（現在のオブジェクト数）chとして代入
            ins[num-offset] = ins_temp / 255

            root, ext = os.path.splitext(os.path.basename(fname))
            num_list.append(int(root))

        num_list.sort()

        masks = np.array(ins, dtype=np.uint8)

        ins_num = ins_num - offset
        # print(ins_num)

        # 各instance画像のbboxを求める
        bboxes = []
        for num in range(ins_num):
            # bbox = self._mask_to_bbox(ins[num])
            bbox = utils.mask_to_bbox(ins[num])
            bboxes.append(bbox)
            # print((bbox[2]-bbox[0])*(bbox[3]-bbox[1]))
        bboxes = np.array(bboxes, dtype=np.float32)

        # print(bboxes.shape)


        # クラスラベル　全部１
        labels = np.zeros((ins_num), dtype=np.int32)

        # splineを作成
        spline_list_src = []
        fname = self.spline_path + self.img_names[i].rstrip('.png') + '.csv'
        with open(fname, 'r') as f:
            reader = csv.reader(f)
            
            for row in reader:
                spline_list_src.append(list(map(int,row)))

        splines = [] # (葉の枚数, 8, 2)
        for i in range(len(spline_list_src)//8):
            if i in num_list:
                splines_temp = [] # (8, 2)
                for j in range(8):
                    splines_temp.append(spline_list_src[i*8+j][2:4])
                    # print(i, j, spline_list_src[i*8+j][2:4])

                splines.append(splines_temp)

        splines = np.array(splines, dtype=np.int32)

        # img       (3, h, w)
        # bboxes    (n, h, w)
        # labels    (n)
        # masks     (n, 4)
        # splines   (n, 8, 2)

        if ins_num == 0:
            return self.get_example(i+1)
        else:
            return tuple([img] + [bboxes, labels, masks, splines])

    """
    floatで返す
    """
    def _mask_to_bbox(self, mask):
        index = np.where(mask == 1)
        # return [index[0].min(), index[1].min(), index[0].max(), index[1].max()]
        return [index[1].min(), index[0].min(), index[1].max(), index[0].max()]

    """
    anns(annotations)からbbox, label, maskを作ってる

    annsの中身は
    segmentation:マスク領域をかたどる座標群（cityscapesと同じ感じ）
    is_crowd:わかんない
    image_id:わかんない
    bbox:バウンディングボックスの左上と右下？左下と右上？の座標がある
    category_id:ラベルのカテゴリー番号
    id:わかんない
    これがラベル数分ある

    """
    def _annotations_to_example(self, anns, height, width):
        bboxes = []
        labels = []
        masks = []
        if self._return_crowd:
            crowds = []
        if self._return_area:
            areas = []
        for ins_id, ann in enumerate(anns):
            if 'segmentation' not in ann:
                continue
            if not self._use_crowd and ann['iscrowd'] == 1:
                continue
            class_id = self.cat_id_to_class_id[ann['category_id']]
            if isinstance(ann['segmentation'], list):
                # polygon
                mask = np.zeros((height, width), dtype=np.uint8)
                mask = PIL.Image.fromarray(mask)
                for seg in ann['segmentation']:
                    xy = np.array(seg).reshape((-1, 2))
                    xy = [tuple(xy_i) for xy_i in xy]
                    PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
                mask = np.asarray(mask)
            else:
                # mask
                if isinstance(ann['segmentation']['counts'], list):
                    rle = pycocotools.mask.frPyObjects(
                        [ann['segmentation']], height, width)
                else:
                    rle = [ann['segmentation']]
                mask = pycocotools.mask.decode(rle)[:, :, 0]
                # FIXME: some of minival annotations are malformed.
                if mask.shape != (height, width):
                    continue
            mask = mask == 1  # int32 -> bool
            bbox = utils.mask_to_bbox(mask)  # y1, x1, y2, x2
            bboxes.append(bbox)
            masks.append(mask)
            labels.append(class_id)
            if self._return_crowd:
                crowds.append(ann['iscrowd'])
            if self._return_area:
                areas.append(ann['area'])
        bboxes = np.asarray(bboxes, dtype=np.float32)
        bboxes = bboxes.reshape((-1, 4))
        labels = np.asarray(labels, dtype=np.int32)
        masks = np.asarray(masks, dtype=np.int32)
        masks = masks.reshape((-1, height, width))
        example = [bboxes, labels, masks]
        if self._return_crowd:
            crowds = np.asarray(crowds, dtype=np.int32)
            example.append(crowds)
        if self._return_area:
            areas = np.asarray(areas, dtype=np.float32)
            example.append(areas)
        return example

if __name__=='__main__':
    dataset = OomugiDataset()
    tmp = dataset.get_example(400)