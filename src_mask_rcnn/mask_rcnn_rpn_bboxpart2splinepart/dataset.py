#!/usr/bin/env python

import os
import os.path as osp
import sys

import chainer

import numpy as np

# sys.path.append(osp.join(osp.dirname(__file__), '../..'))
# import chainer_mask_rcnn as cmr

here = osp.dirname(osp.abspath(__file__))  # NOQA
sys.path.insert(0, osp.join(here, '..'))  # NOQA

import train_common

import cv2


class OomugiDataset(chainer.dataset.DatasetMixin):

    

    def __init__(self, test=False):
        # root = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_ver3/dataset_SemInsSpline'
        root = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver3/dataset_SemInsSpline'
        self.img_path = root + '/image/'
        self.sem_path = root + '/semantic/'
        self.ins_path = root + '/instance_segment/'
        self.spline_path = root + '/spline/'

        self.img_names = os.listdir(self.img_path)


    def __len__(self):
        # return len(self.img_names)
        return 10

    def get_example(self, i):
        fname = self.img_names[i]

        # print('fname ', fname)

        img = cv2.imread(self.img_path + fname)

        # print('type img ', type(img))
        # print(img.dtype)
        # print(img.shape)

        # instance画像のパス生成
        ins_dir = self.ins_path + self.img_names[i].rstrip('.png') + '/'
        # オブジェクト数を格納
        ins_num = len(os.listdir(ins_dir)) - 1
        # print(ins_num)
        # instance画像と同サイズのarray生成（ｃｈ数＝最大オブジェクト数）
        ins = np.zeros((ins_num, img.shape[0], img.shape[1]), dtype=np.int32)

        # instance画像をnumpyに格納
        for num in range(ins_num):
            # instance画像生成
            ins_temp = cv2.imread(ins_dir + '{}.png'.format(num+1), 0)
            # 255で割って正規化したやつを（現在のオブジェクト数）chとして代入
            ins[num] = ins_temp / 255
        masks = np.array(ins, dtype=np.uint8)

        # print('type masks ', type(masks))
        # print(masks.dtype)
        # print(masks.shape)
        # print(np.unique(masks))


        # 各instance画像のbboxを求める
        # bboxをsplineの制御点に変える
        bboxes = []
        for num in range(ins_num):
            bbox = self._mask_to_bbox(ins[num])
            bboxes.append(bbox)
        bboxes = np.array(bboxes, dtype=np.float32)
        # print(bboxes.shape)

        points = []
        points_x = []
        points_y = []
        for num in range(ins_num):
            pass


        labels = np.ones((ins_num), dtype=np.int32)

        # print('type labels ', type(labels))
        # print(labels.dtype)
        # print(labels.shape)

        example = [bboxes, labels, masks]

        
        return tuple([img] + example)

    """
    floatで返す
    """
    def _mask_to_bbox(self, mask):
        index = np.where(mask == 1)
        return [index[0].min(), index[1].min(), index[0].max(), index[1].max()]

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