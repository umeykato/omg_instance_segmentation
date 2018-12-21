import bpy
import os

def setCirclePathCamera(j, save_dir, obj_num=0, point_num=0):
# def setCirclePathCamera(j, num):
    clip_end = 999999

    #Blenderのデータベースとシーングラフについて以下参照
    #https://dskjal.com/blender/database-and-scene-graph.html

    #この流れで作成
    #https://qiita.com/jp_ibis/items/6d7dc4f6422325191e57

    # print(bpy.data.objects['BezierCircle'] in list(bpy.data.objects))
    # if bpy.data.objects['BezierCircle'] in list(bpy.data.objects):
    #     bpy.data.objects.remove(bpy.data.objects['BezierCircle'])


    #カメラオブジェクト作成
    cam = bpy.data.cameras.new("Cam")             #空のカメラをデータベースに追加
    cam.clip_end = clip_end                       #よくわかんない
    cam_ob = bpy.data.objects.new("Cam", cam)     #カメラを指定してオブジェクトを追加
    bpy.context.scene.objects.link(cam_ob)        #コンテクストを使って現在のシーンから参照

    #円オブジェクト作成
    bpy.ops.curve.primitive_bezier_circle_add()
    circle_ob = bpy.context.object

    #空オブジェクト作成
    empty_ob = bpy.data.objects.new("empty", None)
    bpy.context.scene.objects.link(empty_ob)
    bpy.context.scene.update()

    #撮影フレーム数設定
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 99

    #円とカメラを連結
    bpy.context.scene.objects.active = bpy.data.objects["Cam"]
    bpy.ops.object.constraint_add(type='FOLLOW_PATH')
    bpy.context.object.constraints["Follow Path"].target = bpy.data.objects['BezierCircle']
    bpy.context.object.constraints["Follow Path"].use_curve_follow = True
    bpy.context.object.constraints["Follow Path"].forward_axis = 'FORWARD_Y'
    bpy.context.object.constraints["Follow Path"].up_axis = 'UP_Z'
    override={'constraint':bpy.context.object.constraints["Follow Path"]}
    bpy.ops.constraint.followpath_path_animate(override, constraint='Follow Path')

    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.object.constraints["Track To"].target = bpy.data.objects['empty']
    bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'

    #円の回転とカメラ向きの初期化（大麦自体が回転しているため，それに合わせた）
    #
    #     いじってはダメ！ぜったい！！！！！！！！！！
    #
    # cam_ob.rotation_euler[0] = 1.5708
    # cam_ob.rotation_euler[2] = -1.5708

    # circle_ob.scale *= 40
    # circle_ob.rotation_euler.x += 3.14 / 2
    # circle_ob.location = (0, -15, 0)

    empty_ob.location = (0, 0, 20)

    #円の位置設定
    # circle_ob.scale *= 1                #円の大きさを変更し，オブジェクトとの距離を調整
    # circle_ob.scale *= 0.9
    # circle_ob.scale *= 0.5
    # circle_ob.location = (0, -15, 0)    #円の位置を変更し，撮影位置を調整
    # circle_ob.location = (0, -40, 0)
    # circle_ob.location = (0, -60, 0)

    #カメラ角度設定
    # cam_ob.rotation_euler[0] = 1.5708   #カメラ向きの上下を調整
    # cam_ob.rotation_euler[0] = 1.0   
    # cam_ob.rotation_euler[0] = 0.5  
    
    #撮影画質設定(１あたり０．５ピクセル)
    bpy.context.scene.render.resolution_x = 1000    # 500pixel
    bpy.context.scene.render.resolution_y = 1000    # 500pixel
    
    #撮影開始
    cs = [50, 50, 50, 50, 50]
    cl = [0, 20, 40, 60, 80]
    # save_dir = root_path + '/img'
    # try:
    #     os.mkdir(save_dir + '/adel{}nsect1'.format(num))
    # except:
    #     pass
    def makeDirectory(path):
        try:
            os.mkdir(path)
        except:
            pass

    for i in range(5):
        circle_ob.scale = (cs[i], cs[i], cs[i])
        circle_ob.location = (0, 0, cl[i])
        if j==1:
            save_dir2 = save_dir + '/image_location{}/'.format(i)
            makeDirectory(save_dir2)
            bpy.data.scenes['Scene'].render.filepath = (save_dir2)
            # bpy.data.scenes['Scene'].render.filepath = (root_path + 'adel{}nsect1/o/'.format(num)+str(i)+'/')
        elif j==2:
            save_dir2 = save_dir + '/semantic_location{}/'.format(i)
            makeDirectory(save_dir2)
            bpy.data.scenes['Scene'].render.filepath = (save_dir2)
            # bpy.data.scenes['Scene'].render.filepath = (root_path + 'adel{}nsect1/f/'.format(num) + str(i) + '/')
        elif j==3:
            save_dir2 = save_dir + '/instance_location{}/'.format(i)
            makeDirectory(save_dir2)
            bpy.data.scenes['Scene'].render.filepath = (save_dir2)
            # bpy.data.scenes['Scene'].render.filepath = (root_path + 'adel{}nsect1/s/'.format(num) + str(i) + '/')
        elif j==4:
            save_dir2 = save_dir + '/spline_location{}object{}point{}/'.format(i, obj_num, point_num)
            makeDirectory(save_dir2)
            bpy.data.scenes['Scene'].render.filepath = (save_dir2)
            # bpy.data.scenes['Scene'].render.filepath = (root_path + 'adel{}nsect1/s/'.format(num) + str(i) + '/')
        else:
            # bpy.data.scenes['Scene'].render.filepath = (root_path + './tmp/'+str(i)+'/')
            pass
        bpy.context.scene.camera=bpy.data.objects['Cam']
        bpy.ops.render.render(animation=True)



# def setCirclePathCamera(j):
#     clip_end = 999999

#     #カメラ作成
#     cam = bpy.data.cameras.new("Cam")
#     cam.clip_end = clip_end
#     cam_ob = bpy.data.objects.new("Cam", cam)
#     #cam_ob.location=(0,-10,1)
#     bpy.context.scene.objects.link(cam_ob)


#     camOrgPos = bpy.data.objects.new("camOrgPos", None)
#     bpy.context.scene.objects.link(camOrgPos)
#     bpy.context.scene.update()


#     bpy.ops.curve.primitive_bezier_circle_add()
#     circle = bpy.context.object
#     #円のサイズ
#     circle.scale *= 40
#     circle.rotation_euler[0] = 3.14 / 2
#     #bpy.context.scene.objects.active = circle
#     #circle.location=(0,0,1)
#     #bpy.ops.transform.rotate(value=-3.14 / 2, axis=(-1, 0, 0))
#     #カメラの位置
#     co = circle.data.splines[0].bezier_points[-1].co * 10
#     cam_ob.location = co
#     # cam_ob.location=(0,-100,1)
#     cam_ob.location=(0,-50,1)
#     #co=bpy.data.cameras
#     #bpy.data.cameras["Cam"].shift_x=100

#     cam_ob.rotation_euler[0] = 3.14 / 2

#     cam_ob.select = True
#     bpy.ops.object.parent_set(type='FOLLOW')

#     bpy.context.scene.frame_start=0
#     bpy.context.scene.frame_end=100
#     # bpy.context.scene.frame_end=1
#     con = cam_ob.constraints.new('TRACK_TO')
#     con.target = camOrgPos
#     con.track_axis = 'TRACK_NEGATIVE_Z'
#     con.up_axis = 'UP_X'
#     #bpy.ops.scree.animation_play()
#     # bpy.context.scene.render.resolution_x = 6000
#     # bpy.context.scene.render.resolution_y = 6000
#     bpy.context.scene.render.resolution_x = 1000
#     bpy.context.scene.render.resolution_y = 1000
#     #bpy.context.scene.render.resolution_percentage=100 #解像度
#     for i in range(20,30,10):
#         # cam_ob.location = (0, -45, i)
#         # camOrgPos.location=(0,0,i-3)
#         cam_ob.location = (50, -20, 0)
#         camOrgPos.location=(0,-20,0)
#         if j==1:
#             bpy.data.scenes['Scene'].render.filepath=('./o/'+str(i)+'/')
#         elif j==2:
#             bpy.data.scenes['Scene'].render.filepath = ('./f/' + str(i) + '/')
#         elif j==3:
#             bpy.data.scenes['Scene'].render.filepath = ('./s/' + str(i) + '/')
#         elif j==4:
#             bpy.data.scenes['Scene'].render.filepath = ('./obj/' + str(i) + '/')
#         elif j==8:
#             bpy.data.scenes['Scene'].render.filepath = ('./end8/' + str(i) + '/')
#         elif j==9:
#             bpy.data.scenes['Scene'].render.filepath = ('./end9/' + str(i) + '/')
#         elif j==10:
#             bpy.data.scenes['Scene'].render.filepath = ('./end10/' + str(i) + '/')
#         elif j==11:
#             bpy.data.scenes['Scene'].render.filepath = ('./end11/' + str(i) + '/')
#         else:
#             bpy.data.scenes['Scene'].render.filepath=('./tmp/'+str(i)+'/')
#         bpy.context.scene.camera=bpy.data.objects['Cam']
#         bpy.ops.render.render(animation=True)


#     for area in bpy.context.screen.areas:
#         if area.type == 'VIEW_3D':
#             area.spaces[0].clip_end = clip_end


if __name__=='__main__':
    # setCirclePathCamera()
    pass