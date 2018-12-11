#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       VPlants.PlantGL
#
#       Copyright 2011-2011 INRIA - CIRAD - INRA
#
#       File author(s): Christophe Pradal <christophe.pradal@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################


""" `OBJ`_ codec for PlantGL
This module provide a codec for OBJ file format.
`OBJ`_ is a file format for 3D geometry defined by the Wavefront company.
This codec allow to read and write `OBJ`_ file format. 
.. _OBJ: http://en.wikipedia.org/wiki/Wavefront_.obj_file
"""

__license__ = "Cecill-C"
__revision__ = " $Id: obj.py 2242 2010-02-08 17:03:26Z cokelaer $ "

import os
import warnings
from random import randint
from itertools import izip_longest

import openalea.plantgl.math as mt
import openalea.plantgl.scenegraph as sg
import openalea.plantgl.algo as alg
import inspect

# マテリアルカラーをランダムに生成
def random_material(): 
    r, g, b = randint(0,255), randint(0,255), randint(0,255)
    return sg.Material(sg.Color3(r, g, b))

class Group(object):
    def __init__(self, name):
        self.name = name
        self.vindex = []
        self.nindex = []
        self.tindex = []
        self.material = sg.Material()
        self.lvindex = []
        self.lnindex = []
        self.pvindex = []

    def add_face(self, vindex, nindex=None, tindex=None):
        vi = self.vindex 
        vi.append(vindex)
            
        if nindex:
            ni = self.nindex 
            ni.append(nindex)
        if tindex:
            ti = self.tindex 
            ti.append(tindex)

    def add_line(self,  vindex, nindex = None):
        self.lvindex.append(vindex)
        self.lnindex.append(nindex)

    def add_pointset(self,  vindex):
        self.pvindex.append(vindex)

    def shape(self, vertices, normals, textures):
        # Create tset, qset and FaceSet
        # TODO: Add QuadSet
        pointList = vertices
        indexList = self.vindex
        normalList = normals if normals else None
        normalIndexList = self.nindex if self.nindex else None
        textCoordList = sg.Point2Array(textures) if textures else None
        textCoordIndexList = self.tindex if self.tindex else None

        tset = None
        #try:
        if normalIndexList and textCoordIndexList:
            tset = sg.FaceSet(pointList=pointList, indexList=indexList,
            normalList=normalList, normalIndexList=normalIndexList,
            texCoordList=textCoordList, texCoordIndexList=textCoordIndexList)
        elif normalIndexList:
            tset = sg.FaceSet(pointList=pointList, indexList=indexList,
            normalList=normalList, normalIndexList=normalIndexList)
        else:
            tset = sg.FaceSet(pointList=pointList, indexList=indexList)
        #except:
        #    return 
        
        glines = sg.Group([])
        if len(self.lvindex) > 0:
            for line in self.lvindex:
               glines.geometryList.append(sg.Polyline(pointList=[pointList[i] for i in line]))
        
        gpoints = sg.Group([])
        if len(self.pvindex) > 0:
            for points in self.pvindex:
               gpoints.geometryList.append(sg.PointSet(pointList=[pointList[i] for i in points]))
        
        if len(glines) == 0:
            if len(gpoints) == 0:
                geom = tset
            else:
                geom = sg.Group([tset,gpoints])
        elif len(gpoints) == 0:
            if tset is None:
                geom = glines
            else:
                geom = sg.Group([tset,glines]) 
        elif tset is None:
            geom = sg.Group([glines,gpoints])
        else:
            geom = sg.Group([tset,glines,gpoints])

        _shape =  sg.Shape(geom, self.material)
        _shape.name = self.name
        return _shape

    def __len__(self):
        return len(self.vindex) 

class Faces(object):
    def __init__(self, name, offset, mesh, appearancename):
        """ Create a temporary object to ease the writing of OBJ files.
        offset has to be greater than 1.
        """
        self.offset = offset
        self.vindex = mesh.indexList if mesh.ccw else [list(reversed(idx)) for idx in mesh.indexList]
        self.nindex = mesh.normalIndexList if mesh.normalPerVertex and mesh.normalIndexList else []
        self.tindex = mesh.texCoordIndexList if mesh.texCoordIndexList else []
        self.name = name
        self.appearancename = appearancename

    def has_normal(self):
        return bool(self.nindex) 

    def has_texture(self):
        return bool(self.tindex) 

    def obj(self, output):
        """ Write the faces in an obj format. """
        gen = izip_longest(self.vindex, self.tindex,self.nindex, fillvalue=None)
        offset = self.offset
        output.write('g %s \n'%self.name)
        # output.write('usemtl %s \n' % self.appearancename)
        for index, texture, normal in gen:
            s = ' '.join('/'.join((str(index[i]+offset),
                                   str(texture[i]+offset) if texture else '', 
                                   str(normal[i]+offset) if normal else '')).strip('/') for i in range(len(index)))
            line = 'f ' + s + '\n'
            output.write(line)

    def obj1(self, output):
        """ Write the faces in an obj format. """
        gen = izip_longest(self.vindex, self.tindex,self.nindex, fillvalue=None)
        offset = self.offset
        output.write('g %s \n'%self.name)
        output.write('usemtl %s \n' % self.appearancename)
        for index, texture, normal in gen:
            s = ' '.join('/'.join((str(index[i]+offset),
                                   str(texture[i]+offset) if texture else '', 
                                   str(normal[i]+offset) if normal else '')).strip('/') for i in range(len(index)))
            line = 'f ' + s + '\n'
            output.write(line)

    # オブジェクトを１つずつ保存する用（offsetを１にした）
    def obj2(self, output):
        """ Write the faces in an obj format. """
        gen = izip_longest(self.vindex, self.tindex,self.nindex, fillvalue=None)
        # offset = self.offset
        offset = 1
        # print(offset)
        output.write('g %s \n'%self.name)
        for index, texture, normal in gen:
            s = ' '.join('/'.join((str(index[i]+offset),
                                   str(texture[i]+offset) if texture else '', 
                                   str(normal[i]+offset) if normal else '')).strip('/') for i in range(len(index)))
            line = 'f ' + s + '\n'
            output.write(line)
            # print(s)

# objファイル生成クラス
class ObjCodec (sg.SceneCodec):
    """ OBJ File Format 
    The OBJ file format is a simple data-format that represents 3D geometry alone: 
        - the position of each vertex, 
        - the UV position of each texture coordinate vertex, 
        - normals, 
        - the faces that make each polygon defined as a list of vertices, 
        - and texture vertices. 
    File example::
        # List of Vertices, with (x,y,z[,w]) coordinates, w is optional.
        v 0.123 0.234 0.345 1.0
        ...
        
        # Texture coordinates, in (u,v[,w]) coordinates, w is optional.
        vt 0.500 -1.352 [0.234]
        ...
        
        # Normals in (x,y,z) form; normals might not be unit.
        vn 0.707 0.000 0.707
        vn ...
        
        # Face Definitions (see below)
        f 1 2 3
        f 3/1 4/2 5/3
        f 6/4/1 3/5/3 7/6/5
        f ...
    """
    
    def __init__(self):
        """
        Initialisation of the codec info
        """
        sg.SceneCodec.__init__(self,"OBJ",sg.SceneCodec.Mode.ReadWrite)

    def formats(self):
        """ return formats """
        return [ sg.SceneFormat("Obj Codec",["obj"],"The Obj file format") ]


    def read(self,fname):
        """ read an obj file """

        parser = {}
        parser['#'] = parser[''] = self._comment
        parser['v'] = self._vertex
        parser['vt'] = self._vertex_texture
        parser['vn'] = self._vertex_normal
        parser['f'] = self._face
        parser['l'] = self._line
        parser['p'] = self._pointset
        parser['mtllib'] = self._material
        parser['o'] = self._object_name
        parser['g'] = self._group_name
        parser['usemtl'] = self._material_name

        # define data
        self.vertices = []
        self.normals = []
        self.textures= []
        self.groups = [Group('')]
        self.current_group = self.groups[0]
        self.current_material = random_material()
        self.line = 0


        # read the obj file
        with open(fname,"r") as f:
            for l in f:
                l = l.strip()
                fields = l.split()
                if not fields or len(fields)<2:
                    continue
                key = fields[0]
                if key in parser:
                    parser[key](fields[1:])
                else:
                    warnings.warn("Type "+key+" in file '"+fname+"' is not take into account")
                self.line += 1

        # Build the scene
        scene = sg.Scene()
        for g in self.groups:
            if g:
                print 'NAME: ', g.name
                s = g.shape(self.vertices, self.normals, self.textures)
                print 'Shape ', s
                if s and s.geometry: 
                    scene.add(s)


        #scene.add(sg.Shape(sg.PointSet(self.vertices)))

        return scene

    def read_material(self, fname):
        """ Read mtl format, and convert it into PlantGL materials.
        """
        pass

    # Parser functions
    def _comment(self, args):
        pass

    def _vertex(self, args):
        x, y, z = map(float, args)[:3]
        self.vertices.append((x,y,z))

    def _vertex_texture(self, args):
        l = map(float,args)
        self.textures.append(l[:2])

    def _vertex_normal(self, args):
        """ Parse a vertex normal."""
        x, y, z = map(float, args)
        self.normals.append((x,y,z))

    def _face(self, args):
        """ Parse a face set."""
        arg = args[0]
        indices = normals = texts = None
        case = 'vertex' # f v1 v2 v3
        if '//' in arg:
            case ="vertex/normal"
            l = [s.split('//') for s in args]
            indices = tuple(int(v[0]) -1 for v in l)
            normals = tuple(int(v[1])-1 for v in l)
        elif arg.count('/') == 1:
            case ="vertex/texture"
            l = [s.split('/') for s in args]
            indices = tuple(int(v[0]) -1 for v in l)
            texts= tuple(int(v[1])-1 for v in l)
        elif arg.count('/') == 2:
            case ="vertex/texture/normal"
            l = [s.split('/') for s in args]
            indices = tuple(int(v[0]) -1 for v in l)
            texts= tuple(int(v[1])-1 for v in l)
            normals = tuple(int(v[2])-1 for v in l)
        else:
            case = "vertex"
            indices = tuple(int(s)-1 for s in args)

        self.current_group.add_face(vindex=indices, nindex=normals, tindex=texts)

    def _line(self, args):
        """ Parse a line."""
        arg = args[0]
        indices = normals = None
        case = 'vertex' # l v1 v2 v3
        if '//' in arg:
            case ="vertex/normal"
            l = [s.split('//') for s in args]
            indices = tuple(int(v[0]) -1 for v in l)
            normals = tuple(int(v[1])-1 for v in l)
        else:
            case = "vertex"
            indices = tuple(int(s)-1 for s in args)

        self.current_group.add_line(vindex=indices, nindex=normals)

    def _pointset(self, args):
        """ Parse a point set."""
        arg = args[0]
        indices = normals = None
        indices = tuple(int(s)-1 for s in args)

        self.current_group.add_pointset(vindex=indices)

    def _material(self, args):
        # modify the path for local file
        self.read_material(args[0])

    def _object_name(self, args):
        pass

    def _group_name(self, args):
        name = args[0]
        self.current_group = Group(name)
        self.current_group.material = self.current_material
        self.groups.append(self.current_group) 

    def _material_name(self, args):
        name = args[0]
        self.current_material = random_material()
        self.current_material.name = name
        self.current_group.material = self.current_material


    #############################################################################
    #############################################################################
    # PlantGL -> OBJ codec
    def write(self,fname,scene):
        """ Write an OBJ file from a plantGL scene graph.
        This method will convert a PlantGL scene graph into an OBJ file.
        It does not manage  materials correctly yet.
        :Examples:
            import openalea.plantgl.scenegraph as sg
            scene = sg.Scene()"""
        #print("Write "+fname)
        d = alg.Discretizer()
        f = file(fname,'w')
        #print("ss1")
        #print 'write caller name:', inspect.stack()[1][0]
        #print 'caller name:', inspect.stack()[1][1]
        #print 'caller name:', inspect.stack()[1][2]
        #print 'caller name:', inspect.stack()[1][3]
        mtl_file = os.path.splitext(fname)[0]+'.mtl'
        #print astk_interface.__file__
        line = '# File generated by PlantGL - '
        import datetime
        line += datetime.datetime.today().ctime()
        f.write(line+'\n')
        #f.write(line+'\n')
        vertices = [] # List of point List
        normals= [] # List of normal List
        texcoords= [] # List of texture List
        faces = [] # list  of tuple (offset,index List)

        counter = 0
        for i in range(len(scene)):
            #print(i)
            scene[i].name = str(i)

            if scene[i].apply(d):
                p = d.discretization
                pts = p.pointList
                ns = p.normalList
                ts = p.texCoordList
                indices = p.indexList
                n = len(p.pointList)
                if n > 0:
                    vertices.append(pts)
                    if ns:
                        normals.append(ns)
                    if ts:
                        texcoords.append(ts)
                    faces.append(Faces(scene[i].name, counter+1, p, scene[i].appearance.name))
                counter += n

        for pts in vertices:
            for x, y, z in pts:
                f.write('v    %f %f %f\n'%(x, y, z))
            f.write('\n')
        for pts in normals:
            for x, y, z in pts:
                f.write('vn    %f %f %f\n'%(x, y, z))
            f.write('\n')

        for pts in texcoords:
            for x, y in pts:
                f.write('vt    %f %f \n'%(x, y))
            f.write('\n')

        f.write('mtllib %s\n\n'%(os.path.basename(mtl_file)))
        for face in faces:
            face.obj(f)
        f.close()

        fmat = file(mtl_file,'w')
        line = '# File generated by PlantGL'
        normalizedcolor = lambda c : (c.red/255., c.green/255., c.blue/255.)
        outdir = os.path.dirname(fname)
        def tgafname(fname):
            return os.path.splitext(os.path.basename(fname))[0]+'.tga'
        def renameimg(fname):
            outfname = os.path.join(outdir,tgafname(fname))
            try:
                import PIL.Image as Image
                Image.open(fname).save(outfname)
            except ImportError:
                from PyQt4.QtGui import QImage
                img = QImage(fname)
                assert img.save(outfname,'TGA')
            return outfname

        imgstoconvert = set([])
        for sh in scene:
            app = sh.appearance
            if not app.isNamed():
                app.name = 'APP_{}'.format(app.getId())
            if isinstance(app, sg.Material):
                fmat.write("newmtl "+app.name+"\n") 
                fmat.write("\tKa {} {} {}\n".format(*normalizedcolor(app.ambient))) 
                fmat.write("\tKd {} {} {}\n".format(*normalizedcolor(app.diffuseColor()))) 
                fmat.write("\tKs {} {} {}\n".format(*normalizedcolor(app.specular))) 
                fmat.write("\tTr {} \n".format(app.transparency)) 
                fmat.write("\tillum 2\n")
            elif isinstance(app, sg.Texture2D):
                fmat.write("newmtl "+app.name+"\n") 
                fmat.write("\tKa {} {} {}\n".format(*normalizedcolor(app.baseColor))) 
                fmat.write("\tKd {} {} {}\n".format(*normalizedcolor(app.baseColor))) 
                fmat.write("\tKs {} {} {}\n".format(*normalizedcolor(app.baseColor))) 
                fmat.write("\tTr {} \n".format(app.baseColor.alpha/255.))
                imgstoconvert.add(app.image.filename) 
                fmat.write("\tmap_Ka {} \n".format(tgafname(app.image.filename)))
                fmat.write("\tillum 2\n")
        fmat.close()
        print("Write "+mtl_file)

        for img in imgstoconvert:
            tgaimg = renameimg(img)
            print("Write "+tgaimg)
    
    #############################################################################



    #############################################################################
    # PlantGL -> OBJ codec
    # マテリアルファイルを作成する
    def write1(self,fname,scene):
        """ Write an OBJ file from a plantGL scene graph.
        This method will convert a PlantGL scene graph into an OBJ file.
        It does not manage  materials correctly yet.
        :Examples:
            import openalea.plantgl.scenegraph as sg
            scene = sg.Scene()"""
        #print("Write "+fname)
        d = alg.Discretizer()
        f = file(fname,'w')
        #print("ss1")
        #print 'write caller name:', inspect.stack()[1][0]
        #print 'caller name:', inspect.stack()[1][1]
        #print 'caller name:', inspect.stack()[1][2]
        #print 'caller name:', inspect.stack()[1][3]
        mtl_file = os.path.splitext(fname)[0]+'.mtl'
        #print astk_interface.__file__
        line = '# File generated by PlantGL - '
        import datetime
        line += datetime.datetime.today().ctime()
        f.write(line+'\n')
        #f.write(line+'\n')

        # 成分抽出（v, vn, vt, f）
        vertices = [] # List of point List
        normals = [] # List of normal List
        texcoords = [] # List of texture List
        faces = [] # list  of tuple (offset,index List)

        counter = 0
        for i in range(len(scene)):
            #print(i)
            scene[i].name = str(i)

            if scene[i].apply(d):
                p = d.discretization
                pts = p.pointList
                ns = p.normalList
                ts = p.texCoordList
                indices = p.indexList
                n = len(p.pointList)
                if n > 0:
                    vertices.append(pts)
                    if ns:
                        normals.append(ns)
                    if ts:
                        texcoords.append(ts)
                    faces.append(Faces(scene[i].name, counter+1, p, scene[i].appearance.name))
                counter += n

        # .objファイルに書き込み
        ############################
        # os.chdir('/media/sf_share')
        if not os.path.exists("./c/bunkatu/"):
            os.makedirs("./c/bunkatu/")
        fnumber=0
        f1name="./c/bunkatu/stem"+str(fnumber)+".obj"
        #############################################
        
        # v（ジオメトリ座標）書き込み
        for pts in vertices:
            f1=file(f1name,'w')######################
            f1.write(line+'\n')######################
            for x, y, z in pts:
                f1.write('v    %f %f %f\n'%(x, y, z))
            f1.write('\n')
            f1name="./c/bunkatu/stem"+str(fnumber)+".obj"######################
            fnumber+=1######################

        # vn（法線ベクトル）書き込み
        for pts in normals:
            for x, y, z in pts:
                f.write('vn    %f %f %f\n'%(x, y, z))
            f.write('\n')

        # vt（テクスチャ座標）書き込み
        for pts in texcoords:
            for x, y in pts:
                f.write('vt    %f %f \n'%(x, y))
            f.write('\n')

        ######################
        # f1.write('mtllib %s\n\n'%(os.path.basename(mtl_file)))
        for k in range(0,fnumber-1,1):
            f1=file("./c/bunkatu/stem"+str(k)+".obj",'a')
            for face in faces:
                face.obj(f1)
                face.obj(f)
                break
        ######################

        f.close()
        f1.close()######################

        fmat = file(mtl_file,'w')
        line = '# File generated by PlantGL'
        normalizedcolor = lambda c : (c.red/255., c.green/255., c.blue/255.)
        outdir = os.path.dirname(fname)

        # .tgaをファイル名につける
        def tgafname(fname):
            return os.path.splitext(os.path.basename(fname))[0]+'.tga'
        # 画像ファイル名を変更する
        def renameimg(fname):
            outfname = os.path.join(outdir,tgafname(fname))
            try:
                import PIL.Image as Image
                Image.open(fname).save(outfname)
            except ImportError:
                from PyQt4.QtGui import QImage
                img = QImage(fname)
                assert img.save(outfname,'TGA')
            return outfname

        # .mtlファイルに書き込み
        imgstoconvert = set([])
        for sh in scene:
            app = sh.appearance
            if not app.isNamed():
                app.name = 'APP_{}'.format(app.getId())
            if isinstance(app, sg.Material):
                fmat.write("newmtl "+app.name+"\n") 
                fmat.write("\tKa {} {} {}\n".format(*normalizedcolor(app.ambient))) 
                fmat.write("\tKd {} {} {}\n".format(*normalizedcolor(app.diffuseColor()))) 
                fmat.write("\tKs {} {} {}\n".format(*normalizedcolor(app.specular))) 
                fmat.write("\tTr {} \n".format(app.transparency)) 
                fmat.write("\tillum 2\n")
            elif isinstance(app, sg.Texture2D):
                fmat.write("newmtl "+app.name+"\n") 
                fmat.write("\tKa {} {} {}\n".format(*normalizedcolor(app.baseColor))) 
                fmat.write("\tKd {} {} {}\n".format(*normalizedcolor(app.baseColor))) 
                fmat.write("\tKs {} {} {}\n".format(*normalizedcolor(app.baseColor))) 
                fmat.write("\tTr {} \n".format(app.baseColor.alpha/255.))
                imgstoconvert.add(app.image.filename) 
                fmat.write("\tmap_Ka {} \n".format(tgafname(app.image.filename)))
                fmat.write("\tillum 2\n")
        fmat.close()
        print("Write "+mtl_file)

        #　画像ファイル名を.tgaにする
        for img in imgstoconvert:
            tgaimg = renameimg(img)
            print("Write "+tgaimg)
    

    
    #############################################################################


    
    #############################################################################


    def write2(self,save_dir,scene):
        pass
        #初期化
        #成分抽出
        #.objファイル書き込み
        #

        # obj初期化
        d = alg.Discretizer()
        # f = file(fname,'w')
        line = '# File generated by PlantGL - '
        import datetime
        line += datetime.datetime.today().ctime()
        # f.write(line+'\n')

        # 成分抽出
        vertices = [] # List of point List
        normals= [] # List of normal List
        texcoords= [] # List of texture List
        faces = [] # list  of tuple (offset,index List)

        counter = 0
        for i in range(len(scene)):
            #print(i)
            scene[i].name = str(i)

            if scene[i].apply(d):
                p = d.discretization
                pts = p.pointList
                ns = p.normalList
                ts = p.texCoordList
                indices = p.indexList
                n = len(p.pointList)
                if n > 0:
                    vertices.append(pts)
                    if ns:
                        normals.append(ns)
                    if ts:
                        texcoords.append(ts)
                    faces.append(Faces(scene[i].name, counter+1, p, scene[i].appearance.name))
                counter += n

        # objファイル書き込み
        # v（ジオメトリ座標）書き込み
        for i in range(len(vertices)):
            pts = vertices[i]
            fname = save_dir + '/{}.obj'.format(i)
            f = open(fname, 'w')
            f.write(line + '\n')
            for x, y, z in pts:
                f.write('v    %f %f %f\n'%(x, y, z))
            f.write('\n')
            f.close()
        
        # f(face)書き込み
        # print(faces)
        for k in range(len(faces)):
            fname = save_dir + '/{}.obj'.format(k)
            face = faces[k]
            f = open(fname, 'a')
            # print(face)
            # for face in faces:
            #     face.obj(f)
            #     break
            face.obj2(f)
            f.close()

        # print(faces)


if __name__=='__main__':
    codec = ObjCodec()
    sg.SceneFactory.get().registerCodec(codec)