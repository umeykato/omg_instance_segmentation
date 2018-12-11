#!/usr/bin/env python

import os
import sys

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Variable


# Region Proposal Network
from chainercv.links.model.faster_rcnn.utils.generate_anchor_base import \
    generate_anchor_base
from chainercv.links.model.faster_rcnn.utils.proposal_creator import \
    ProposalCreator

import numpy as np
import cupy as cp


class MaskRCNN(chainer.Chain):
    def __init__():
        extractor = VGG16(initialW=vgg.initialW)
        extractor.pick = 'conv5_3'
        extractor.remove_unused()

        rpn = RegionProporsalNetwork()
        
        head = Head()

    def __call__():
        pass

class RegionProposalNetwork(Chainer.Chain):
    """
    
    args: (int)
    in_channels: (int)
    mid_channels: (list of floats)
    anchor_scales: (list of numbers)
    feat_stride: (int)
    initialW: (callable)
    proposal_creator_params: (dict)

    """

    def __init__(
            self,
            in_channels=512,
            mid_channels=512
            rations=[0.5, 1, 2],
            anchor_scales=[8, 16, 32],
            feat_stride=16,
            initialW=None,
            proposal_creator_params=dict()
    ):
        pass


    """
    Region Proposal Networkのフォワード処理
    N: バッチサイズ
    C: チャンネルサイズ
    H, W: 入力特徴マップのheightとwidth 
    A: anchorの数　len(ratios) * len(anchor_scales)

    args
    x: chainer.Variable (N, C, H, W)
    img_size: tuple of ints
    scale: float

    returns
    rpn_locs: anchorのためのバウンディングボックスのオフセットとスケール
              (N, H W A, 4)
    rpn_scores: anchorのための前景のスコア
              (N, H W A, 2)
    rois: アンカーボックスの座標情報を持つバウンディングボックス
          バッチサイズ分のバウンディングボックスが合わさっている
          R_i: バッチサイズi番目の画像からR個のバウンディングボックスが予測される
          R' = sum(R_i)
            (R', 4) 
    roi_indices: RoIが対応する画像のインデックスを含む配列
            (R',)
    anchor: シフトしたアンカーの座標を列挙したもの
            (H W A, 4)
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