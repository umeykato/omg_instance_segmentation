#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import math
import os
import sys


import numpy as np
import pandas as pd

from alinea.adel.astk_interface import AdelWheat
from alinea.astk.Weather import sample_weather
import openalea.plantgl.all as pgl

import obj

def makeDirectory(dir_name):
    try:
        os.mkdir(dir_name)
    except:
        pass


def plot3d1(g,i, 
               leaf_material = None,
               stem_material = None,
               soil_material = None,
               colors = None):
    """
    Returns a plantgl scene from an mtg.
    """
    
    Material = pgl.Material
    Color3 = pgl.Color3
    Shape = pgl.Shape
    Scene = pgl.Scene

    if colors is None:
        if leaf_material is None:
            leaf_material = Material(Color3(0,180,0))
        if stem_material is None:
            stem_material = Material(Color3(0,130,0))
        if soil_material is None:
            soil_material = Material(Color3(170, 85,0))
        colors = g.property('color')

    geometries = g.property('geometry')
    greeness = g.property('is_green')
    labels = g.property('label')
    scene = Scene()

    output_map = [[True, True, True, True],
                    [True, False, True, False],
                    [False, True, False, True],
                    [True, False, False, False],
                    [False, True, False, False],
                    [False, False, True, False],
                    [False, False, False, True]]
    
    def geom2shape(vid, mesh, scene):
        shape = None
        if isinstance(mesh, list):
            for m in mesh:
                geom2shape(vid, m, scene)
            return
        if mesh is None:
            return
        if isinstance(mesh, Shape):
            shape = mesh
            mesh = mesh.geometry
        label = labels.get(vid)
        is_green = greeness.get(vid)
        if colors:
            shape = Shape(mesh, Material(Color3(* colors.get(vid, [0,0,0]) )))
        elif not greeness:
            if not shape:
                shape = Shape(mesh)
                shape.id=vid
            scene.add(shape)

        # 緑の茎を出す
        elif label.startswith('Stem') and is_green and (output_map[i][0]):
            shape = Shape(mesh, stem_material)
            shape.id=vid
            scene.add(shape)
            s=property(scene.add(shape))

        # 緑の葉を出す
        elif label.startswith('Leaf') and is_green and (output_map[i][1]):
            shape = Shape(mesh, leaf_material)
            shape.id=vid
            scene.add(shape)

        # 茶色の茎を出す
        elif label.startswith('Stem') and not is_green and (output_map[i][2]):
            shape = Shape(mesh, soil_material)
            shape.id=vid
            scene.add(shape)

        # 茶色の葉を出す
        elif label.startswith('Leaf') and not is_green and (output_map[i][3]):
            shape = Shape(mesh, soil_material)
            shape.id=vid
            scene.add(shape)


    for vid, mesh in geometries.iteritems():
        geom2shape(vid, mesh, scene)

    # sceneはオブジェクトファイルとして保存される
    return scene

def growth_wheat():
    seq, weather = sample_weather()
    wdata = weather.get_weather(seq)

    nsect = 1 #the number of element per leaf

    adel = AdelWheat(nsect=nsect, nplants=1, seed=2)

    # age=900に固定
    g = adel.setup_canopy(900)
    adel.grow(g, wdata)

    # csv保存
    with open('label.csv','w') as f:
        writer=csv.writer(f)
        label=g.property('label')
        geometry=g.property('geometry')
        is_green=g.property('is_green')
        writer.writerow([label])
        writer.writerow([geometry])
        writer.writerow([is_green])
    f.close()

    # 茎，緑葉，茶葉，全体を生成して保存
    for i in range(0,4,1):
        st = plot3d1(g,i)
        for t in range(len(st)):
            st[t].name = str(t)
        # 自動的に.mtlも保存してくれるっぽい
        st.save("./"+"compare/"+str(i)+"/nsect"+str(nsect)+".obj")

    st = plot3d1(g,4)
    w=obj.ObjCodec()
    w.write2("./compare/1/aa.obj",st)

def growth_wheat_someage():
    seq, weather = sample_weather()
    wdata = weather.get_weather(seq)
    nsect = 1 #the number of element per leaf
    adel = AdelWheat(nsect=nsect, nplants=1, seed=2)

    # save_dir = './obj'
    # save_dir = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver4/obj'
    if os.name == 'nt':
        save_dir = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_ver4/obj'
    else:
        save_dir = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver4/obj'

    makeDirectory(save_dir)

    for age in range(100, 1100, 100):

        g = adel.setup_canopy(age)
        adel.grow(g, wdata)

        # パラメータcsv保存
        with open(save_dir+'/param_age{}.csv'.format(age),'w') as f:
            writer=csv.writer(f)
            label=g.property('label')
            geometry=g.property('geometry')
            is_green=g.property('is_green')
            writer.writerow([label])
            writer.writerow([geometry])
            writer.writerow([is_green])
        f.close()

        # 茎，緑葉，茶葉，全体, 葉を生成して保存

        folder_name = ['all','stem', 'leaf', 'green_stem', 'green_leaf', 'brown_stem', 'brown_leaf']
        for i in range(len(folder_name)):
            makeDirectory(save_dir+'/'+folder_name[i]+'_age'+str(age))
            st = plot3d1(g,i)
            for t in range(len(st)):
                st[t].name = str(t)
            # 自動的に.mtlも保存してくれるっぽい
            st.save(save_dir+'/'+folder_name[i]+'_age'+str(age)+'.obj')

            # if i != 3:
            w=obj.ObjCodec()
            w.write2(save_dir+'/'+folder_name[i]+'_age'+str(age),st)


if __name__=='__main__':
    growth_wheat_someage()
