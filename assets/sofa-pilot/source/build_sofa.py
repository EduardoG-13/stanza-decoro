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
# Loose seat cushions. pos/rot/size keep the photographed composition (three light + two
# olive-weave) and asymmetry; neighbours are nudged slightly apart along X to relieve the
# confirmed mesh interpenetration (01-02..04-05) without large vertical moves that would
# flatten the silhouette. `flatten` adds the soft contact compression on each cushion's
# underside (FEAT-002) so the thin contact band with the seat reads as foam, not clipping.
CUSHIONS = [
  ('cushion_01',(-.912,-.11,.648),(-12,-17,-6),(.193,.235),.70),
  ('cushion_02',(-.582,-.188,.651),(-18,14,4),(.191,.245),.68),
  ('cushion_03',(-.235,-.092,.702),(-15,-11,-4),(.214,.275),.66),
  ('cushion_04',(.152,-.108,.662),(-17,-17,4),(.181,.235),.68),
  ('cushion_05',(.462,-.233,.623),(-22,-28,-10),(.178,.195),.70)]

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

def seat(name, parent, mat, n=144, foam=False, batting=False):
    pts=[catmull(OUTLINE,i/n) for i in range(n)]
    # A continuous upholstered bean, with a restrained crown and softened underside.
    profile=[(.88,.086),(.94,.09),(.978,.115),(.997,.165),(1,.24),(1,.31),(.997,.365),(.984,.407),(.963,.437),(.925,.462),(.86,.477),(.74,.485),(.57,.489),(.38,.491),(.19,.492)]
    # FEAT-003: the seat FOAM is its own coherent block (a firm, lower cushion core that
    # sits inside the upholstery), not the outer shell merely rescaled. It is shorter,
    # flatter-crowned and inset from the cover so the batting can wrap it. The BATTING is a
    # thin poly wrap just outside the foam (Sailrite "Anatomy of a Cushion"/"Gluing Batting
    # to Foam"): ~12 mm of soft loft that rounds the foam edges and fills the gap to the
    # cover. batting -> slightly larger & taller than foam but still well inside the cover.
    if foam: profile=[(s*.93,.168+(z-.086)*.58) for s,z in profile]
    if batting: profile=[(s*.945,.172+(z-.086)*.60) for s,z in profile]
    vs=[]; uv=[]
    for r,(s,z) in enumerate(profile):
        for i,p in enumerate(pts):
            x,y=p.x*s,p.y*s
            ripple=.0013*sin(i/n*2*pi*17+.8)*sin(pi*r/(len(profile)-1))
            # Soft foam dimple under each loose cushion so its underside is cradled by the
            # seat crown (FEAT-002) instead of the cushion belly clipping through a flat top.
            # A shallow Gaussian per cushion footprint; crest stays restrained, no central dome.
            depression=0
            if z>.4:
                for _cn,_cp,_cr,_cs,_cf in CUSHIONS:
                    depression+=.019*exp(-((x-_cp[0])/(_cs[0]+.11))**2-((y-_cp[1])/(_cs[1]+.10))**2)
                depression=min(depression,.026)
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

def back(name,parent,mat,n=104,m=32,foam=False,batting=False):
    vs=[];uv=[];fs=[];length=0;prev=None
    for i in range(n+1):
        t=i/n; p=catmull(BACK,t,False); prevp=catmull(BACK,max(0,t-.001),False); nextp=catmull(BACK,min(1,t+.001),False)
        tangent=(nextp-prevp); tangent.z=0;tangent.normalize(); norm=Vector((-tangent.y,tangent.x,0))
        if prev is not None:length+=(p-prev).length
        prev=p.copy()
        edge=min(t/.055,(1-t)/.055,1); cap=sqrt(max(.0002,1-(1-edge)**2))
        low=.315; high=p.z; center=(high+low)/2; hh=(high-low)/2
        thick=.122*(.94+.06*sin(t*pi))
        # FEAT-003: foam core is the firmest/innermost back volume; batting is a thin loft
        # just outside it. Both stay inside the upholstery shell (which is unscaled here).
        if foam:thick*=.70;hh*=.80
        elif batting:thick*=.80;hh*=.86
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

def pillow(name,parent,mat,seam,n,pos,rot,size,seed,flatten=0):
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
                # Soft contact compression (FEAT-002): the underside (side=+1 rests on the
                # seat) develops a broad flattened patch, as foam does under load, instead of a
                # round belly poking through the seat shell. The tapered knife edge is kept.
                if side>0 and flatten:
                    contact=max(0,(1-(u/.9)**2)*(1-(v/.9)**2))**.75
                    d-=flatten*contact*(.112*belly)
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

def strap(name,a,b,parent,mat,width=.05,thick=.004,sag=.012,segs=12,over=False):
    # FEAT-003: one elasticized webbing strap tensioned between two frame anchors a->b.
    # Modelled as a thin flat band with a shallow catenary-like sag at mid-span (loaded
    # webbing dips slightly) and a small lift at the crossing when it rides OVER a
    # perpendicular strap (`over`). Grounded in Simplicity Sofas: webbing is firmly fixed to
    # the frame; thicker bands and some interlacing read as quality. Not a universal
    # criss-cross: only the widest central spans interlace (see build()).
    a=Vector(a); b=Vector(b)
    axis=(b-a); L=axis.length; axis=axis.normalized()
    side=Vector((-axis.y,axis.x,0))
    if side.length<1e-6: side=Vector((1,0,0))
    side=side.normalized()
    vs=[];uv=[];fs=[]
    rings=segs+1
    for s in range(rings):
        t=s/segs; c=a.lerp(b,t)
        dip=sag*(1-(2*t-1)**2)          # mid-span sag
        lift=(.006 if over else 0)*(1-(2*t-1)**2)  # ride-over bump at the crossing
        z=c.z-dip+lift
        for w in (-1,1):
            p=c+side*(width/2*w)
            vs.append((p.x,p.y,z+thick/2)); uv.append((t*L/TILE,(w+1)/2*width/TILE))
        for w in (-1,1):
            p=c+side*(width/2*w)
            vs.append((p.x,p.y,z-thick/2)); uv.append((t*L/TILE,(w+1)/2*width/TILE))
    # 4 longitudinal faces (top, bottom, two sides) per segment
    for s in range(segs):
        o=s*4; n=o+4
        fs.append((o+0,o+1,n+1,n+0))   # top
        fs.append((o+2,o+3,n+3,n+2))   # bottom
        fs.append((o+0,o+2,n+2,n+0))   # side -
        fs.append((o+1,o+3,n+3,n+1))   # side +
    # end caps
    fs.append((0,1,3,2)); last=segs*4; fs.append((last+0,last+2,last+3,last+1))
    return mesh(name,vs,fs,parent,mat,uv)

def box(name,location,scale,parent,mat,bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=parent;o.data.materials.append(mat);o['asset_id']=name
    mod=o.modifiers.new('Small edge radius','BEVEL');mod.width=bevel;mod.segments=2
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in o.data.polygons:p.use_smooth=False
    return o

def build(mobile=False):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.materials):bpy.data.materials.remove(m)
    root=empty('sofa_root');root['modelId']='stanza-organic-01';root['revision']='1.2.0';root['dimensions_estimated']=True;root['construction']='illustrative'
    groups={name:empty(name,root) for name in ['upholstery','padding','frame','legs','cushions','suspension']}
    cloth=fabric('fabric_main',mobile); seam=cloth.copy();seam.name='fabric_seam'
    foam=material('padding_illustrative',(.72,.62,.43),.97)
    # FEAT-003: batting (manta de poliéster) is a NEW, visually distinct sub-material inside
    # the padding group: lighter, slightly warmer-white and softer than the foam core, so
    # the thin wrap reads as the loft layer, not as a second foam shell.
    batt=material('batting_illustrative',(.90,.88,.83),.99)
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
        depression=min(sum(.019*exp(-((x-cp[0])/(cs[0]+.11))**2-((y-cp[1])/(cs[1]+.10))**2) for _cn,cp,_cr,cs,_cf in CUSHIONS),.026)
        pts.append((x,y,.4385+ripple-depression))
    tube('seat_panel_seam',pts,.0011,groups['upholstery'],seam,sides=5 if not mobile else 4)
    # FEAT-003 padding by components: a firm FOAM core plus a thin BATTING loft wrapping it.
    # The batting is a genuinely distinct object/material (not the foam shell rescaled):
    # slightly larger and taller than the foam but inset from the cover, so when the layers
    # are separated the manta reads as a thin soft wrap over the foam block.
    seat('seat_foam',groups['padding'],foam,n=64 if mobile else 96,foam=True)
    seat('seat_batting',groups['padding'],batt,n=48 if mobile else 80,batting=True)
    back('back_foam',groups['padding'],foam,n=40 if mobile else 64,m=16 if mobile else 20,foam=True)
    back('back_batting',groups['padding'],batt,n=36 if mobile else 56,m=14 if mobile else 18,batting=True)
    # FEAT-003 frame: a solid-wood perimeter rail following the bean contour (Simplicity
    # Sofas / Beaumont & Fletcher: corner-blocked, doweled, screwed-and-glued hardwood frame
    # of which the feet are part). The perimeter hugs ~82% of the silhouette so it reads as
    # the load rail that the webbing and feet attach to. FR_S scales the contour for the rail.
    FR_S=.86
    framepts=[]
    for i in range(64 if mobile else 96):
        p=catmull(OUTLINE,i/(64 if mobile else 96));framepts.append((p.x*FR_S,p.y*(FR_S-.06),.19))
    tube('perimeter_support',framepts,.043,groups['frame'],frame,sides=4)
    # Front and rear seat rails that the webbing is tensioned between, plus lateral tie rails
    # at the ends; these run with the contour so no bar is left functionless when exposed.
    FRONT_Y=-.50; REAR_Y=.46
    STRAP_X=[-.86,-.58,-.30,-.02,.26,.54,.84]   # anchor columns across the width
    def contour_y(x,base):                       # keep rails inside the contour at a given x
        return base*(1-.12*(x/1.2)**2)
    box('front_rail',(0,contour_y(0,FRONT_Y),.205),(1.98,.05,.07),groups['frame'],frame)
    box('rear_rail',(-.1,REAR_Y,.205),(1.9,.05,.07),groups['frame'],frame)
    for k,x in enumerate([-.9,.92]):
        box('side_rail_'+str(k),(x,-.02,.205),(.05,.86,.07),groups['frame'],frame)
    # Two cross braces under the widest span keep the perimeter from racking (corner-block idea).
    for k,x in enumerate([-.4,.42]):
        box('cross_support_'+str(k),(x,0,.17),(.05,.80,.06),groups['frame'],frame)
    box('rear_support',(-.1,.30,.37),(1.58,.06,.11),groups['frame'],frame)
    # FEAT-003 webbing: individual elasticized straps tensioned FRONT->REAR across the seat
    # (the primary span the body loads), each anchored to the front and rear wood rails. A
    # partial interlace is justified, NOT a universal criss-cross: only the three widest
    # central spans get two lateral straps woven over/under them for the quality cue the
    # references describe; the outer/short spans stay single-direction, as a real maker would
    # not waste webbing where the span is short. Straps sit just above the rails (z~.225).
    WZ=.225; sb=0
    anchors={}
    for k,x in enumerate(STRAP_X):
        fa=(x,contour_y(x,FRONT_Y)-.01,WZ); ra=(x,contour_y(x,REAR_Y)+.01,WZ)
        anchors[k]=(fa,ra)
        # central columns (2,3,4) are interlaced -> their longitudinal straps ride a touch low
        central = k in (2,3,4)
        strap('suspension_band_'+str(sb),fa,ra,groups['suspension'],belt,
              width=.052,thick=.004,sag=.016 if central else .012,over=False); sb+=1
    # Lateral interlacing straps only across the three central longitudinal straps.
    for k,y in enumerate([-.22,.0,.22]):
        la=(STRAP_X[1]+.02,contour_y(STRAP_X[1],y),WZ); lb=(STRAP_X[5]-.02,contour_y(STRAP_X[5],y),WZ)
        strap('suspension_band_'+str(sb),la,lb,groups['suspension'],belt,
              width=.05,thick=.004,sag=.012,over=True); sb+=1
    # FEAT-003 feet: four turned feet that REST on the floor (bottom at z=0) and read as
    # part of the base. The cylinder is a touch taller so its top meets the perimeter rail
    # underside (~.147); a short mount block bridges foot-top to the wood rail so the foot is
    # visibly attached to the frame (Beaumont & Fletcher: the feet are part of the frame),
    # not floating under it. Feet keep their own dark finish (legs_dark).
    FOOT_H=.15
    for k,(x,y) in enumerate([(-.90,-.26),(.92,-.17),(-.80,.30),(.80,.28)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16 if mobile else 32,radius=.05,depth=FOOT_H,location=(x,y,FOOT_H/2));ob=bpy.context.object;ob.name='foot_'+str(k+1);ob.parent=groups['legs'];ob.data.materials.append(feet)
        bevel=ob.modifiers.new('Foot softened edge','BEVEL');bevel.width=.009;bevel.segments=2;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=bevel.name)
        for p in ob.data.polygons:p.use_smooth=True
        # Mount block tying the foot top to the frame rail so the connection reads coherently.
        box('foot_mount_'+str(k+1),(x,y,FOOT_H+.012),(.09,.09,.03),groups['legs'],feet,bevel=.006)
    for k,(name,pos,rot,sz,flat) in enumerate(CUSHIONS):pillow(name,groups['cushions'],cloth,seam,12 if mobile else 20,pos,rot,sz,k,flatten=flat)
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
