#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import shutil
import sys
import argparse

import numpy as np
import pandas as pd
import cv2

# import adelWheat
import mesh2pointcloud
import isomap
import spline

def main():
    parser = argparse.ArgumentParser(
                prog='segment_instance5_from_dataset_ver2',
                usage='create instance image',
                description='description',
                epilog='end',
                add_help=True,
                )

    parser.add_argument('--start', '-S', type=int, default=100,
                        help='select start age')

    args = parser.parse_args()

    # root = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver3'
    # root = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver3'
    root = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_zoom'
    img_root = root + '/img'
    txt_root = root + '/ply_render2d'

    save_root = root + '/dataset_arrange'
    
    # imageを移す
    start = args.start
    end = 100
    for age in range(start, start+end, 100):
        for location in range(5):
            for img_num in range(100):
                src = img_root + '/leaf_age{}/image_location{}/{:04}.png'.format(age, location, img_num)
                dst = save_root + '/image/age{}location{}_{:04}.png'.format(age, location, img_num)

                shutil.copyfile(src, dst)

    # semanticを移す
    for age in range(start, start+end, 100):
        for location in range(5):
            for img_num in range(100):
                src = img_root + '/leaf_age{}/semantic_location{}/{:04}.png'.format(age, location, img_num)
                dst = save_root + '/semantic/age{}location{}_{:04}.png'.format(age, location, img_num)

                shutil.copyfile(src, dst)

    # instanceを移す
    for age in range(start, start+end, 100):
        for location in range(5):
            for img_num in range(100):
                src = img_root + '/leaf_age{}/instance_location{}/{:04}.png'.format(age, location, img_num)
                dst = save_root + '/instance/age{}location{}_{:04}.png'.format(age, location, img_num)

                shutil.copyfile(src, dst)

    # splineを移す
    for age in range(start, start+end, 100):
        for location in range(5):
            for img_num in range(100):
                src = txt_root + '/leaf_age{}/location{}_{:04}.csv'.format(age, location, img_num)
                dst = save_root + '/spline/age{}location{}_{:04}.csv'.format(age, location, img_num)

                shutil.copyfile(src, dst)


                


if __name__=='__main__':
    """
    def processing
    for plant_num
        for object_num:
            for point_num:
                for position:
                    read image
                    画像上の座標算出
                    座標保存

    保存ファイル名
    age(plant_num)
    nsect
    obj_num

    """
    main()
