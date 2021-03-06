from chainercv import transforms

class MaskRCNNTransform(object):

    def __init__(self, mask_rcnn, train=True):
        self.mask_rcnn = mask_rcnn
        self.train = train

    def __call__(self, in_data):
        # print(len(in_data))
        if len(in_data) == 6:
            img, bbox, label, mask, crowd, area = in_data
        elif len(in_data) == 5:
            img, bbox, label, mask, spline = in_data
        else:
            raise ValueError

        img = img.transpose(2, 0, 1)  # H, W, C -> C, H, W

        if not self.train:
            if len(in_data) == 6:
                return img, bbox, label, mask, crowd, area
            elif len(in_data) == 5:
                return img, bbox, label, mask, spline
            else:
                raise ValueError

        imgs, sizes, scales = self.mask_rcnn.prepare([img])
        # print(type(imgs))
        # print(type(sizes))
        # print(type(scales))

        img = imgs[0]
        H, W = sizes[0]
        scale = scales[0]
        _, o_H, o_W = img.shape

        if len(bbox) > 0:
            bbox = transforms.resize_bbox(bbox, (H, W), (o_H, o_W))
        if len(mask) > 0:
            mask = transforms.resize(
                mask, size=(o_H, o_W), interpolation=0)

        if len(spline) > 0:
            spline = spline * scale

        # # horizontally flip
        # img, params = transforms.random_flip(
        #     img, x_random=True, return_param=True)
        # bbox = transforms.flip_bbox(
        #     bbox, (o_H, o_W), x_flip=params['x_flip'])
        # if mask.ndim == 2:
        #     mask = transforms.flip(
        #         mask[None, :, :], x_flip=params['x_flip'])[0]
        # else:
        #     mask = transforms.flip(mask, x_flip=params['x_flip'])

        # print(H,W)
        # print(o_H, o_W)
        # print(scale)

        def flip_spline(spline, y_flip=False, x_flip=False):
            if y_flip:
                spline[:,:,1] = o_H - spline[:,:,1]

            if x_flip:
                spline[:,:,0] = o_W - spline[:,:,0]

            return spline

        # horizontally and vartically flip
        img, params = transforms.random_flip(
            img, y_random=True, x_random=True, return_param=True)
        bbox = transforms.flip_bbox(
            bbox, (o_H, o_W), y_flip=params['y_flip'], x_flip=params['x_flip'])
        if mask.ndim == 2:
            mask = transforms.flip(
                mask[None, :, :], y_flip=params['y_flip'], x_flip=params['x_flip'])[0]
        else:
            mask = transforms.flip(mask, y_flip=params['y_flip'], x_flip=params['x_flip'])

        spline = flip_spline(spline, y_flip=params['y_flip'], x_flip=params['x_flip'])

        return img, bbox, label, mask, spline, scale, sizes
