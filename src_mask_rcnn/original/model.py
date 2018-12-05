#!/usr/bin/env python

import os
import sys

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable

import numpy as np
import cupy as cp


class BackBone(Chainer.Chain):
    """


    """

    def __init__():
        pass

    def __call__():
        pass

class RegionProporsalNetwork(Chainer.Chain):
    """
    

    """

    def __init__():
        pass


    """
    Region Proposal Networkのフォワード処理
    N: バッチサイズ
    C: チャンネルサイズ
    H, W: 入力特徴マップのheightとwidth 
    A: anchorの数

    args
    x: chainer.Variable (N, C, H, W)
    img_size: tuple of ints
    scale: float

    returns
    rpn_locs: anchorのためのウンディングボックスのオフセットとスケール
              (N, H W A, 4)
    rpn_scores: anchorのための前景のスコア
              (N, H W A, 2)
    rois: プロポーサルボックスの座標情報を持つバウンディングボックス
          バッチサイズ分のバウンディングボックスが合わさっている
            (R', 4) R:
    roi_indeces: 
    anchor: 
    

    """

    def __call__():
        pass

class Head(Chainer.Chain):
    """
    

    """

    def __init__():
        pass

    def __call__():
        pass

if __name__=='__main__':
    pass