import os
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import csv
import colorsys
import argparse

# レンダリング時の色付け情報を取得
# partはleaf,stemから選択する
def get_color_list(csv_fname, part):
    color = []
    with open(csv_fname, 'r') as f:
        reader = csv.reader(f)
        age = 0
        type = None
        for row in reader:
            if row[0] == 'age':
                age = row[1]
                continue

            if row[0] == 'type':
                type = row[1]
                continue

            if type == part:
                color.append(list(map(float,row[1:4])))
                continue
                
    return color

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


    # root,read,saveディレクトリの指定（windowsとubuntuがごちゃ混ぜ）
    # root = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver4'
    # root = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver3'
    root = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_ver4'

    if os.name == 'nt':
        root = 'I:/ykato_git/datasets/omg_instance_segmentation/dataset_ver4'
    else:
        root = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver4'

    # read_dir = root + '/dataset_SemInsSpline/instance'
    # save_path = root + '/dataset_SemInsSpline/instance_segment'
    read_dir = root + '/dataset_arrange/instance'
    save_path = root + '/dataset_arrange/instance_segment'



    def instance_segment(age, location, img_num):
        fname = read_dir + '/age{}location{}_{:04}.png'.format(age, location, img_num)
        save_dir = save_path + '/age{}location{}_{:04}'.format(age, location, img_num)

        print(save_dir)
        try:
            os.mkdir(save_dir)
        except:
            pass

        # 画像を読み込み
        ins = cv2.imread(fname, 1)

        # 色のリストを作成
        h, w, c = ins.shape
        ins_temp = ins.reshape([h*w, c])
        color_list = np.unique(ins_temp, axis=0)
        del ins_temp

        # 実際の色csvからカラーリストを読み込む
        csv_fname = root + '/img/leaf_age{}/color_age{}.csv'.format(age, age)
        leaf_color_list_true = get_color_list(csv_fname, 'leaf')
        stem_color_list_true = get_color_list(csv_fname, 'stem')

        #真カラーとカラーリストを比較し，二乗誤差の低いものをマッチング
        #マッチングした色のマスク画像を保存
        #保存ファイル名はオブジェクト番号
        def get_index_color_match(leaf_color):

            # ガンマ補正をなくし，RBGをBGRに変更
            leaf_color = (np.power(leaf_color, 1/2.2) * 255)[::-1]

            # カラーリストとの平均二乗誤差を算出
            scores = []
            for i in range(color_list.shape[0]):
                score = ((leaf_color - color_list[i])**2).mean(axis=0)
                scores.append(score)

            return scores, np.array(scores).argmin()


        # レンダリング結果と色情報から，色ごとに分割した画像を保存するループ
        # 保存する画像名はオブジェクト番号と一致
        # ループ回数は葉のオブジェクト数と同じ
        color_list_index_list = []
        for i in range(len(leaf_color_list_true)):
            
            # 真カラーとカラーリストの平均二乗誤差，及び誤差が最小時のインデックス
            scores, color_list_index = get_index_color_match(np.array(leaf_color_list_true[i]))

            # 平均二乗誤差が10以上の場合，ループを抜ける
            if scores[color_list_index] > 10:
                continue

            # 誤差最小時のインデックスリスト
            color_list_index_list.append(color_list_index)

            # 重複するオブジェクトを選択した場合，ループを抜ける
            if not len(color_list_index_list) == len(set(color_list_index_list)):
                print(age, location, img_num, i, color_list_index)
                continue

            # RGBそれぞれで値が一致するか判定
            mask = np.where(ins[:,:,0] == color_list[color_list_index,0],True,False)
            mask *= np.where(ins[:,:,1] == color_list[color_list_index,1],True,False)
            mask *= np.where(ins[:,:,2] == color_list[color_list_index,2],True,False)
            
            # 判定結果を画像化
            mask = mask.astype(np.uint8) * 255
            
            # 画像を保存
            cv2.imwrite(save_dir + '/{}.png'.format(i), mask)

    # ループ回数は　生長時間(age) * 撮影の高さ位置(location) * 円上での撮影回数(img_num)
    start = args.start
    for age in range(100, 1100, 100):
        for location in range(5):
            for img_num in range(100):
                instance_segment(age, location, img_num)


if __name__=='__main__':
    main()

    
