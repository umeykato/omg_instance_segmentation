#!/usr/bin/env python
import os
import sys

import chainer
import chainer.functions as F
from chainer import Variable
from chainer.dataset import concat_examples

import numpy as np
import cupy as cp

import cv2

class Updater(chainer.training.StandardUpdater):
    def __init__(self, is_training=True, alpha=4e-4, *args, **kwargs):
        self.extractor, self.rpn, self.head = kwargs.pop('models')
        self.is_training = is_training
        self.alpha = alpha
        super(Updater, self).__init__(*args, **kwargs)

    def loss_rpn(self, rpn, bboxes, rpn_locs, rpn_scores):
        rpn_sigma = 3.

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

        rpn_loc_loss = self._fast_rcnn_loc_loss(rpn_locs, gt_rpn_locs, gt_rpn_labels, self.rpn_sigma)
        rpn_cls_loss = F.sigmoid_cross_entropy(rpn_scores, gt_rpn_labels)

        loss = rpn_loc_loss + rpn_cls_loss

        return loss

    def loss_head(self, head, roi_cls_locs, roi_scores, gt_roi_locs, gt_roi_labels, gt_roi_masks):
        roi_sigma = 1.

        n_sample = len(roi_cls_locs)
        roi_cls_locs = roi_cls_locs.reshape((n_sample, -1, 4))
        roi_locs = roi_cls_locs[self.xp.arange(n_sample), gt_roi_labels]

        roi_loc_loss = self._fast_rcnn_loc_loss(roi_locs, gt_roi_locs, gt_roi_labels, self.roi_sigma)
        roi_cls_loss = F.softmax_cross_entropy(roi_scores, gt_roi_labels)
        roi_mask_loss = F.sigmoid_cross_entropy(roi_masks[np.arange(n_sample), gt_roi_labels - 1, :, :], gt_roi_masks)

        loss = roi_loc_loss + roi_cls_locs

        return loss

    def _smooth_l1_loss(self, x, t, in_weight, sigma):
        sigma2 = sigma ** 2
        diff = in_weight * (x - t)
        abs_diff = F.absolute(diff)
        flag = (abs_diff.data < (1. / sigma2)).astype(np.float32)

        y = (flag * (sigma2 / 2.) * F.square(diff) +
            (1 - flag) * (abs_diff - 0.5 / sigma2))

        return F.sum(y)


    def _fast_rcnn_loc_loss(self, pred_loc, gt_loc, gt_label, sigma):
        xp = chainer.cuda.get_array_module(pred_loc)

        in_weight = xp.zeros_like(gt_loc)
        # Localization loss is calculated only for positive rois.
        in_weight[gt_label > 0] = 1
        loc_loss = self._smooth_l1_loss(pred_loc, gt_loc, in_weight, sigma)
        # Normalize by total number of negtive and positive rois.
        loc_loss /= xp.sum(gt_label >= 0)
        return loc_loss
    

    def update_core(self):

        rpn_optimizer = self.get_optimizer('rpn')
        head_optimizer = self.get_optimizer('head')

        extractor, rpn, head = self.extractor, self.rpn, self.head

        batch = self.get_iterator('main').next()
        imgs, bboxes, labels, masks, scales = concat_examples(batch, self.device)

        

        '''extractor forward

        '''

        features = extractor(imgs)

        '''rpn forward

        '''
        rpn_locs, rpn_scores, rois, roi_indices, anchor = rpn(features, img_size, scales)


        '''rpn teach create

        '''

        sample_rois = self.xp.concatenate(sample_rois, axis=0)
        sample_roi_indices = self.xp.concatenate(sample_roi_indices, axis=0)
        gt_roi_locs = self.xp.concatenate(gt_roi_locs, axis=0)
        gt_roi_labels = self.xp.concatenate(gt_roi_labels, axis=0)
        gt_roi_masks = self.xp.concatenate(gt_roi_masks, axis=0)

        '''head forward

        '''

        roi_cls_locs, roi_scores, roi_masks = head(features, sample_rois, sample_roi_indices)


        '''loss calcurate

        '''

        rpn_optimizer.update(self.loss_rpn, rpn, bboxes, rpn_locs, rpn_scores)
        head_optimizer.update(self.loss_head, head, roi_cls_locs, roi_scores, gt_roi_locs, gt_roi_labels, gt_roi_masks)

if __name__=='__main__':
    pass