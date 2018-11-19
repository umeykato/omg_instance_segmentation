#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import sys

import numpy as np
import pandas as pd
import cv2

# import adelWheat
import mesh2pointcloud
import isomap
import spline

def makeDirectory(path):
    try:
        os.mkdir(path)
    except:
        pass

def calcPosition(image_path):
    print(image_path)
    img = cv2.imread(image_path)
    temp = np.empty((img.shape))
    # print(img.shape)
    index_map = np.where(img[:,:,0] == 0, True, False)
    index_map *= np.where(img[:,:,1] == 0, True, False)
    index_map *= np.where(img[:,:,2] == 0, True, False)

    index = np.where(index_map)

    # print(index)
    # print(np.average(index[0]).astype(np.int16), np.average(index[1]).astype(np.uint16))
    # print(np.round(np.average(index[0])).astype(np.int16), np.round(np.average(index[1])).astype(np.int16))

    index_x = np.round(np.average(index[0])).astype(np.int16)
    index_y = np.round(np.average(index[1])).astype(np.int16)

    return index_x, index_y
                

def main():
    root_path = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver3/img'
    save_path = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver3/ply_render2d'

    for age in range(100, 1100, 100):
        root_dir = root_path + '/leaf_age{}'.format(age)
        save_dir = save_path + '/leaf_age{}'.format(age)
        makeDirectory(save_dir)
        for i in range(100):
            for location in range(5):
                f = open(save_dir + '/location{}_{:04}.txt'.format(location, i), 'w')
                for object_num in range(60):
                    exist_path = root_dir + '/spline_location{}object{}point0'.format(location, object_num)
                    print('exist_path : ', exist_path)
                    if not os.path.exists(exist_path):
                        continue
                    for point_num in range(8):
                        image_path = root_dir + '/spline_location{}object{}point{}/{:04}.png'.format(location, object_num, point_num, i)
                        print('image_path : ', image_path)
                        x, y = calcPosition(image_path)
                        f.write(str(x)+'\n')
                        f.write(str(y)+'\n')
                        print('x:', x, ' y: ', y)

                f.close()
                        
                
                


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
