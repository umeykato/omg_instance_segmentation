#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def triangle_area_multi(v1,v2,v3):
    '''

    :param v1:
    :param v2:
    :param v3:
    :return:
    '''
    return 0.5*np.linalg.norm(np.cross(v2-v1,v3-v1),axis=1)


"""
process: verticesとfacesから点群を生成
input:   vertices, faces
output:  pointcloud
"""

    
def mesh2pointcloud_dataframe(vartices_df, faces_df):
    points_xyz = vartices_df[['x','y','z']].values

    # print(type(points_xyz))
    # print(points_xyz)

    # print(faces_df)

    # print(faces_df['v1'])
    # print(faces_df['v2'])
    # print(faces_df['v3'])

    v1_xyz = points_xyz[faces_df['v1']-1]
    v2_xyz = points_xyz[faces_df['v2']-1]
    v3_xyz = points_xyz[faces_df['v3']-1]

    # print(type(v1_xyz))
    # print(type(v2_xyz))
    # print(type(v3_xyz))
    # print(v1_xyz)
    # print(v2_xyz)
    # print(v3_xyz)

    n=5000
    naive_random_indices=np.random.randint(low=0,high=v1_xyz.shape[0],size=n)
    # print(naive_random_indices)

    areas=triangle_area_multi(v1_xyz,v2_xyz,v3_xyz)
    probabilities=areas/areas.sum()

    weighted_random_indices=np.random.choice(range(len(areas)),size=n,p=probabilities)
    # print(weighted_random_indices)

    v1_xyz=v1_xyz[weighted_random_indices]
    v2_xyz=v2_xyz[weighted_random_indices]
    v3_xyz=v3_xyz[weighted_random_indices]

    u=np.random.rand(n,1)
    v=np.random.rand(n,1)
    is_a_problem=u+v>1

    u[is_a_problem]=1-u[is_a_problem]
    v[is_a_problem]=1-v[is_a_problem]

    w=1-(u+v)

    result=pd.DataFrame()

    result_xyz=(v1_xyz*u)+(v2_xyz*v)+(w*v3_xyz)
    result_xyz=result_xyz.astype((np.float32))

    result["x"]=result_xyz[:,0]
    result["y"]=result_xyz[:,1]
    result["z"]=result_xyz[:,2]

    # print(result)

    # fig = plt.figure()
    # ax3d = Axes3D(fig)
    # ax3d.plot(result["x"],result["y"],result["z"], 'o', ms=2, mew=0.1, color='blue')
    # plt.show()

    return result, result_xyz
    # print("length:",len(result))
    # print(result.head())

    # write_ply("./result.ply",points=result,as_text=True)


if __name__=='__main__':
    pass
