#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import sys

import numpy as np
import pandas as pd

# from pyntcloud.io import read_ply
# from pyntcloud.io import write_ply
# from pyntcloud import PyntCloud
from sklearn.datasets import load_digits
from sklearn.manifold import Isomap
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from scipy.interpolate import interp2d

def isomap_centerline(pointcloud):
    # 点群を取得
    points_xyz = pointcloud[['x','y','z']].values
    x = points_xyz[:,0]
    y = points_xyz[:,1]
    z = points_xyz[:,2]

    # isomapに展開
    n_neighbor = 30
    n_components = 2
    isomap = Isomap(n_neighbors=n_neighbor, n_components=n_components)

    points_xyz_iso = isomap.fit(points_xyz).transform(points_xyz)
    x_iso = points_xyz_iso[:,0]
    y_iso = points_xyz_iso[:,1]

    # print(points_xyz.shape)
    # print(points_xyz_iso.shape)

    # plt.scatter(x_iso, y_iso)
    # plt.show()

    # isomapでy軸-0.01~0.01（センターライン）のインデックスを取得
    area = 0.01
    index = np.where(np.logical_and(y_iso < area, y_iso > -area))

    # 取得したインデックスをisomapのx軸に関して昇順にソート
    points_xyz_iso_index = points_xyz_iso[index, :]

    temp = np.argsort(points_xyz_iso_index, axis=1)

    # print("ソート前")
    # print(index[0])
    # print("ソート順")
    # print(temp[:,:,0][0])
    # print("ソート後")
    # print(index[0][temp[:,:,0][0]])

    index_sorted = index[0][temp[:,:,0][0]]

    # anky_points_xyz_iso_index = anky_points_xyz_iso[index, :]
    points_xyz_iso_index = points_xyz_iso[index_sorted]
    x_iso_index = points_xyz_iso_index[:,0]
    y_iso_index = points_xyz_iso_index[:,1]

    # plt.scatter(x_iso, y_iso)
    # plt.scatter(x_iso_index, y_iso_index, color='red')
    # plt.show()

    points_xyz_index = points_xyz[index_sorted]
    x_index = points_xyz_index[:,0]
    y_index = points_xyz_index[:,1]
    z_index = points_xyz_index[:,2]

    # センターラインの両端の距離とその間の点の累積距離リストを作成
    distance = 0
    distance_list = []
    for i in range(1, len(index[0])):
        dx = x_index[i] - x_index[i-1]
        dy = y_index[i] - y_index[i-1]
        dz = z_index[i] - z_index[i-1]
        d = math.sqrt(dx**2 + dy**2 + dz**2)
        distance += d
        distance_list.append(distance)
    # print(distance_list)
    # print(distance)

    # point_num点で等間隔の距離リストを出す
    point_num = 8
    distance_interval = distance / float(point_num - 1)
    distance_midPoints_neighborhood = []
    for i in range(point_num):
        distance_midPoints_neighborhood.append(distance_interval * float(i))
    # print(distance_midPoints_neighborhood)

    def getNearestValue(list, num):
        """
        概要: リストからある値に最も近い値を返却する関数
        @param list: データ配列
        @param num: 対象値
        @return 対象値に最も近い値
        """

        # リスト要素と対象値の差分を計算し最小値のインデックスを取得
        idx = np.abs(np.asarray(list) - num).argmin()
        # return list[idx]
        return idx

    # 等間隔の距離リストをもとに，最も近い点を出す
    spline_index = []
    for i in range(point_num):
        spline_index.append(getNearestValue(distance_list, distance_midPoints_neighborhood[i]))
    
    spline_xyz = points_xyz[np.array(index[0][temp[:,:,0][0]])[spline_index]]
    x_spline = spline_xyz[:,0]
    y_spline = spline_xyz[:,1]
    z_spline = spline_xyz[:,2]
    # print(spline_xyz)

    # plt.scatter(x_iso, y_iso)
    # plt.scatter(x_iso_index, y_iso_index, color='red')
    # plt.show()

    # fig = plt.figure()
    # ax = Axes3D(fig)
    # ax.plot(x,y,z,'o',ms=1, mew=0.1, color='black')
    # ax.plot(x_index,y_index,z_index,'o',ms=3, mew=0.1, color='red')
    # ax.plot(x_spline,y_spline,z_spline,'o',ms=5, mew=0.1, color='green')
    # plt.show()

    return points_xyz_iso, points_xyz_iso_index, points_xyz_index, spline_xyz


if __name__=='__main__':
    pass
