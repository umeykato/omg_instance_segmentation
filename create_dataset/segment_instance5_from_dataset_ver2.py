import os
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import csv
import colorsys
import argparse

def main():
    parser = argparse.ArgumentParser(
                prog='segment_instance5_from_dataset_ver2',
                usage='create instance image',
                description='description',
                epilog='end',
                add_help=True,
                )

    parser.add_argument('--start', '-S', type=int, default=100,
                        help='select start age')

    args = parser.parse_args()

    # root = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver3'
    root = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver3'

    read_dir = root + '/dataset_SemInsSpline/instance'
    save_path = root + '/dataset_SemInsSpline/instance_segment'


    start = args.start
    for age in range(start, start+100, 100):
        for location in range(5):
            for img_num in range(100):
                fname = read_dir + '/age{}location{}_{:04}.png'.format(age, location, img_num)
                save_dir = save_path + '/age{}location{}_{:04}'.format(age, location, img_num)
                print(save_dir)
                try:
                    os.mkdir(save_dir)
                except:
                    pass

                ins = cv2.imread(fname, 1)
                color_list = np.array([[255, 255, 255]])

                # 色のリストを作成
                for h in range(ins.shape[0]):
                    for w in range(ins.shape[1]):
                        if not np.allclose(ins[h, w], [255, 255, 255]): #白色[255,255,255]であるか比較

                            flag = 0
                            for l in range(color_list.shape[0]):         #カラーリストを探索
                                if np.allclose(ins[h, w], color_list[l]):#カラーリストに存在すればフラグを１にする
                                    flag = 1

                            if flag == 0:#フラグが１であればカラーリストに追加
                                color_list = np.append(color_list, [ins[h, w]], axis=0)

                #カラーリストの色ごとの画像を保存
                for l in range(color_list.shape[0]):
                    a = np.where(ins[:,:,0] == color_list[l,0],True,False)
                    b = np.where(ins[:,:,1] == color_list[l,1],True,False)
                    c = np.where(ins[:,:,2] == color_list[l,2],True,False)
                    d = a*b*c
                    
                    img = d.astype(np.uint8) * 255
                    
                    cv2.imwrite(save_dir + '/{}.png'.format(l), img)

if __name__=='__main__':
    
    # read_color_hsv2rgb()

    # for time in range(400, 1100, 100):
    #     for view in range(5):        
    #         create_instance_image(time, view)

    # for view in range(3,5):
    #     create_instance_image(1000, view)

    # create_instance_image(900, 4)

    main()

    
