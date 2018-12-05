#
#   カラー画像，インスタンスセグメンテーション画像，セマンティックセグメンテーション画像を作成
#

import bpy
import os
import math
import sys
#import texture

import csv
sys.path.append(os.getcwd())
import camera
import copy

def delete_all():
    for item in bpy.context.scene.objects:
        bpy.context.scene.objects.unlink(item)

    for item in bpy.data.objects:
        bpy.data.objects.remove(item)

    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)

    for item in bpy.data.materials:
        bpy.data.materials.remove(item)

def render2color(obj_fname, save_dir):
    delete_all()

    #Worldに関する設定
    world = bpy.data.worlds['World'] # 編集する World の取得
    world.horizon_color = (1.0, 1.0, 1.0)
    world.zenith_color = (1.0, 1.0, 1.0)
    world.ambient_color = (0.01, 0.01, 0.01)
    #world.light_settings.use_ambient_occlusion = True # 環境光を使う
    world.light_settings.ao_factor = 1.0 # 環境光の明るさ
    world.light_settings.use_environment_light=True
    world.use_sky_blend=True
    world.light_settings.use_ambient_occlusion=True

    #照明を太陽光にする
    # lamp=bpy.data.objects['Lamp']
    # lamp.data.type='SUN'
    # lamp.location=(0,40,50)

    #objファイルのimport
    # bpy.ops.import_scene.obj(filepath='./plant_obj/original/all/adel400nsect1.obj')
    bpy.ops.import_scene.obj(filepath=obj_fname)
    sel = bpy.context.selected_objects
    leaf=sel[:]

    #選択オブジェクトを代入
    sel = bpy.context.selected_objects

    #active?
    act = bpy.context.active_object

    #厚み付け，細分割曲面
    for obj in sel:
        bpy.context.scene.objects.active = obj #sets the obj accessible to bpy.ops
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.05
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels=3
        obj.data.materials.clear()

        bpy.context.scene.objects.active = obj
        bpy.ops.mesh.uv_texture_add()
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)

    #厚み付け
    for obj in sel:
        bpy.context.scene.objects.active = obj #sets the obj accessible to bpy.ops
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.05
        #bpy.ops.object.modifier_add(type='SUBSURF')
        #bpy.context.object.modifiers["Subsurf"].levels=0
        obj.data.materials.clear()

        bpy.context.scene.objects.active = obj
        bpy.ops.mesh.uv_texture_add()
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)

    sel = bpy.context.selected_objects
    leaf2=sel[:]
    #leaf.extend(leaf2)

    # オブジェクトの回転
    for obj in sel:
        bpy.context.scene.objects.active = obj
        # bpy.ops.transform.rotate(value=-3.14/2,axis=(0,-1,0))
        obj.rotation_euler = (0,0,0)

    #オブジェクトの選択
    for i in sel:
        i.select=False
        # i.select=True

    for i in leaf:
        i.select=True
        # i.select=False

    sel=bpy.context.selected_objects

    for obj in sel:
        mat1 = bpy.data.materials.new('GREEN')
        tex1 = bpy.data.textures.new('Texture', type='IMAGE')
        bpy.ops.texture.new('INVOKE_DEFAULT')
        # bpy.ops.image.open(filepath='C:/Users/matsuoka/Desktop/sub.jpg')
        # tex1.image = bpy.data.images.load('C:/Users/matsuoka/Desktop/ko.png')
        tex1.image = bpy.data.images.load(os.getcwd() + '/ko.PNG')
        mat1.texture_slots.add()
        mat1.texture_slots[0].texture = tex1
        bpy.context.scene.objects.active = obj
        obj.data.materials.append(mat1)

    for i in sel:
        i.select=False

    for i in leaf2:
        i.select=True

    sel=bpy.context.selected_objects

    #テクスチャ付け
    for obj1 in sel:
        mat2 = bpy.data.materials.new('BLUE')
        tex2 = bpy.data.textures.new('Texture', type='IMAGE')
        bpy.ops.texture.new('INVOKE_DEFAULT')
        # bpy.ops.image.open(filepath='C:/Users/matsuoka/Desktop/sub.jpg')
        # tex2.image = bpy.data.images.load('C:/Users/matsuoka/Desktop/ko.png')
        tex2.image = bpy.data.images.load(os.getcwd() + '/ko.PNG')
        mat2.texture_slots.add()
        mat2.texture_slots[0].texture = tex2
        bpy.context.scene.objects.active = obj1
        obj1.data.materials.append(mat2)

    #カメラ撮影
    camera.setCirclePathCamera(1, save_dir)

def render2semantic(obj_fname, save_dir):
    delete_all()

    #Worldに関する設定
    world = bpy.data.worlds['World'] # 編集する World の取得
    world.horizon_color = (1.0, 1.0, 1.0)
    world.zenith_color = (1.0, 1.0, 1.0)
    world.ambient_color = (0.01, 0.01, 0.01)
    #world.light_settings.use_ambient_occlusion = True # 環境光を使う
    world.light_settings.ao_factor = 1.0 # 環境光の明るさ
    world.light_settings.use_environment_light=True
    world.use_sky_blend=True
    world.light_settings.use_ambient_occlusion=True

    #照明を太陽光にする
    # lamp=bpy.data.objects['Lamp']
    # lamp.data.type='SUN'
    # lamp.location=(0,40,50)

    #objファイルのimport
    # bpy.ops.import_scene.obj(filepath='./plant_obj/original/all/adel400nsect1.obj')
    bpy.ops.import_scene.obj(filepath=obj_fname)
    sel = bpy.context.selected_objects
    leaf=sel[:]

    #選択オブジェクトを代入
    sel = bpy.context.selected_objects

    #active?
    act = bpy.context.active_object

    #厚み付け，細分割曲面
    for obj in sel:
        bpy.context.scene.objects.active = obj #sets the obj accessible to bpy.ops
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.05
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels=3
        obj.data.materials.clear()

        bpy.context.scene.objects.active = obj
        bpy.ops.mesh.uv_texture_add()
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)

    #厚み付け
    for obj in sel:
        bpy.context.scene.objects.active = obj #sets the obj accessible to bpy.ops
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.05
        #bpy.ops.object.modifier_add(type='SUBSURF')
        #bpy.context.object.modifiers["Subsurf"].levels=0
        obj.data.materials.clear()

        bpy.context.scene.objects.active = obj
        bpy.ops.mesh.uv_texture_add()
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)

    sel = bpy.context.selected_objects
    leaf2=sel[:]
    #leaf.extend(leaf2)

    # オブジェクトの回転
    for obj in sel:
        bpy.context.scene.objects.active = obj
        # bpy.ops.transform.rotate(value=-3.14/2,axis=(0,-1,0))
        obj.rotation_euler = (0,0,0)

    #オブジェクトの選択
    for i in sel:
        i.select=False
        # i.select=True

    for i in leaf:
        i.select=True
        # i.select=False

    sel=bpy.context.selected_objects

    for obj in sel:
        mat1 = bpy.data.materials.new('GREEN')
        tex1 = bpy.data.textures.new('Texture', type='IMAGE')
        bpy.ops.texture.new('INVOKE_DEFAULT')
        # bpy.ops.image.open(filepath='C:/Users/matsuoka/Desktop/sub.jpg')
        # tex1.image = bpy.data.images.load('C:/Users/matsuoka/Desktop/ko.png')
        tex1.image = bpy.data.images.load(os.getcwd() + '/ko.PNG')
        mat1.texture_slots.add()
        mat1.texture_slots[0].texture = tex1
        bpy.context.scene.objects.active = obj
        obj.data.materials.append(mat1)

    for i in sel:
        i.select=False

    for i in leaf2:
        i.select=True

    sel=bpy.context.selected_objects

    #テクスチャ付け
    for obj1 in sel:
        mat2 = bpy.data.materials.new('BLUE')
        tex2 = bpy.data.textures.new('Texture', type='IMAGE')
        bpy.ops.texture.new('INVOKE_DEFAULT')
        # bpy.ops.image.open(filepath='C:/Users/matsuoka/Desktop/sub.jpg')
        # tex2.image = bpy.data.images.load('C:/Users/matsuoka/Desktop/ko.png')
        tex2.image = bpy.data.images.load(os.getcwd() + '/ko.PNG')
        mat2.texture_slots.add()
        mat2.texture_slots[0].texture = tex2
        bpy.context.scene.objects.active = obj1
        obj1.data.materials.append(mat2)

    #テクスチャ削除
    for obj in sel:
        obj.data.materials.clear()
    for i in sel:
        i.select=False

    for i in leaf:
        i.select=True

    sel=bpy.context.selected_objects

    #緑色テクスチャ
    for obj in sel:
        mat1 = bpy.data.materials.new('GREEN')
        tex1 = bpy.data.textures.new('Texture', type='IMAGE')
        bpy.ops.texture.new('INVOKE_DEFAULT')
        # bpy.ops.image.open(filepath='C:/Users/matsuoka/Desktop/sub.jpg')
        # tex1.image = bpy.data.images.load('C:/Users/matsuoka/Desktop/green.png')
        tex1.image = bpy.data.images.load(os.getcwd() + '/green.png')
        mat1.texture_slots.add()
        mat1.texture_slots[0].texture = tex1
        bpy.context.scene.objects.active = obj
        obj.data.materials.append(mat1)

    for i in sel:
        i.select=False

    # for i in leaf2:
    #     i.select=True

    sel=bpy.context.selected_objects

    #青色テクスチャ
    for obj1 in sel:
        mat2 = bpy.data.materials.new('BLUE')
        tex2 = bpy.data.textures.new('Texture', type='IMAGE')
        bpy.ops.texture.new('INVOKE_DEFAULT')
        # bpy.ops.image.open(filepath='C:/Users/matsuoka/Desktop/sub.jpg')
        # tex2.image = bpy.data.images.load('C:/Users/matsuoka/Desktop/blue.png')
        tex2.image = bpy.data.images.load(os.getcwd() + '/blue.png')
        mat2.texture_slots.add()
        mat2.texture_slots[0].texture = tex2
        bpy.context.scene.objects.active = obj1
        obj1.data.materials.append(mat2)

    #質感変更
    for item in bpy.data.materials:
        item.diffuse_shader=('FRESNEL')
        item.diffuse_fresnel=1.0
        item.emit=1.0
        item.specular_intensity=0.0
        item.ambient=0.0
        item.translucency=0.0
        item.use_raytrace=False
        item.use_mist=False

    # lamp=bpy.data.objects['Lamp']
    bpy.data.scenes["Scene"].render.use_antialiasing=False

    #lamp.data.type='SUN'
    #lamp.location=(0,30,40)
    camera.setCirclePathCamera(2, save_dir)

def render2instance(leaf_dname, stem_dname, save_dir):
    delete_all()

    #Worldに関する設定
    world = bpy.data.worlds['World'] # 編集する World の取得
    world.horizon_color = (1.0, 1.0, 1.0)
    world.zenith_color = (1.0, 1.0, 1.0)
    world.ambient_color = (0.01, 0.01, 0.01)
    #world.light_settings.use_ambient_occlusion = True # 環境光を使う
    world.light_settings.ao_factor = 1.0 # 環境光の明るさ
    world.light_settings.use_environment_light=True
    world.use_sky_blend=True
    world.light_settings.use_ambient_occlusion=True

    #照明を太陽光にする
    # lamp=bpy.data.objects['Lamp']
    # lamp.data.type='SUN'
    # lamp.location=(0,40,50)

    '''
    #objファイルのimport
    # bpy.ops.import_scene.obj(filepath='./plant_obj/original/all/adel900nsect1.obj')
    bpy.ops.import_scene.obj(filepath=obj_fname)
    sel = bpy.context.selected_objects

    #色のテクスチャ環境作成
    for obj1 in sel:
        obj1.data.materials.clear()
        mat2 = bpy.data.materials.new('COLOR')
        obj1.data.materials.append(mat2)

    #color変更
    j=0
    for item in bpy.data.materials:
        item.diffuse_color.hsv=(j*0.1,1.0,0.4)
        j+=0.15
        # print('bgr = ', item.diffuse_color.bgr)
        print(item.diffuse_color.hsv)
    #exit()

    #csv書き込み
    basename = os.path.basename(obj_fname)
    root_ext_pair = os.path.splitext(basename)
    print(basename)
    print(root_ext_pair)
    with open(save_dir + '/' + root_ext_pair[0] + '.csv','w',newline='') as f:
        writer=csv.writer(f)
        #print('materials num  ', bpy.data.materials)

        for item in bpy.data.materials:
            writer.writerow([item.diffuse_color.r, item.diffuse_color.g, item.diffuse_color.b])
        f.close()

    #bpy.ops.import_scene.obj(filepath='E:/share/compare/0/adel900nsect1.obj')
    sel = bpy.context.selected_objects
    leaf=sel[:]
    '''

    def import_obj_and_write_color(dname, type='leaf', saturation):
        sat = saturation
        fn = len(os.listdir(dname))

        for i in range(fn):
            obj_fname = dname + '/' + '{}.obj'.format(i)
            #objファイルのimport
            bpy.ops.import_scene.obj(filepath=obj_fname)
            sel = bpy.context.selected_objects
            #色のテクスチャ環境作成
            for obj1 in sel:
                obj1.data.materials.clear()
                mat2 = bpy.data.materials.new('COLOR')
                obj1.data.materials.append(mat2)

            #color変更
            j=0
            for item in bpy.data.materials:
                item.diffuse_color.hsv=(j*0.1,1.0,0.4)
                j+=0.15
            #exit()

            #csv書き込み
            basename = os.path.basename(obj_fname)
            root_ext_pair = os.path.splitext(basename)
            print(basename)
            print(root_ext_pair)
            with open(save_dir + '/' + root_ext_pair[0] + '.csv','w',newline='') as f:
                writer=csv.writer(f)
                #print('materials num  ', bpy.data.materials)

                for item in bpy.data.materials:
                    writer.writerow([item.diffuse_color.r, item.diffuse_color.g, item.diffuse_color.b])
                f.close()

            #bpy.ops.import_scene.obj(filepath='E:/share/compare/0/adel900nsect1.obj')
            sel = bpy.context.selected_objects
            leaf=sel[:]

        
    saturation = 0
    saturation = import_obj_and_write_color(leaf_dname, type='leaf', saturation)
    saturation = import_obj_and_write_color(stem_dname, type='stem', saturation)

    



    #全要素を代入
    sel = bpy.context.selected_objects

    #active?
    act = bpy.context.active_object

    #厚み付け・細分割曲面
    for obj in sel:
        bpy.context.scene.objects.active = obj #sets the obj accessible to bpy.ops
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.05
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels=3
        #obj.data.materials.clear()

        # bpy.context.scene.objects.active = obj
        # bpy.ops.mesh.uv_texture_add()
        # bpy.ops.object.editmode_toggle()
        # bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)

    # bpy.ops.import_scene.obj(filepath='./plant_obj/original/all/adel900nsect1.obj')
    # sel = bpy.context.selected_objects
    # act = bpy.context.active_object

    #厚み付け
    for obj in sel:
        bpy.context.scene.objects.active = obj #sets the obj accessible to bpy.ops
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.05
        #bpy.ops.object.modifier_add(type='SUBSURF')
        #bpy.context.object.modifiers["Subsurf"].levels=0
        #obj.data.materials.clear()

        # bpy.context.scene.objects.active = obj
        # bpy.ops.mesh.uv_texture_add()
        # bpy.ops.object.editmode_toggle()
        # bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)

    sel = bpy.context.selected_objects
    leaf2=sel[:]

    #オブジェクトの回転
    for obj in sel:
        bpy.context.scene.objects.active = obj
        obj.rotation_euler = (0,0,0)
        # bpy.ops.transform.rotate(value=-3.14/2,axis=(-1,0,0))
        # bpy.ops.transform.rotate(value=-3.14/2,axis=(0,-1,0))
        # bpy.ops.transform.rotate(value=-3.14/2,axis=(0,0,-1))
        # bpy.ops.transform.rotate(value=3.14/2,axis=(-1,0,0))
        # bpy.ops.transform.rotate(value=3.14/2,axis=(0,-1,0))
        # bpy.ops.transform.rotate(value=3.14/2,axis=(0,0,-1))
        #bpy.ops.transform.translate(180)

    #質感変更
    for item in bpy.data.materials:
        item.diffuse_shader=('FRESNEL')
        item.diffuse_fresnel=1.0
        item.emit=1.0
        item.specular_intensity=0.0
        item.ambient=0.0
        item.translucency=0.0
        item.use_raytrace=False
        item.use_mist=False
        # シェーディングを切る
        item.use_shadeless = True

    # lamp=bpy.data.objects['Lamp']

    #lamp.data.type='SUN'
    #lamp.location=(0,30,40)

    # アンチエイリアシングを切る
    bpy.data.scenes["Scene"].render.use_antialiasing=False

    #カメラ撮影
    camera.setCirclePathCamera(3, save_dir)

def render2spline(point_xyz, save_dir, obj_num, point_num):
    delete_all()

    #Worldに関する設定
    world = bpy.data.worlds['World'] # 編集する World の取得
    world.horizon_color = (1.0, 1.0, 1.0)
    world.zenith_color = (1.0, 1.0, 1.0)
    world.ambient_color = (0.01, 0.01, 0.01)
    #world.light_settings.use_ambient_occlusion = True # 環境光を使う
    world.light_settings.ao_factor = 1.0 # 環境光の明るさ
    world.light_settings.use_environment_light=True
    world.use_sky_blend=True
    world.light_settings.use_ambient_occlusion=True

    #球オブジェクト作成
    bpy.ops.mesh.primitive_uv_sphere_add()
    uv_sphere_ob = bpy.context.object
    uv_sphere_mat = bpy.data.materials.new('uv_spere_mat')
    obj = bpy.context.scene.objects.active
    # print(obj)
    obj.data.materials.append(uv_sphere_mat)
    # print(type(uv_sphere_ob))
    # print(uv_sphere_ob)
    # print(bpy.data.materials)
    uv_sphere_ob.location = (point_xyz[0], point_xyz[1], point_xyz[2])

    #color変更
    for item in bpy.data.materials:
        item.diffuse_color.hsv=(0.0, 0.0, 0.0)

    #質感変更
    for item in bpy.data.materials:
        item.diffuse_shader=('FRESNEL')
        item.diffuse_fresnel=1.0
        item.emit=1.0
        item.specular_intensity=0.0
        item.ambient=0.0
        item.translucency=0.0
        item.use_raytrace=False
        item.use_mist=False
        # シェーディングを切る
        item.use_shadeless = True

    # アンチエイリアシングを切る
    bpy.data.scenes["Scene"].render.use_antialiasing=False

    #カメラ撮影
    camera.setCirclePathCamera(4, save_dir, obj_num, point_num)

def read_ply(file_path):
    
    _format = ''
    _version = ''
    _comment = ''

    elements = []

    f = open(file_path, 'r')
    line = f.readline()

    # header
    while line:
        if line=='end_header\n':
            break

        fields = line.split()
        if fields[0]=='format':
            _format = fields[1]
            _version = fields[2]
        elif fields[0]=='comment':
            _comment = line[8:]
        elif fields[0]=='element':
            current= {}
            current['name'] = fields[1]
            current['properties'] = []
            current['count'] = int(fields[2])
            elements.append(current)                
        elif fields[0]=='property':
            current['properties'].append(line)

        line = f.readline()

    # elements
    for element in elements:
        element['data'] = []
        for i in range(element['count']):
            line=f.readline()
            element['data'].append(list(map(float, line.split())))

    # print(elements)

    # try:
    # # header
    #     while True:
    #         print(line)
    #         line = f.readline()
    #         if(line=='end_header'):
    #             break
    # except StopIteration:
    #     print("EOF")


    # # elements

    f.close()

    return elements

def getValue(key, items):
    values = [x['data'] for x in items if 'name' in x and 'data' in x and x['name'] == key]
    return values[0] if values else None

def main():
    # root_dir = 'I:/ykato_git/datasets/oomugi_blender/dataset_ver3'
    root_dir = '/home/demo/document/ykato_git/datasets/omg_instance_segmentation/dataset_ver4'
    obj_dir = root_dir + '/obj'
    ply_dir = root_dir + '/ply_render3d'
    img_dir = root_dir + '/img'

    def makeDirectory(path):
        try:
            os.mkdir(path)
        except:
            pass

    # color semantic instance
    for age in range(100, 1100, 100):
        # 保存先ディレクトリの指定と作成
        save_dir = img_dir + '/leaf_age{}'.format(age)
        # save_dir = '../../datasets/omg_instance_segmentation/blender_test'
        makeDirectory(save_dir)

        # 読み込みファイルの指定

        obj_fname = obj_dir + '/all_age{}.obj'.format(age)
        leaf_dname = obj_dir + '/leaf_age{}'
        stem_dname = obj_dir + '/stem_age{}'

        # obj_fname = './all_age1000.obj'

        # render2color(obj_fname, save_dir)
        # render2semantic(obj_fname, save_dir)
        render2instance(leaf_dname, stem_dname, save_dir)

    # spline
    # for age in range(100, 1100, 100):
    #     # オブジェクト数の確認
    #     obj_num = len(os.listdir(ply_dir + '/leaf_age{}'.format(age))) // 4
    #     for on in range(obj_num):
    #         # 保存先ディレクトリの指定と作成
    #         save_dir = img_dir + '/leaf_age{}'.format(age)
    #         makeDirectory(save_dir)

    #         # 読み込みファイルの指定と読み込み
    #         ply_fname = ply_dir + '/leaf_age{}/ControlPoints_{}.ply'.format(age, on)
    #         elements = read_ply(ply_fname)
    #         points_xyz = getValue('vertex', elements)

    #         for pn in range(8):
    #             render2spline(points_xyz[pn], save_dir, on, pn)
    # pass

if __name__=='__main__':
    main()