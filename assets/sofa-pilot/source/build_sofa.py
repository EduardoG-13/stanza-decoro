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
# Loose seat cushions (FEAT-002 rev2). Each tuple: name, pos, rot (deg, XYZ), half size
# (a=width, b=height), loft (max fill per face, m). Pillow axes: local X = width, local Z =
# height (v=-1 is the LOWER edge), local Y = thickness; side=+1 is the REAR face (it maps to
# world +Y = towards the backrest for every cushion), side=-1 the front face.
# Composition follows SOFA-2.jpg: cushions stand fairly upright, lean back and rest their lower
# edge on the rear of the seat; staggered in depth (02 and 04 against the backrest, 01 in the
# low left arm/back corner, 03 - the tallest - and 05 one row forward leaning on their
# neighbours), three light + two olive positions, all ending before the chaise (back ends at
# x~.62). pos (y,z) were SOLVED, not eyeballed: each cushion is translated until its
# undeformed shell overlaps the seat by ~1 cm and its rear face overlaps what it leans on
# by ~1-1.5 cm (.agents-only solver, see docs/sofa-3d-review/feat002-rev2-cushions.md); the
# generator then turns that overlap into localized soft compression (settle_contacts()).
CUSHIONS = [
  ('cushion_01',(-0.8,-0.016,0.6707),(-14,-6,18),(0.19,0.19),0.08),
  ('cushion_02',(-0.5,0.1567,0.7112),(-16,14,3),(0.182,0.21),0.082),
  ('cushion_03',(-0.16,0.0626,0.7177),(-14,-10,-3),(0.2,0.222),0.084),
  ('cushion_04',(0.17,0.1773,0.6909),(-17,-15,4),(0.166,0.19),0.08),
  ('cushion_05',(0.45,0.0348,0.6703),(-15,-24,-12),(0.156,0.152),0.072)]
# Contact solve order: what each cushion rests on is built before it.
SETTLE_ORDER = ['cushion_02','cushion_04','cushion_03','cushion_01','cushion_05']

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

def seat_dimple(x,y):
    """Soft foam dimple under each cushion's real footprint (FEAT-002 rev2): the cushions
    lean back, so the lower edge rests ~5 cm forward of the holder centre; the dimple is a
    band along the cushion width there, shallow (<=16 mm), so the seat reads as cradling."""
    d=0
    for _cn,cp,_cr,cs,_cl in CUSHIONS:
        d+=.011*exp(-((x-cp[0])/(cs[0]+.07))**2-((y-cp[1]+.05)/.13)**2)
    return min(d,.016)

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
            # Shallow foam dimple under each cushion footprint (see seat_dimple()).
            depression=seat_dimple(x,y) if z>.4 else 0
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

def pillow_shape(n,size,seed,loft):
    """Undeformed knife-edge cushion in its local frame (X width, Z height, Y thickness)."""
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
                d=.008+loft*belly+gathers
                vs.append((x,side*d,z));uv.append((x/TILE,z/TILE))
    block=(n+1)**2
    for s in range(2):
        for j in range(n):
            for i in range(n):
                k=s*block+j*(n+1)+i;fs.append((k,k+1,k+n+2,k+n+1))
    perimeter=list(range(n+1))+[j*(n+1)+n for j in range(1,n+1)]+[n*(n+1)+i for i in range(n-1,-1,-1)]+[j*(n+1) for j in range(n-1,0,-1)]
    for i,k in enumerate(perimeter):k2=perimeter[(i+1)%len(perimeter)];fs.append((k,k2,k2+block,k+block))
    return vs,uv,fs,perimeter

def cushion_matrix(pos,rot):
    from mathutils import Matrix, Euler
    return Matrix.Translation(Vector(pos)) @ Euler(tuple(math.radians(r) for r in rot),'XYZ').to_matrix().to_4x4()

def collider(verts,faces):
    """BVH of a closed shell with face normals recalculated OUTWARD (signed distances)."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    bm=bmesh.new(); bv=[bm.verts.new(Vector(v)) for v in verts]
    for f in faces: bm.faces.new([bv[k] for k in f])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.normal_update()
    t=BVHTree.FromBMesh(bm); bm.free()
    return t

def _signed(bvh,p,reach=.12):
    loc,nrm,_i,dist=bvh.find_nearest(p,reach)
    if loc is None: return None,None
    return (p-loc).dot(nrm),nrm

def settle_contacts(pts,faces,colliders,radius=.045,bulge=.45):
    """FEAT-002 rev2 localized contact deformation of one cushion (world space).
    colliders: [(bvh, clearance)]; clearance<0 = allowed soft compression depth (m).
    Penetrating vertices are pushed out along the collider normal; the displacement field
    is then Gaussian-smoothed over the cushion surface (radius) so the compression spreads
    as a soft falloff PATCH around the real contact (lower-edge band on the seat, rear-face
    patch on the backrest/arm or neighbour) instead of a whole-face thinning or a hard
    facet. A small difference-of-Gaussians ring bulges the fabric outward around each patch
    (displaced fill), and a last projection pass guarantees no vertex passes the allowance."""
    import bmesh
    from mathutils.kdtree import KDTree
    V=len(pts); P0=[Vector(p) for p in pts]
    bm=bmesh.new(); bv=[bm.verts.new(p) for p in P0]
    for f in faces: bm.faces.new([bv[k] for k in f])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.normal_update()
    N=[v.normal.copy() for v in bm.verts]; bm.free()
    kd=KDTree(V)
    for k,p in enumerate(P0): kd.insert(p,k)
    kd.balance()
    near=[kd.find_range(p,radius) for p in P0]
    s2=(radius/2)**2
    W=[[(idx,exp(-d*d/(2*s2))) for _c,idx,d in nb] for nb in near]
    def smooth(D):
        out=[]
        for k in range(V):
            acc=Vector(); ws=0
            for idx,w in W[k]: acc+=D[idx]*w; ws+=w
            out.append(acc/ws)
        return out
    def project(D):
        hit=False
        for k in range(V):
            p=P0[k]+D[k]
            for bvh,clr in colliders:
                s,nrm=_signed(bvh,p)
                if s is not None and s<clr:
                    D[k]=D[k]+nrm*(clr-s); p=P0[k]+D[k]; hit=True
        return hit
    D=[Vector() for _ in range(V)]
    for _it in range(10):
        if not project(D) and _it: break
        D=smooth(D)
    # displaced fill: ring bulge just outside the compressed patch, along the cushion normal
    M=[d.length for d in D]
    wide=[sum(M[idx]*w for idx,w in W[k])/sum(w for _i,w in W[k]) for k in range(V)]
    wide=[sum(wide[idx]*w for idx,w in W[k])/sum(w for _i,w in W[k]) for k in range(V)]
    for k in range(V):
        ring=max(0,wide[k]-M[k])
        D[k]=D[k]+N[k]*(bulge*ring)
    for _ in range(3): project(D)
    return [P0[k]+D[k] for k in range(V)]

def cushion_geometry(n,pos,rot,size,seed,loft,colliders):
    """Settled cushion: returns local cover verts, uv, faces, perimeter, welt line (local)
    and the world-space verts (used as a collider by cushions that lean on this one)."""
    vs,uv,fs,perimeter=pillow_shape(n,size,seed,loft)
    M=cushion_matrix(pos,rot); Mi=M.inverted()
    world=settle_contacts([M@Vector(v) for v in vs],fs,colliders)
    block=(n+1)**2
    # Welt follows the deformed knife edge (midpoint of front/rear perimeter rows) and is kept
    # just proud of anything it touches so the seam never vanishes into seat, back or neighbour.
    line=[]
    for k in perimeter:
        p=(world[k]+world[k+block])/2
        for _ in range(2):
            for bvh,_clr in colliders:
                s,nrm=_signed(bvh,p,.03)
                if s is not None and s<.0008: p=p+nrm*(.0008-s)
        line.append(tuple(Mi@p))
    return [tuple(Mi@p) for p in world],uv,fs,perimeter,line,world

def pillow(name,parent,mat,seam,geo,pos,rot):
    vs,uv,fs,perimeter,line,_world=geo
    holder=empty(name,parent);holder.location=pos;holder.rotation_euler=tuple(math.radians(r) for r in rot)
    ob=mesh(name+'_cover',vs,fs,holder,mat,uv)
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
    root=empty('sofa_root');root['modelId']='stanza-organic-01';root['revision']='1.3.0';root['dimensions_estimated']=True;root['construction']='illustrative'
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
        depression=seat_dimple(x,y)
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
    # Rails and webbing anchors are fitted INSIDE the upholstered contour (rev2 fix: the
    # FEAT-003 straight rails at y=-.50/.46 and the strap ends poked up to ~15 cm through the
    # seat cover where the bean outline swings inward). The seat cover's band at rail height
    # (z .17-.24) sits at ~99% of OUTLINE; FIT_S/FIT_M keep a clear margin inside it.
    STRAP_X=[-.86,-.58,-.30,-.02,.26,.54,.84]   # anchor columns across the width
    FIT_S=.99; FIT_M=.035
    ring=[catmull(OUTLINE,i/720) for i in range(720)]
    def edge_y(x,front):
        ys=[p.y*FIT_S for p in ring if abs(p.x*FIT_S-x)<.012]
        return min(ys) if front else max(ys)
    def span_y(x0,x1,front):
        xs=[x0+(x1-x0)*k/24 for k in range(25)]
        return max(edge_y(x,True) for x in xs)+FIT_M+.025 if front else min(edge_y(x,False) for x in xs)-FIT_M-.025
    FR_X=(-.95,.95); RR_X=(-.90,.88)
    FRONT_Y=span_y(*FR_X,True); REAR_Y=span_y(*RR_X,False)
    box('front_rail',((FR_X[0]+FR_X[1])/2,FRONT_Y,.205),(FR_X[1]-FR_X[0],.05,.07),groups['frame'],frame)
    box('rear_rail',((RR_X[0]+RR_X[1])/2,REAR_Y,.205),(RR_X[1]-RR_X[0],.05,.07),groups['frame'],frame)
    for k,x in enumerate([-.9,.92]):
        y0=max(edge_y(x+d,True) for d in (-.025,0,.025))+FIT_M; y1=min(edge_y(x+d,False) for d in (-.025,0,.025))-FIT_M
        box('side_rail_'+str(k),(x,(y0+y1)/2,.205),(.05,y1-y0,.07),groups['frame'],frame)
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
    def contour_y(x,base):                       # lateral strap rows stay inside the contour
        return base*(1-.12*(x/1.2)**2)
    WZ=.225; sb=0
    anchors={}
    for k,x in enumerate(STRAP_X):
        fa=(x,FRONT_Y,WZ); ra=(x,REAR_Y,WZ)
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
    # FEAT-002 rev2: cushions settle against the OUTER cover shells (raw mesh data; the 1.5 mm
    # solidify grows inward) and against the cushions they lean on, in SETTLE_ORDER.
    # Groups are still at the origin here, so mesh coordinates are world coordinates.
    def shell(ob): return [tuple(v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons]
    rigid=[(collider(*shell(seatob)),-.0012),(collider(*shell(backob)),-.0012)]
    spec={c[0]:(k,c) for k,c in enumerate(CUSHIONS)}; geos={}
    for name in SETTLE_ORDER:
        k,(_n,pos,rot,sz,loft)=spec[name]
        others=[(collider(geos[o][5],geos[o][2]),-.0008) for o in geos]
        geos[name]=cushion_geometry(12 if mobile else 20,pos,rot,sz,k,loft,rigid+others)
    for name,pos,rot,sz,loft in CUSHIONS: pillow(name,groups['cushions'],cloth,seam,geos[name],pos,rot)
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
