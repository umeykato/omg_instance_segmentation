# Modified works:
# --------------------------------------------------------
# Copyright (c) 2017 - 2018 Kentaro Wada.
# Licensed under The MIT License [see LICENSE for details]
# --------------------------------------------------------

# This is modified work of FasterRCNNTrainChain:
# --------------------------------------------------------
# Copyright (c) 2017 Preferred Networks, Inc.
# Licensed under The MIT License [see LICENSE for details]
# https://github.com/chainer/chainercv
# --------------------------------------------------------

import numpy as np
import cupy as xp

import chainer
from chainer import cuda
import chainer.functions as F

from .utils import ProposalTargetCreator
from chainercv.links.model.faster_rcnn.utils.anchor_target_creator import\
    AnchorTargetCreator

from inspect import currentframe


# ロス計算及びログのレポート
class MaskRCNNTrainChain(chainer.Chain):

    """Calculate losses for Faster R-CNN and report them.

    This is used to train Faster R-CNN in the joint training scheme
    [#FRCNN]_.

    The losses include:

    * :obj:`rpn_loc_loss`: The localization loss for \
        Region Proposal Network (RPN).
    * :obj:`rpn_cls_loss`: The classification loss for RPN.
    * :obj:`roi_loc_loss`: The localization loss for the head module.
    * :obj:`roi_cls_loss`: The classification loss for the head module.

    .. [#FRCNN] Shaoqing Ren, Kaiming He, Ross Girshick, Jian Sun. \
    Faster R-CNN: Towards Real-Time Object Detection with \
    Region Proposal Networks. NIPS 2015.

    Args:
        faster_rcnn (~chainercv.links.model.faster_rcnn.FasterRCNN):
            A Faster R-CNN model that is going to be trained.
        rpn_sigma (float): Sigma parameter for the localization loss
            of Region Proposal Network (RPN). The default value is 3,
            which is the value used in [#FRCNN]_.
        roi_sigma (float): Sigma paramter for the localization loss of
            the head. The default value is 1, which is the value used
            in [#FRCNN]_.
        anchor_target_creator: An instantiation of
            :obj:`chainercv.links.model.faster_rcnn.AnchorTargetCreator`.
        proposal_target_creator_params: An instantiation of
            :obj:`chainercv.links.model.faster_rcnn.ProposalTargetCreator`.

    """

    def __init__(self, mask_rcnn, rpn_sigma=3., roi_sigma=1.,
                 anchor_target_creator=AnchorTargetCreator(),
                 proposal_target_creator=ProposalTargetCreator(),
                 ):
        super(MaskRCNNTrainChain, self).__init__()
        with self.init_scope():
            self.mask_rcnn = mask_rcnn
        self.rpn_sigma = rpn_sigma
        self.roi_sigma = roi_sigma

        self.anchor_target_creator = anchor_target_creator
        self.proposal_target_creator = proposal_target_creator

        self.loc_normalize_mean = mask_rcnn.loc_normalize_mean
        self.loc_normalize_std = mask_rcnn.loc_normalize_std

    def __call__(self, imgs, bboxes, labels, masks, spline, scales, sizes):
        """Forward Faster R-CNN and calculate losses.
        mask rcnn のフォワード及びロス計算．faster rcnn をラップ
        Here are notations used.

        * :math:`N` is the batch size.
        * :math:`R` is the number of bounding boxes per image.

        Currently, only :math:`N=1` is supported.

        Args:
            imgs (~chainer.Variable): A variable with a batch of images.
            bboxes (~chainer.Variable): A batch of bounding boxes.
                Its shape is :math:`(N, R, 4)`.
            labels (~chainer.Variable): A batch of labels.
                Its shape is :math:`(N, R)`. The background is excluded from
                the definition, which means that the range of the value
                is :math:`[0, L - 1]`. :math:`L` is the number of foreground
                classes.
            scale (float or ~chainer.Variable): Amount of scaling applied to
                the raw image during preprocessing.

        Returns:
            chainer.Variable:
            Scalar loss variable.
            This is the sum of losses for Region Proposal Network and
            the head module.

        """
        if isinstance(bboxes, chainer.Variable):
            bboxes = bboxes.data
        if isinstance(labels, chainer.Variable):
            labels = labels.data
        if isinstance(scales, chainer.Variable):
            scales = scales.data

        scales = cuda.to_cpu(np.array(scales))

        batch_size, _, H, W = imgs.shape
        img_size = (H, W)

        # backborn forward
        features = self.mask_rcnn.extractor(imgs)   # (2, 512, 14, 14)

        # Region Proporsal Network forward
        # (2, R, 4)
        # 
        # 
        # 
        # 
        rpn_locs, rpn_scores, rois, roi_indices, anchor = self.mask_rcnn.rpn(
            features, img_size, scales)

        batch_indices = range(batch_size)
        sample_rois = []
        sample_roi_indices = []
        gt_roi_locs = []
        gt_roi_labels = []
        gt_roi_masks = []

        # batch size times
        for batch_index, bbox, label, mask in \
                zip(batch_indices, bboxes, labels, masks):
            roi = rois[roi_indices == batch_index]
            # rpnの教師データ作成
            sample_roi, gt_roi_loc, gt_roi_label, gt_roi_mask = \
                self.proposal_target_creator(roi, bbox, label, mask)
            del roi
            sample_roi_index = self.xp.full(
                (len(sample_roi),), batch_index, dtype=np.int32)
            sample_rois.append(sample_roi)
            sample_roi_indices.append(sample_roi_index)
            del sample_roi, sample_roi_index
            # サンプリングされたRoIの位置，サイズをGTに一致させるオフセットとスケール
            gt_roi_locs.append(gt_roi_loc)
            # サンプリングされたRoIに割り当てられたラベル
            gt_roi_labels.append(gt_roi_label)
            gt_roi_masks.append(gt_roi_mask)
            del gt_roi_loc, gt_roi_label, gt_roi_mask

        sample_rois = self.xp.concatenate(sample_rois, axis=0)
        sample_roi_indices = self.xp.concatenate(sample_roi_indices, axis=0)
        gt_roi_locs = self.xp.concatenate(gt_roi_locs, axis=0)
        gt_roi_labels = self.xp.concatenate(gt_roi_labels, axis=0)
        gt_roi_masks = self.xp.concatenate(gt_roi_masks, axis=0) # (2, 512, 14, 14) -> (1024, 14, 14)

        
        # 
        # 
        # (1024)
        # 
        # 

        # Head forward
        roi_cls_locs, roi_scores, roi_masks, roi_splines = self.mask_rcnn.head(
            features, sample_rois, sample_roi_indices)

        print('spline : ', spline.shape)
        print('roi_spline : ', roi_splines.shape)


        # RPN losses
        gt_rpn_locs = []
        gt_rpn_labels = []
        for bbox, rpn_loc, rpn_score in zip(bboxes, rpn_locs, rpn_scores):

            gt_rpn_loc, gt_rpn_label = self.anchor_target_creator(
                bbox, anchor, img_size)
            gt_rpn_locs.append(gt_rpn_loc)
            gt_rpn_labels.append(gt_rpn_label)
            del gt_rpn_loc, gt_rpn_label

        gt_rpn_locs = self.xp.concatenate(gt_rpn_locs, axis=0)
        gt_rpn_labels = self.xp.concatenate(gt_rpn_labels, axis=0)
        rpn_locs = F.concat(rpn_locs, axis=0)
        rpn_scores = F.concat(rpn_scores, axis=0)

        rpn_loc_loss = _fast_rcnn_loc_loss(
            rpn_locs, gt_rpn_locs, gt_rpn_labels, self.rpn_sigma)
        rpn_cls_loss = F.sigmoid_cross_entropy(rpn_scores, gt_rpn_labels)

        # ROI losses
        n_sample = len(roi_cls_locs)
        roi_cls_locs = roi_cls_locs.reshape((n_sample, -1, 4)) # (n_sample, n_cls, 4(h,w,y,x))
        roi_locs = roi_cls_locs[self.xp.arange(n_sample), gt_roi_labels]

        roi_loc_loss = _fast_rcnn_loc_loss(
            roi_locs, gt_roi_locs, gt_roi_labels, self.roi_sigma)
        roi_cls_loss = F.softmax_cross_entropy(roi_scores, gt_roi_labels)

        print(roi_splines[np.arange(n_sample), gt_roi_labels - 1, :, :].shape)
        print('gt_roi_labels : ', gt_roi_labels.shape)
        print('roi_masks : ', roi_masks.shape)
        print('gt_roi_masks : ', gt_roi_masks.shape)

        # mask branch losses
        # (1024, 14, 14)
        # (1024, 14, 14)
        roi_mask_loss = F.sigmoid_cross_entropy(
            roi_masks[np.arange(n_sample), gt_roi_labels - 1, :, :],
            gt_roi_masks)
        # (1)

        # keypoint branch loss
        # 
        # 
        # roi_spline_loss = F.softmax_cross_entropy(roi_splines, gt_roi_splines)


        loss = rpn_loc_loss + rpn_cls_loss + roi_loc_loss + roi_cls_loss + \
            roi_mask_loss # + roi_spline_loss
        chainer.reporter.report({'rpn_loc_loss': rpn_loc_loss,
                                 'rpn_cls_loss': rpn_cls_loss,
                                 'roi_loc_loss': roi_loc_loss,
                                 'roi_cls_loss': roi_cls_loss,
                                 'roi_mask_loss': roi_mask_loss,
                                #  'roi_spline_loss': roi_spline_loss,
                                 'loss': loss},
                                self)
        return loss


def _smooth_l1_loss(x, t, in_weight, sigma):
    sigma2 = sigma ** 2
    diff = in_weight * (x - t)
    abs_diff = F.absolute(diff)
    flag = (abs_diff.data < (1. / sigma2)).astype(np.float32)

    y = (flag * (sigma2 / 2.) * F.square(diff) +
         (1 - flag) * (abs_diff - 0.5 / sigma2))

    return F.sum(y)


def _fast_rcnn_loc_loss(pred_loc, gt_loc, gt_label, sigma):
    xp = chainer.cuda.get_array_module(pred_loc)

    in_weight = xp.zeros_like(gt_loc)
    # Localization loss is calculated only for positive rois.
    in_weight[gt_label > 0] = 1
    loc_loss = _smooth_l1_loss(pred_loc, gt_loc, in_weight, sigma)
    # Normalize by total number of negtive and positive rois.
    loc_loss /= xp.sum(gt_label >= 0)
    return loc_loss

# 元論文のロス

def _diversity_loss(pred, n_landmark, pool_size):
        pred_pool = tf.nn.pool(pred, window_shape=[pool_size, pool_size], strides=[1, 1], pooling_type="AVG", padding="VALID")
        # convert avg pool to sum pool
        # pred_pool = pred_pool * float(pool_size) * float(pool_size)
        pred_max = tf.reduce_max(pred_pool, axis=3)
        pred_max_sum = tf.reduce_sum(pred_max, axis=[1, 2])
        pred_max_sum = float(n_landmark) - pred_max_sum
        pred_max_sum = tf.reduce_mean(pred_max_sum)
        return pred_max_sum

def _align_loss(predA, predB, deformation, n_landmarks):
    

    # compute the mean of landmark locations

    batch_size = predA.get_shape()[0]
    pred_size = predA.get_shape()[1]
    index = tf.range(0, tf.cast(pred_size, tf.float32), delta=1, dtype=tf.float32)
    index = tf.reshape(index, [pred_size, 1])

    x_index = tf.tile(index, [1, pred_size])

    index = tf.transpose(index)

    y_index = tf.tile(index, [pred_size, 1])

    x_index = tf.expand_dims(x_index, 2)
    x_index = tf.expand_dims(x_index, 0)

    y_index = tf.expand_dims(y_index, 2)
    y_index = tf.expand_dims(y_index, 0)

    x_index = tf.tile(x_index, [batch_size, 1, 1, n_landmarks])
    y_index = tf.tile(y_index, [batch_size, 1, 1, n_landmarks])


    u_norm2 = tf.pow(x_index, 2.) + tf.pow(y_index, 2.)
    u_norm2 = u_norm2 * predA
    loss_part1 = tf.reduce_sum(u_norm2, axis=[1, 2])

    x_index_deformed = feature_warping2(x_index, deformation, padding=3)
    y_index_defomred = feature_warping2(y_index, deformation, padding=3)
    v_norm2 = tf.pow(x_index_deformed, 2.) + tf.pow(y_index_defomred, 2.)
    v_norm2 = v_norm2 * predB
    loss_part2 = tf.reduce_sum(v_norm2, axis=[1, 2])


    loss_part3x = tf.reduce_sum(x_index * predA, axis=[1, 2])
    loss_part3y = tf.reduce_sum(y_index * predA, axis=[1, 2])
    loss_part4x = tf.reduce_sum(x_index_deformed * predB, axis=[1, 2])
    loss_part4y = tf.reduce_sum(y_index_defomred * predB, axis=[1, 2])

    loss_part3 = loss_part3x * loss_part4x + loss_part3y * loss_part4y
    loss = loss_part1 + loss_part2 - 2. * loss_part3
    loss = tf.reduce_mean(loss)

    return loss