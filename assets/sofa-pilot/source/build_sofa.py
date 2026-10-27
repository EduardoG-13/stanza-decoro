"""Editable parametric upholstery study. Run with Blender 5.2 --background --python.
Coordinates here: X width, -Y front, Z up. glTF exporter maps to X/Y-up/+Z front.
All dimensions and concealed construction are illustrative, not shop drawings.
"""
import bpy, math, json, sys, os
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi, sqrt, exp

ROOT = Path(__file__).resolve().parents[1]
TILE = .14
OUTLINE = [(-1.16,-.39),(-.91,-.56),(-.50,-.57),(-.13,-.47),(.21,-.44),(.60,-.48),(1.02,-.39),(1.23,-.16),(1.24,.12),(1.05,.37),(.73,.47),(.29,.44),(-.18,.43),(-.66,.44),(-1.04,.32),(-1.22,.04)]
BACK = [(-1.05,-.29,.61),(-1.10,-.07,.70),(-1.02,.20,.84),(-.82,.34,.91),(-.46,.37,.92),(-.06,.38,.92),(.32,.38,.91),(.62,.34,.89)]

def catmull(points, t, closed=True):
    n=len(points); total=n if closed else n-1; f=min(t, .999999999)*total; i=int(f); a=f-i
    def at(k): return Vector(points[k%n] if closed else points[max(0,min(n-1,k))])
    p0,p1,p2,p3=[at(k) for k in [i-1,i,i+1,i+2]]
    return .5*((2*p1)+(-p0+p2)*a+(2*p0-5*p1+4*p2-p3)*a*a+(-p0+3*p1-3*p2+p3)*a*a*a)

def mesh(name, verts, faces, parent, mat, uv=None):
    me=bpy.data.meshes.new(name+'_mesh'); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); ob.parent=parent
    me.materials.append(mat)
    for p in me.polygons: p.use_smooth=True
    layer=me.uv_layers.new(name='Fabric_140mm')
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi=me.loops[li].vertex_index
            layer.data[li].uv = uv[vi] if uv else (verts[vi][0]/TILE,verts[vi][2]/TILE)
    # Recalculate outward normals, including cap winding and reversible solids.
    import bmesh
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    ob['asset_id']=name
    return ob

def empty(name,parent=None):
    o=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(o); o.parent=parent; o['asset_id']=name
    return o

def material(name,color,roughness=1):
    m=bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=roughness; bs.inputs['Metallic'].default_value=0
    return m

def srgb(v): return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4

def fabric(name, mobile=False):
    # Base color is pre-tinted in the embedded GLB only. Separate neutral maps permit runtime tints.
    m=material(name,(1,1,1)); nodes=m.node_tree.nodes; links=m.node_tree.links; bs=nodes.get('Principled BSDF')
    folder=ROOT/'materials'/'boucle'
    for kind,socket in [('basecolor','Base Color'),('roughness','Roughness'),('normal','Normal')]:
        ext='png' if kind=='normal' else 'jpg'
        if kind=='basecolor':
            path=ROOT/'source'/'embedded-boucle-areia.jpg'
        elif kind=='roughness': path=ROOT/'source'/'embedded-boucle-roughness.jpg'
        else: path=folder/(kind+'.'+ext)
        if mobile: path=ROOT/'source'/'mobile-boucle'/(kind+'.'+ext)
        im=bpy.data.images.load(str(path),check_existing=False)
        im.colorspace_settings.name='sRGB' if kind=='basecolor' else 'Non-Color'
        tex=nodes.new('ShaderNodeTexImage'); tex.image=im; tex.label=kind+' | 140 mm repeat'; tex.extension='REPEAT'
        if kind=='normal':
            norm=nodes.new('ShaderNodeNormalMap'); norm.inputs['Strength'].default_value=.9
            links.new(tex.outputs['Color'],norm.inputs['Color']); links.new(norm.outputs['Normal'],bs.inputs[socket])
        else: links.new(tex.outputs['Color'],bs.inputs[socket])
        im.pack()
    bs.inputs['Sheen Weight'].default_value=.2; bs.inputs['Sheen Roughness'].default_value=.9
    return m

def seat(name, parent, mat, n=144, foam=False):
    pts=[catmull(OUTLINE,i/n) for i in range(n)]
    # A continuous upholstered bean, with a restrained crown and softened underside.
    profile=[(.88,.086),(.94,.09),(.978,.115),(.997,.165),(1,.24),(1,.31),(.997,.365),(.984,.407),(.963,.437),(.925,.462),(.86,.477),(.74,.485),(.57,.489),(.38,.491),(.19,.492)]
    if foam: profile=[(s*.954,.19+(z-.086)*.68) for s,z in profile]
    vs=[]; uv=[]
    for r,(s,z) in enumerate(profile):
        for i,p in enumerate(pts):
            x,y=p.x*s,p.y*s
            ripple=.0013*sin(i/n*2*pi*17+.8)*sin(pi*r/(len(profile)-1))
            # Very shallow compression under the loose cushions, no inflated central dome.
            depression=.009*exp(-((x+.48)/.75)**2-((y-.17)/.27)**2) if z>.4 else 0
            vs.append((x,y,z+ripple-depression))
            uv.append((x/TILE,y/TILE) if r>=8 else (i/n*6.28*.80/TILE,z/TILE))
    fs=[]
    for r in range(len(profile)-1):
        for i in range(n): fs.append((r*n+i,r*n+(i+1)%n,(r+1)*n+(i+1)%n,(r+1)*n+i))
    bot=len(vs);vs.append((0,0,profile[0][1]));uv.append((0,0))
    top=len(vs);vs.append((0,0,profile[-1][1]));uv.append((0,0))
    for i in range(n):
        fs.append((bot,(i+1)%n,i));fs.append((top,(len(profile)-1)*n+i,(len(profile)-1)*n+(i+1)%n))
    ob=mesh(name,vs,fs,parent,mat,uv)
    # Correct the U seam of each side polygon without splitting the smooth geometry.
    layer=ob.data.uv_layers.active
    for p in ob.data.polygons:
        vals=[layer.data[k].uv.x for k in p.loop_indices]
        if p.index < 8*n and max(vals)-min(vals)>20:
            for k in p.loop_indices:
                if layer.data[k].uv.x<1:layer.data[k].uv.x=6.28*.8/TILE
    return ob

def back(name,parent,mat,n=104,m=32,foam=False):
    vs=[];uv=[];fs=[];length=0;prev=None
    for i in range(n+1):
        t=i/n; p=catmull(BACK,t,False); prevp=catmull(BACK,max(0,t-.001),False); nextp=catmull(BACK,min(1,t+.001),False)
        tangent=(nextp-prevp); tangent.z=0;tangent.normalize(); norm=Vector((-tangent.y,tangent.x,0))
        if prev is not None:length+=(p-prev).length
        prev=p.copy()
        edge=min(t/.055,(1-t)/.055,1); cap=sqrt(max(.0002,1-(1-edge)**2))
        low=.315; high=p.z; center=(high+low)/2; hh=(high-low)/2
        thick=.122*(.94+.06*sin(t*pi))
        if foam:thick*=.78;hh*=.86
        for j in range(m):
            a=2*pi*j/m
            c=math.copysign(abs(cos(a))**.48,cos(a)); s=math.copysign(abs(sin(a))**.48,sin(a))
            v=p+norm*(thick*c*cap);v.z=center+hh*s*cap
            v.z+=.0012*sin(t*37)*sin(a)**2
            vs.append(tuple(v));uv.append((length/TILE,(j/m*(2*(2*hh+2*thick)))/TILE))
    for i in range(n):
        for j in range(m):fs.append((i*m+j,i*m+(j+1)%m,(i+1)*m+(j+1)%m,(i+1)*m+j))
    for end in (0,n):
        ring=vs[end*m:(end+1)*m];idx=len(vs);vs.append(tuple(sum(v[k] for v in ring)/m for k in range(3)));uv.append((0,0))
        for j in range(m):fs.append((idx,end*m+j,end*m+(j+1)%m))
    ob=mesh(name,vs,fs,parent,mat,uv)
    # Smooth topology keeps the flowing arm/back outline editable as a quad loft.
    for p in ob.data.polygons:
        us=[ob.data.uv_layers.active.data[k].uv.y for k in p.loop_indices]
        if max(us)-min(us)>3:
            for k in p.loop_indices:
                if ob.data.uv_layers.active.data[k].uv.y<.01: ob.data.uv_layers.active.data[k].uv.y=max(us)*m/(m-1)
    return ob

def tube(name,pts,radius,parent,mat,sides=5,closed=True):
    vs=[];uv=[];fs=[];length=0
    for i,p in enumerate(pts):
        p=Vector(p)
        if i:length+=(p-Vector(pts[i-1])).length
        tangent=(Vector(pts[(i+1)%len(pts)])-Vector(pts[(i-1)%len(pts)])).normalized()
        normal=tangent.cross(Vector((0,0,1)))
        if normal.length<.01:normal=tangent.cross(Vector((0,1,0)))
        normal.normalize();b=tangent.cross(normal).normalized()
        for j in range(sides):
            a=2*pi*j/sides;v=p+radius*(normal*cos(a)+b*sin(a));vs.append(tuple(v));uv.append((length/TILE,j/sides*.01/TILE))
    for i in range(len(pts) if closed else len(pts)-1):
        for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,((i+1)%len(pts))*sides+(j+1)%sides,((i+1)%len(pts))*sides+j))
    return mesh(name,vs,fs,parent,mat,uv)

def pillow(name,parent,mat,seam,n,pos,rot,size,seed):
    vs=[];uv=[];fs=[];a,b=size
    for side in (-1,1):
        for j in range(n+1):
            v=j/n*2-1
            for i in range(n+1):
                u=i/n*2-1
                # Knife-edge cushions: tapered seams, soft broad fill, small inward edge gathers.
                x=a*u*(1+.045*(1-v*v));z=b*v*(1+.025*(1-u*u))
                belly=max(0,(1-u*u)*(1-v*v))**.55
                edge=min(1-abs(u),1-abs(v))
                gathers=.0055*sin(34*u+9*v+seed)*exp(-edge*9)*sin(pi*max(0,edge)/.28)
                d=.008+.112*belly+gathers
                vs.append((x,side*d,z));uv.append((x/TILE,z/TILE))
    block=(n+1)**2
    for s in range(2):
        for j in range(n):
            for i in range(n):
                k=s*block+j*(n+1)+i;fs.append((k,k+1,k+n+2,k+n+1))
    perimeter=list(range(n+1))+[j*(n+1)+n for j in range(1,n+1)]+[n*(n+1)+i for i in range(n-1,-1,-1)]+[j*(n+1) for j in range(n-1,0,-1)]
    for i,k in enumerate(perimeter):k2=perimeter[(i+1)%len(perimeter)];fs.append((k,k2,k2+block,k+block))
    holder=empty(name,parent);holder.location=pos;holder.rotation_euler=tuple(math.radians(r) for r in rot)
    ob=mesh(name+'_cover',vs,fs,holder,mat,uv)
    line=[(vs[k][0],0,vs[k][2]) for k in perimeter]
    tube(name+'_welt',line,.0015,holder,seam,sides=4)
    return ob

def box(name,location,scale,parent,mat,bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=parent;o.data.materials.append(mat);o['asset_id']=name
    mod=o.modifiers.new('Small edge radius','BEVEL');mod.width=bevel;mod.segments=2
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in o.data.polygons:p.use_smooth=False
    return o

def build(mobile=False):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.materials):bpy.data.materials.remove(m)
    root=empty('sofa_root');root['modelId']='stanza-organic-01';root['revision']='1.0.0';root['dimensions_estimated']=True;root['construction']='illustrative'
    groups={name:empty(name,root) for name in ['upholstery','padding','frame','legs','cushions','suspension']}
    cloth=fabric('fabric_main',mobile); seam=cloth.copy();seam.name='fabric_seam'
    foam=material('padding_illustrative',(.72,.62,.43),.97)
    frame=material('frame_illustrative',(.21,.13,.075),.84)
    feet=material('legs_dark',(.026,.025,.022),.5)
    belt=material('suspension_illustrative',(.10,.083,.067),.95)
    seatob=seat('seat_cover',groups['upholstery'],cloth,n=80 if mobile else 144)
    backob=back('back_cover',groups['upholstery'],cloth,n=52 if mobile else 96,m=20 if mobile else 32)
    # Real thin shell thickness on the upholstery, not overlapping foam surfaces.
    for ob in [seatob,backob]:
        mod=ob.modifiers.new('Cloth thickness 1.5 mm','SOLIDIFY');mod.thickness=.0015;mod.offset=-1
    pts=[]
    for i in range(100 if mobile else 160):
        t=i/(100 if mobile else 160);p=catmull(OUTLINE,t)
        x,y=p.x*.9655,p.y*.9655
        ripple=.0013*sin(t*2*pi*17+.8)*sin(pi*8/14)
        depression=.009*exp(-((x+.48)/.75)**2-((y-.17)/.27)**2)
        pts.append((x,y,.4385+ripple-depression))
    tube('seat_panel_seam',pts,.0011,groups['upholstery'],seam,sides=5 if not mobile else 4)
    seat('seat_padding',groups['padding'],foam,n=64 if mobile else 96,foam=True)
    back('back_padding',groups['padding'],foam,n=40 if mobile else 64,m=16 if mobile else 20,foam=True)
    framepts=[]
    for i in range(64 if mobile else 96):
        p=catmull(OUTLINE,i/(64 if mobile else 96));framepts.append((p.x*.80,p.y*.72,.19))
    tube('perimeter_support',framepts,.043,groups['frame'],frame,sides=4)
    for k,x in enumerate([-.82,-.38,.08,.54,.91]):
        box('cross_support_'+str(k),(x,0,.19),(.043,.58,.075),groups['frame'],frame)
    box('rear_support',(-.2,.28,.38),(1.60,.06,.12),groups['frame'],frame)
    for k,x in enumerate([-.88,-.62,-.36,-.1,.16,.42,.68,.9]):
        box('suspension_band_'+str(k),(x,0,.24),(.055,.61,.004),groups['suspension'],belt,.001)
    for k,(x,y) in enumerate([(-.94,-.24),(.98,-.15),(-.84,.29),(.82,.27)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16 if mobile else 32,radius=.052,depth=.105,location=(x,y,.0525));ob=bpy.context.object;ob.name='foot_'+str(k+1);ob.parent=groups['legs'];ob.data.materials.append(feet)
        bevel=ob.modifiers.new('Foot softened edge','BEVEL');bevel.width=.009;bevel.segments=2;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=bevel.name)
        for p in ob.data.polygons:p.use_smooth=True
    pillows=[
      ('cushion_01',(-.88,-.105,.65),(-12,-17,-6),(.195,.235)),
      ('cushion_02',(-.57,-.185,.652),(-18,14,4),(.195,.245)),
      ('cushion_03',(-.225,-.09,.703),(-15,-11,-4),(.218,.275)),
      ('cushion_04',(.13,-.105,.663),(-17,-17,4),(.185,.235)),
      ('cushion_05',(.44,-.23,.625),(-22,-28,-10),(.18,.195))]
    for k,(name,pos,rot,sz) in enumerate(pillows):pillow(name,groups['cushions'],cloth,seam,12 if mobile else 20,pos,rot,sz,k)
    bpy.context.view_layer.update()
    points=[o.matrix_world @ Vector(c) for o in bpy.context.scene.objects if o.type=='MESH' for c in o.bound_box]
    cx=(min(p.x for p in points)+max(p.x for p in points))/2
    cy=(min(p.y for p in points)+max(p.y for p in points))/2
    for group in groups.values(): group.location.x=-cx;group.location.y=-cy
    bpy.context.view_layer.update()
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    bpy.context.scene['orientation']='Blender -Y front; exported glTF +Z front, Y up'
    bpy.context.scene['reference']='SOFA-2.jpg; Sofá Orgânico em Design Feijão; single photographed angle'
    bpy.context.scene['estimated_dimensions']=True
    bpy.ops.object.select_all(action='SELECT')
    dest=ROOT/'models'/('sofa-mobile.glb' if mobile else 'sofa.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True,export_cameras=False,export_lights=False,export_image_format='AUTO')
    if not mobile:
        for a in bpy.context.screen.areas:
            if a.type=='VIEW_3D':
                a.spaces.active.region_3d.view_distance=4.2;a.spaces.active.region_3d.view_location=Vector((0,0,.45))
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/'sofa.blend'),compress=True)
    print('EXPORTED',dest)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if '--mobile-only' not in args:build(False)
    build(True)
