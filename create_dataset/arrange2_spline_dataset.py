#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import shutil
import sys

import numpy as np
import pandas as pd
import cv2

# import adelWheat
import mesh2pointcloud
import isomap
import spline

def main():
    # root = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver3'
    root = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver3'
    img_root = root + '/img'
    txt_root = root + '/ply_render2d'

    save_root = root + '/dataset_SemInsSpline'
    
    # imageを移す
    for age in range(100, 1100, 100):
        for location in range(5):
            for img_num in range(100):
                src = img_root + '/leaf_age{}/image_location{}/{:04}.png'.format(age, location, img_num)
                dst = save_root + '/image/age{}location{}_{:04}.png'.format(age, location, img_num)

                shutil.copyfile(src, dst)

    # semanticを移す
    for age in range(100, 1100, 100):
        for location in range(5):
            for img_num in range(100):
                src = img_root + '/leaf_age{}/semantic_location{}/{:04}.png'.format(age, location, img_num)
                dst = save_root + '/semantic/age{}location{}_{:04}.png'.format(age, location, img_num)

                shutil.copyfile(src, dst)

    # instanceを移す
    for age in range(100, 1100, 100):
        for location in range(5):
            for img_num in range(100):
                src = img_root + '/leaf_age{}/instance_location{}/{:04}.png'.format(age, location, img_num)
                dst = save_root + '/instance/age{}location{}_{:04}.png'.format(age, location, img_num)

                shutil.copyfile(src, dst)

    # splineを移す
    for age in range(100, 1100, 100):
        for location in range(5):
            for img_num in range(100):
                src = txt_root + '/leaf_age{}/location{}_{:04}.txt'.format(age, location, img_num)
                dst = save_root + '/spline/age{}location{}_{:04}.txt'.format(age, location, img_num)

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
