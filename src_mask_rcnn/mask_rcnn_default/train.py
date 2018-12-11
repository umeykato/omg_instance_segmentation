#!/usr/bin/env python

import os.path as osp
import sys

import chainer

sys.path.append(osp.join(osp.dirname(__file__), '..'))
import chainer_mask_rcnn as cmr

here = osp.dirname(osp.abspath(__file__))  # NOQA
sys.path.insert(0, osp.join(here, '..'))  # NOQA

import train_common
import dataset


def main():
    args = train_common.parse_args()

    args.logs_dir = osp.join(here, 'logs')

    # Dataset.
    # args.dataset = 'coco'
    # train_data = chainer.datasets.ConcatenatedDataset(
    #     cmr.datasets.COCOInstanceSegmentationDataset('train'),
    #     cmr.datasets.COCOInstanceSegmentationDataset('valminusminival'),
    # )
    
    # test_data = cmr.datasets.COCOInstanceSegmentationDataset(
    #     'minival',
    #     use_crowd=True,
    #     return_crowd=True,
    #     return_area=True,
    # )
    # args.class_names = tuple(test_data.class_names.tolist())

    args.dataset = 'original'
    train_data = dataset.OomugiDataset()
    test_data = dataset.OomugiDataset(test=True)
    args.class_names = ['leaf']

    # Model.
    args.min_size = 800
    args.max_size = 1333
    args.anchor_scales = (2, 4, 8, 16, 32)
    args.ratios = (0.11, 0.14, 0.2, 0.25, 0.33, 0.5, 1, 2, 3, 4, 5, 7, 9)

    # Run training!.
    train_common.train(
        args=args,
        train_data=train_data,
        test_data=test_data,
        evaluator_type='coco',
    )


if __name__ == '__main__':
    main()
