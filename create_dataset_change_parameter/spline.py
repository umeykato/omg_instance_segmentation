#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import sys

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import interp2d

def CatmullRom(p0, p1, p2, p3, t):
    v0 = (p2 - p0) * 0.5
    v1 = (p3 - p1) * 0.5
    t2 = t * t
    t3 = t2 * t
    return ((p1 - p2)*2.0 + v0 + v1) * t3 + ((p2 - p1)*3.0 - 2.0 * v0 - v1) * t2 + v0 * t + p1

def CatmullRomSpline(points, interpolate_num):
    dst = []
    for i in range(1, len(points) - 2):
        div_kernel = 1.0 / interpolate_num
        for k in range(interpolate_num):
            t = k * div_kernel
            xcr = CatmullRom(points[i-1][0],points[i][0],points[i+1][0],points[i+2][0],t)
            ycr = CatmullRom(points[i-1][1],points[i][1],points[i+1][1],points[i+2][1],t)
            zcr = CatmullRom(points[i-1][2],points[i][2],points[i+1][2],points[i+2][2],t)
            
            dst.append([xcr, ycr, zcr])

    return dst

if __name__=='__main__':
    pass
