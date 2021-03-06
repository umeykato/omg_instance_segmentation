from __future__ import print_function

import argparse
import datetime
import functools
import os
import os.path as osp
import random
import socket
import sys

import matplotlib.pyplot as plt
plt.switch_backend('agg')  # NOQA

import chainer
from chainer import training
from chainer.training import extensions
import fcn
import numpy as np
import cupy as xp
import cv2

sys.path.append(osp.join(osp.dirname(__file__), '..'))
import chainer_mask_rcnn as cmr


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--model',
        '-m',
        choices=['vgg16', 'resnet50', 'resnet101'],
        default='vgg16',
        # default='resnet50',
        help='base model',
    )
    parser.add_argument(
        '--pooling-func',
        '-p',
        choices=['pooling', 'align', 'resize'],
        default='align',
        help='pooling function',
    )
    parser.add_argument('--gpu', '-g', type=int, help='gpu id')
    parser.add_argument(
        '--multi-node',
        '-n',
        action='store_true',
        help='use multi node',
    )
    parser.add_argument(
        '--roi-size',
        '-r',
        type=int,
        # default=14,
        default=7,
        help='roi size',
    )
    parser.add_argument(
        '--initializer',
        choices=['normal', 'he_normal'],
        default='normal',
        help='initializer',
    )
    # (180e3 * 8) / len(coco_trainval)
    default_max_epoch = (180e3 * 8) / 118287
    default_max_epoch = 1000
    parser.add_argument(
        '--max-epoch',
        type=float,
        default=default_max_epoch,
        help='max epoch',
    )
    parser.add_argument(
        '--batch-size-per-gpu',
        type=int,
        default=2,
        help='batch size / gpu',
    )
    parser.add_argument(
        '--resume',
        type=str,
        default='I:/ykato_git/result/omg_instance_segmentation/mask_rnn_log/20181211_122853-o/snapshot_model_0.npz',
        help='load trainer parameter'
    )
    return parser.parse_args()


def train(args, train_data, test_data, evaluator_type):
    required_args = [
        'dataset',
        'class_names',
        'logs_dir',
        'min_size',
        'max_size',
        'anchor_scales',
        'ratios',
    ]
    for arg_key in required_args:
        if not hasattr(args, arg_key):
            raise ValueError(
                'args must contain required key: {}'.format(arg_key)
            )

    assert evaluator_type in ['voc', 'coco'], \
        'Unsupported evaluator_type: {}'.format(evaluator_type)

    if args.multi_node:
        import chainermn

        comm = chainermn.create_communicator('hierarchical')
        device = comm.intra_rank

        args.n_node = comm.inter_size
        args.n_gpu = comm.size
        chainer.cuda.get_device_from_id(device).use()
    else:
        if args.gpu is None:
            print(
                'Option --gpu is required without --multi-node.',
                file=sys.stderr,
            )
            sys.exit(1)
        args.n_node = 1
        args.n_gpu = 1
        chainer.cuda.get_device_from_id(args.gpu).use()
        device = args.gpu

    args.seed = 0
    now = datetime.datetime.now()
    args.timestamp = now.isoformat()
    # args.out = osp.join(args.logs_dir, now.strftime('%Y%m%d_%H%M%S'))
    args.out = '../../../result/omg_instance_segmentation/mask_rnn_log/' + now.strftime('%Y%m%d_%H%M%S')

    args.batch_size = args.batch_size_per_gpu * args.n_gpu

    # lr: 0.00125 * 8 = 0.01  in original
    # args.lr = 0.00125 * args.batch_size
    args.lr = 0.00125
    args.weight_decay = 0.0001

    # lr / 10 at 120k iteration with
    # 160k iteration * 16 batchsize in original
    args.step_size = [
        (120e3 / 180e3) * args.max_epoch,
        (160e3 / 180e3) * args.max_epoch,
    ]

    random.seed(args.seed)
    np.random.seed(args.seed)

    if args.pooling_func == 'align':
        pooling_func = cmr.functions.roi_align_2d
    elif args.pooling_func == 'pooling':
        pooling_func = cmr.functions.roi_pooling_2d
    elif args.pooling_func == 'resize':
        pooling_func = cmr.functions.crop_and_resize
    else:
        raise ValueError(
            'Unsupported pooling_func: {}'.format(args.pooling_func)
        )

    if args.initializer == 'normal':
        mask_initialW = chainer.initializers.Normal(0.01)
    elif args.initializer == 'he_normal':
        mask_initialW = chainer.initializers.HeNormal(fan_option='fan_out')
    else:
        raise ValueError(
            'Unsupported initializer: {}'.format(args.initializer)
        )

    if args.model == 'vgg16':
        mask_rcnn = cmr.models.MaskRCNNVGG16(
            # n_fg_class=len(args.class_names),
            n_fg_class=1,
            pretrained_model='imagenet',
            pooling_func=pooling_func,
            # ratios=(0.5, 1, 2),
            ratios=args.ratios,
            anchor_scales=args.anchor_scales,
            roi_size=args.roi_size,
            min_size=args.min_size,
            max_size=args.max_size,
            mask_initialW=mask_initialW,
        )
    elif args.model in ['resnet50', 'resnet101']:
        n_layers = int(args.model.lstrip('resnet'))
        mask_rcnn = cmr.models.MaskRCNNResNet(
            n_layers=n_layers,
            # n_fg_class=len(args.class_names),
            n_fg_class=1,
            pooling_func=pooling_func,
            anchor_scales=args.anchor_scales,
            roi_size=args.roi_size,
            min_size=args.min_size,
            max_size=args.max_size,
            mask_initialW=mask_initialW,
        )
    else:
        raise ValueError('Unsupported model: {}'.format(args.model))
    model = cmr.models.MaskRCNNTrainChain(mask_rcnn)
    if args.multi_node or args.gpu >= 0:
        model.to_gpu()

    # print(model)

    optimizer = chainer.optimizers.MomentumSGD(lr=args.lr, momentum=0.9)
    if args.multi_node:
        optimizer = chainermn.create_multi_node_optimizer(optimizer, comm)
    optimizer.setup(model)
    optimizer.add_hook(chainer.optimizer.WeightDecay(rate=args.weight_decay))

    if args.model in ['resnet50', 'resnet101']:
        # ResNetExtractor.freeze_at is not enough to freeze params
        # since WeightDecay updates the param little by little.
        mask_rcnn.extractor.conv1.disable_update()
        mask_rcnn.extractor.bn1.disable_update()
        mask_rcnn.extractor.res2.disable_update()
        for link in mask_rcnn.links():
            if isinstance(link, cmr.links.AffineChannel2D):
                link.disable_update()

    train_data = chainer.datasets.TransformDataset(
        train_data,
        cmr.datasets.MaskRCNNTransform(mask_rcnn),
    )
    test_data = chainer.datasets.TransformDataset(
        test_data,
        cmr.datasets.MaskRCNNTransform(mask_rcnn, train=False),
    )
    if args.multi_node:
        if comm.rank != 0:
            train_data = None
            test_data = None
        train_data = chainermn.scatter_dataset(train_data, comm, shuffle=True)
        test_data = chainermn.scatter_dataset(test_data, comm)

    # FIXME: MultiProcessIterator sometimes hangs
    train_iter = chainer.iterators.SerialIterator(
        train_data,
        batch_size=args.batch_size_per_gpu,
    )
    test_iter = chainer.iterators.SerialIterator(
        test_data,
        batch_size=args.batch_size_per_gpu,
        repeat=False,
        shuffle=False,
    )

    converter = functools.partial(
        cmr.datasets.concat_examples,
        padding=0,
        # img, bboxes, labels, masks, scales
        indices_concat=[0, 2, 3, 4],  # img, _, labels, masks, scales
        indices_to_device=[0, 1],  # img, bbox
    )
    updater = chainer.training.updater.StandardUpdater(
        train_iter,
        optimizer,
        device=device,
        converter=converter,
    )

    trainer = training.Trainer(
        updater,
        (args.max_epoch, 'epoch'),
        out=args.out,
    )

    trainer.extend(
        extensions.ExponentialShift('lr', 0.1),
        trigger=training.triggers.ManualScheduleTrigger(
            args.step_size,
            'epoch',
        ),
    )

    if args.resume is not None:
        chainer.serializers.load_npz(args.resume, model.mask_rcnn)

    eval_interval = 1000, 'iteration'
    log_interval = 20, 'iteration'
    plot_interval = 0.1, 'epoch'
    print_interval = 20, 'iteration'
    snapshot_interval = 5000, 'iteration'

    if evaluator_type == 'voc':
        evaluator = cmr.extensions.InstanceSegmentationVOCEvaluator(
            test_iter,
            model.mask_rcnn,
            device=device,
            use_07_metric=True,
            label_names=args.class_names,
        )
    elif evaluator_type == 'coco':
        evaluator = cmr.extensions.InstanceSegmentationCOCOEvaluator(
            test_iter,
            model.mask_rcnn,
            device=device,
            label_names=args.class_names,
        )
    else:
        raise ValueError(
            'Unsupported evaluator_type: {}'.format(evaluator_type)
        )
    if args.multi_node:
        evaluator = chainermn.create_multi_node_evaluator(evaluator, comm)
    trainer.extend(evaluator, trigger=eval_interval)

    if not args.multi_node or comm.rank == 0:
        # Save snapshot.
        trainer.extend(
            extensions.snapshot_object(model.mask_rcnn, 'snapshot_model_{}.npz'.format(trainer.updater.epoch)),
            # trigger=training.triggers.MaxValueTrigger(
            #     'validation/main/map',
            #     eval_interval,
            # ),
            # trigger=(1, 'epoch'),
            trigger=snapshot_interval,
        )

        trainer.extend(
            extensions.snapshot(filename='snapshot_trainer_iter-{}.npz'.format(trainer.updater.iteration)),
            # tringger=training.triggers.MaxValueTrigger(
            #     'validation/main/map',
            #     eval_interval,
            # ),
            trigger=snapshot_interval,
        )

        # Dump params.yaml.
        args.git_hash = cmr.utils.git_hash()
        args.hostname = socket.gethostname()
        trainer.extend(fcn.extensions.ParamsReport(args.__dict__))

        # Visualization.
        trainer.extend(
            cmr.extensions.InstanceSegmentationVisReport(
                test_iter,
                model.mask_rcnn,
                label_names=args.class_names,
            ),
            trigger=eval_interval,
        )

        # Logging.
        trainer.extend(
            chainer.training.extensions.observe_lr(),
            trigger=log_interval,
        )
        trainer.extend(extensions.LogReport(trigger=log_interval))
        trainer.extend(
            extensions.PrintReport(
                [
                    'iteration',
                    'epoch',
                    'elapsed_time',
                    'lr',
                    'main/loss',
                    'main/roi_loc_loss',
                    'main/roi_cls_loss',
                    'main/roi_mask_loss',
                    'main/rpn_loc_loss',
                    'main/rpn_cls_loss',
                    'validation/main/map',
                ],
            ),
            trigger=print_interval,
        )
        trainer.extend(extensions.ProgressBar(update_interval=10))

        # Plot.
        assert extensions.PlotReport.available()
        trainer.extend(
            extensions.PlotReport(
                [
                    'main/loss',
                    'main/roi_loc_loss',
                    'main/roi_cls_loss',
                    'main/roi_mask_loss',
                    'main/rpn_loc_loss',
                    'main/rpn_cls_loss',
                ],
                file_name='loss.png',
                trigger=plot_interval,
            ),
            trigger=plot_interval,
        )
        trainer.extend(
            extensions.PlotReport(
                ['validation/main/map'],
                file_name='accuracy.png',
                trigger=plot_interval,
            ),
            trigger=eval_interval,
        )

        trainer.extend(extensions.dump_graph('main/loss'))

    # trainer.run()


    def visualize(imgs, bboxes, masks, labels, scores):
        score_thresh = 0.7

        print(imgs.shape)

        dst = []
        for img, bbox, mask, label, score \
            in zip(imgs, bboxes, masks, labels, scores):

            keep = score >= score_thresh
            bbox = bbox[keep]
            label = label[keep]
            mask = mask[keep]
            score = score[keep]

            captions = []
            for p_score in score:
                caption = 'leaf {:.1%}'.format(p_score)
                captions.append(caption)

            viz = cmr.utils.draw_instance_bboxes(
                img, bbox, label+1, n_class=2,
                masks=mask, captions=captions, bg_class=0)

            dst.append(viz)

        return dst

    predict_dir = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_DIA/image'
    mask_dir = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_DIA/label'
    save_dir = './predict_DIA_noMask'

    fnames = os.listdir(predict_dir)

    for fname in fnames:
        print(osp.join(predict_dir, fname))
        img = cv2.imread(osp.join(predict_dir, fname))
        # mask = cv2.imread(osp.join(mask_dir, fname)) / 255
        # white = np.ones(img.shape) * 255

        # img = img * mask + white * (1-mask)
        # print(img.dtype)
        img = img.transpose(2, 0, 1)[None,:,:,:].astype(np.uint8)

        # img_variable = chainer.Variable(xp.array(img))

        bboxes, masks, labels, scores = model.mask_rcnn.predict(img)

        output = visualize(img.transpose(0,2,3,1), bboxes, masks, labels, scores)

        for p_output in output:
            cv2.imwrite(osp.join(save_dir, fname), p_output)




