"""CPU-only executable transfer test. Never opens/saves a production scene."""
import bpy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

root = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out = Path(args[0]) if args else root/'transfer-output'
out.mkdir(parents=True, exist_ok=True)
recipe_path = root/'recipes/procedural_ink.py'
assert recipe_path.is_file(), 'executable recipe missing'
before = (len(bpy.data.objects), len(bpy.data.materials), len(bpy.data.meshes))
spec = importlib.util.spec_from_file_location('ink', recipe_path)
recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe)
assert before == (len(bpy.data.objects), len(bpy.data.materials), len(bpy.data.meshes)), 'import mutated scene'
# Factory-startup is our private test scene, never user source.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
mesh = bpy.data.meshes.new('banner_test_mesh')
mesh.from_pydata([(-.01,0,-.01),(.01,0,-.01),(.01,0,.01),(-.01,0,.01)], [], [(0,1,2,3)])
banner = bpy.data.objects.new('Banner coupon', mesh)
bpy.context.scene.collection.objects.link(banner)
material = bpy.data.materials.new('Coupon base')
material.use_nodes = True
material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.18,.22,.25,1)
banner.data.materials.append(material)
coords_before = [tuple(v.co) for v in mesh.vertices]
receipt = recipe.apply(banner, period_m=.000625, axes=('X','Z'), strength=.65)
node_count = len(banner.active_material.node_tree.nodes)
recipe.apply(banner, period_m=.000625, axes=('X','Z'), strength=.65)
assert len(banner.active_material.node_tree.nodes) == node_count, 'non-idempotent apply'
assert [tuple(v.co) for v in mesh.vertices] == coords_before
assert banner.active_material != material, 'source material mutated'
assert len(material.node_tree.nodes) == 2, 'original material changed'
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.render.threads_mode = 'FIXED'
scene.render.threads = 2
scene.render.resolution_x = scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.use_compositing = False
world = bpy.data.worlds.new('Transfer test world')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.3,.3,.3,1)
scene.world = world
camera = bpy.data.cameras.new('Transfer camera')
cam = bpy.data.objects.new('Transfer camera', camera)
scene.collection.objects.link(cam)
scene.camera = cam
camera.type = 'ORTHO'
from mathutils import Vector

def render_object(obj, name):
    for other in scene.objects:
        if other.type == 'MESH': other.hide_render = other != obj
    corners = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    center = sum(corners, Vector())/8
    dims = [max(v[k] for v in corners)-min(v[k] for v in corners) for k in range(3)]
    distance = max(dims)*3+.1
    cam.location = center+Vector((0,-distance,0))
    cam.rotation_euler = (center-cam.location).to_track_quat('-Z','Y').to_euler()
    camera.ortho_scale = max(dims[0], dims[2]) * 1.1
    scene.render.filepath = str(out/(name+'.png'))
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    return dict(path=scene.render.filepath, wall_seconds=time.monotonic()-start,
                dimensions=[512,512], pixel_pitch_m=camera.ortho_scale/512,
                device='CPU', samples=8)

images = [render_object(banner, 'banner-control')]
source = Path(args[1]) if len(args)>1 else None
if source:
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with bpy.data.libraries.load(str(source), link=False) as (available, selected):
        assert 'SLP front folded facets' in available.objects, 'transfer receiver missing'
        selected.objects = ['SLP front folded facets']
    stone = selected.objects[0]
    scene.collection.objects.link(stone)
    stone.hide_render = False
    stone.hide_viewport = False
    stone_coords = [tuple(v.co) for v in stone.data.vertices]
    original_materials = list(stone.data.materials)
    # One explicit isolated material coupon, not a claim of preserving original style.
    stone.data.materials.clear()
    stone.data.materials.append(material)
    for poly in stone.data.polygons: poly.material_index = 0
    transfer = recipe.apply(stone, period_m=.000625, axes=('X','Z'), strength=.65)
    assert [tuple(v.co) for v in stone.data.vertices] == stone_coords
    images.append(render_object(stone, 'stone-transfer'))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    transfer.update(source=str(source), source_sha256=source_hash, receiver=stone.name,
                    vertices=len(stone.data.vertices), polygons=len(stone.data.polygons),
                    geometry_unchanged=True, source_file_unchanged=True,
                    caveat='material coupon replaces original material in disposable scene; not integrated style approval')
else:
    transfer = None
for image in images:
    image['sha256'] = hashlib.sha256(Path(image['path']).read_bytes()).hexdigest()
result = dict(import_inert=True, idempotent=True, banner_recipe=receipt, transfer=transfer,
              images=images, max_zoom_gate=None, owner_approved=False,
              conclusion='Executable transfer proven, aesthetic and final-density acceptance NOT proven')
(out/'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'transfer.blend'))
print('TRANSFER_RESULT', json.dumps(result), flush=True)
