"""Product still made from the EXPORTED GLB, with a plain studio and soft lights.
This complements, and never replaces, the WebGL screenshots in previews/.
Blender --background --factory-startup --python source/render_export.py
"""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'models'/'sofa.glb'))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.68,.72,.78,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.22
scene.view_settings.view_transform='AgX'
def light(name,pos,power,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos
    o.rotation_euler=(Vector((0,0,.45))-o.location).to_track_quat('-Z','Y').to_euler()
light('Large softbox',(-3,-3,4),650,3.0,(1,.94,.85))
light('Fill',(3,-1,2.5),230,2.4,(.86,.91,1))
light('Rear strip',(0,3,3),450,2.5,(1,.97,.91))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));ground=bpy.context.object
m=bpy.data.materials.new('studio_floor');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.55,.53,.49,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9;ground.data.materials.append(m)
camdata=bpy.data.cameras.new('Export inspection camera');camera=bpy.data.objects.new('Export inspection camera',camdata);scene.collection.objects.link(camera)
camera.location=(2.7,-4.2,2.35);target=Vector((0,-.02,.48));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camdata.lens=54;scene.camera=camera
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'previews'/'studio-export.png')
bpy.ops.render.render(write_still=True)
