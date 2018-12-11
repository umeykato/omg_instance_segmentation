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

from chainercv.links.model.vgg.vgg16 import VGG16

from model import RegionProposalNetwork, Head


def main():
    # parser
    parser = argparse.ArgumentParser(
        description='Learning convnet from ILSVRC2012 dataset')
    parser.add_argument('--batchsize', '-B', type=int, default=2,
                        help='Learning minibatch size')
    parser.add_argument('--epoch', '-E', type=int, default=10000,
                        help='Number of epochs to train')
    parser.add_argument('--gpu', '-g', type=int, default=0,
                        help='GPU ID (negative value indicates CPU')
    parser.add_argument('--learning_rate', type=float, default=0.0002,
                        help='Learning rate')
    parser.add_argument('--snapshot_interval', type=int, default=50000)
    parser.add_argument('--resume', type=str, default=None)
    args = parser.parse_args()

    # model setting
    vgg_initialW = chainer.initializers.constant.Zero()
    extractor = VGG16(initialW=vgg_initialW)
    extractor.pick('conv5_3')
    extractor.remove_unused()

    rpn = RegionProposalNetwork()
    head = Head()

    if args.gpu >= 0:
        chainer.backends.cuda.get_device_from_id(args.gpu).use()
        rpn.to_gpu(args.gpu)
        head.to_gpu(args.gpu)






    # dataset setting
    train = PreprocessCifar(train)
    test = PreprocessCifar(test)
    train_iter = iterators.SerialIterator(train, args.batchsize)
    test_iter = iterators.SerialIterator(test, args.batchsize, False, False)

    # optimizer setting
    def create_optimizer(model, name="Adam", learning_rate=0.0002):
        if name == "Adam":
            optimizer = chainer.optimizers.Adam(alpha=learning_rate,beta1=0.5)
        elif name == "SGD":
            optimizer = chainer.optimizers.SGD(lr=learning_rate)
        optimizer.setup(model)
        return optimizer

    optimizer_gen = create_optimizer(gen)
    optimizer_dis = create_optimizer(dis)

    # updater setting
    #updater = training.StandardUpdater(train_iter, model_optimizer, device=args.gpu, loss_func=F.mean_squared_error)
    updater = GLCICUpdater(
        models=(gen, dis),
        iterator={'main': train_iter, 'test': test_iter},
        optimizer={'gen': optimizer_gen, 'dis': optimizer_dis},
        device=args.gpu
        )

    # trainer setting
    trainer = training.Trainer(updater, (args.epoch, 'epoch'), out='result')


    # extensions setting
    snapshot_interval = (args.snapshot_interval, 'iteration')

    @training.make_extension(trigger=snapshot_interval)
    def save_image(test_iter, trainer):
        model = trainer.updater.model
        input = test_iter.next()
        # print(type(input))


    trainer.extend(extensions.LogReport(), \
                    trigger=(10000, 'iteration'))
    trainer.extend(extensions.snapshot(filename='snapshot_iter-{.updater.iteration}.npz'), \
                                        trigger=snapshot_interval)
    # trainer.extend(extensions.Evaluator(test_iter, \
    #                                       model, \
    #                                       device=args.gpu), name='test')
    # trainer.extend(save_image(test_iter, trainer))
    trainer.extend(extensions.PrintReport(['epoch', 
                                            'dis/loss', 
                                            'gen/loss', 
                                            'gen/gen_loss', 
                                            'gen/pixel_loss', 
                                            'elapsed_time']), 
                                            trigger=(10000, 'iteration'))
    trainer.extend(extensions.ProgressBar(update_interval=10))

    if args.resume is not None:
        chainer.serializers.load_npz(args.resume, trainer)

    trainer.run()


if __name__ == '__main__':
    main()
