"""Procedural precast positioning study, authored with Blender's Python API.

Run with Blender 5.2+:
  Blender --background --factory-startup --python kmong_227330.py -- --mode build
  Blender --background --factory-startup --python kmong_227330.py -- --mode stills
  Blender --background --factory-startup --python kmong_227330.py -- --mode preview
  Blender --background --factory-startup --python kmong_227330.py -- --mode final

Original concept geometry. This is an explanatory visualization, not an erection
method or a client-specific connection design. No third-party model assets used.
"""

import argparse
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


FPS = 30
FRAME_END = 900
GRID_X = (-6.0, 0.0, 6.0)
GRID_Y = (-3.0, 3.0)
COL_BOTTOM = 0.20
COL_TOP = 4.16
CORBEL_TOP = 3.56
PAD_TOP = 3.58
BEAM_HEIGHT = 0.58
SLAB_BOTTOM = PAD_TOP + BEAM_HEIGHT + 0.018
PLINTH_TOP = -0.12
ANCHOR_FOOTING_BOTTOM = -0.44
ANCHOR_FOOTING_TOP = 0.06
FOOTPLATE_THICKNESS = 0.055
SHOTS = [
    (1, 90, "00", "프리캐스트 구조부재 배치 시각화", "기둥·보·슬래브의 배치 순서를 보여줍니다.", "OVERVIEW"),
    (91, 240, "01", "기둥 배치", "기초 접합 상세 생략 · 임시 지지부(개념)", "COLUMNS"),
    (241, 390, "02", "보 배치", "받침부 위로 보를 정렬하고 안착시킵니다.", "BEAMS"),
    (391, 570, "DETAIL", "받침부 정렬과 안착", "받침 패드 안착 예시 · 영구 접합 상세 생략", "BEARING DETAIL"),
    (571, 750, "03", "슬래브 배치", "슬래브 간 접합·그라우팅 공정 생략", "SLABS"),
    (751, 900, "04", "구조부재 배치 완료", "접합·그라우팅 상세는 발주처 도면에 따라 반영", "POSITIONING STUDY"),
]


def arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    packaged = Path(__file__).resolve().parent.name == "source"
    default_output = Path(__file__).resolve().parent.parent if packaged else Path.cwd() / "output/prototypes/kmong-227330-v2"
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("build", "stills", "preview", "final"), default="build")
    p.add_argument("--output", type=Path, default=default_output)
    p.add_argument("--work-dir", type=Path, default=Path.cwd() / "tmp/prototypes/kmong-227330-v2")
    p.add_argument("--font-dir", type=Path)
    p.add_argument("--frames", help="Comma-separated still frames; used by stills mode")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=FRAME_END)
    p.add_argument("--skip-encode", action="store_true")
    p.add_argument("--samples", type=int, help="Override EEVEE temporal samples (final default: 32)")
    args = p.parse_args(argv)
    if not 1 <= args.start <= args.end <= FRAME_END:
        p.error("--start and --end must define a range within frames 1–900")
    if args.frames and any(not 1 <= int(f) <= FRAME_END for f in args.frames.split(",")):
        p.error("Still frames must be within 1–900")
    if args.samples is not None and args.samples < 1:
        p.error("--samples must be positive")
    return args


def srgb(hex_color):
    v = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)


def material(name, color, roughness=0.6, metallic=0.0, texture=False):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*srgb(color), 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*srgb(color), 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if texture:
        n = m.node_tree.nodes
        links = m.node_tree.links
        coords = n.new("ShaderNodeTexCoord")
        noise = n.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 65
        noise.inputs["Detail"].default_value = 2.2
        noise.inputs["Roughness"].default_value = 0.7
        ramp = n.new("ShaderNodeValToRGB")
        base = srgb(color)
        ramp.color_ramp.elements[0].position = 0.15
        ramp.color_ramp.elements[0].color = (*(c * 0.88 for c in base), 1)
        ramp.color_ramp.elements[1].position = 0.85
        ramp.color_ramp.elements[1].color = (*(min(1, c * 1.07) for c in base), 1)
        bump = n.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.06
        bump.inputs["Distance"].default_value = 0.003
        links.new(coords.outputs["Object"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], ramp.inputs[0])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def move_to(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def cube(name, location, dimensions, mat, collection, bevel=0.015, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to(obj, collection)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        b = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        b.width = bevel
        b.segments = 3
        b.affect = "EDGES"
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    if parent:
        obj.parent = parent
    return obj


def empty(name, collection):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.empty_display_size = 0.25
    return obj


def tube(name, start, end, radius, mat, collection, parent=None, vertices=12):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b - a).length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    move_to(obj, collection)
    if parent:
        obj.parent = parent
    for poly in obj.data.polygons:
        poly.use_smooth = vertices > 6 and len(poly.vertices) == 4
    if vertices == 6:
        bevel = obj.modifiers.new("Machined hex edges", "BEVEL")
        bevel.width, bevel.segments = 0.001, 2
        obj.modifiers.new("Hardware face normals", "WEIGHTED_NORMAL")
    return obj


def build_brace(identity, x, y, direction, column_root, column_parts, finish,
                foundation, steel, hardware, padmat, foundations, collection):
    """Illustrative anchorage, with all contact points derived from the support.

    Footing dimensions and fittings are visual proportions, not an anchor design.
    Cast-in receiver plates travel with columns; removable hardware installs only
    after its column is positioned. Footing bodies continue below ground level.
    """
    u = Vector((*direction, 0))
    v = Vector((-direction[1], direction[0], 0))
    z = Vector((0, 0, 1))
    theta = math.atan2(u.y, u.x)
    center = Vector((x, y, 0))
    root = empty(f"{identity} · brace assembly", collection)
    root["brace_id"], root["brace_role"] = identity, "assembly"
    root["column_root"], root["install_frame"] = column_root.name, finish
    detachable = []

    def mark(obj, role, fixed=False):
        obj["brace_id"], obj["brace_role"] = identity, role
        if not fixed:
            detachable.append(obj)
        return obj

    def box(label, point, dims, role, mat=steel, parent=root, fixed=False):
        obj = cube(f"{identity} · {label}", point, dims, mat, collection, bevel=0.003, parent=parent)
        obj.rotation_euler.z = theta
        return mark(obj, role, fixed)

    def cylinder(label, point, axis, length, radius, role, mat=hardware,
                 parent=root, fixed=False, vertices=16):
        point = Vector(point)
        axis = Vector(axis)
        return mark(tube(f"{identity} · {label}", point - axis * length / 2,
                         point + axis * length / 2, radius, mat, collection,
                         parent=parent, vertices=vertices), role, fixed)

    foot_xy = center + u * 1.30
    footing = cube(f"{identity} · embedded anchor footing",
                   (foot_xy.x, foot_xy.y, (ANCHOR_FOOTING_TOP + ANCHOR_FOOTING_BOTTOM) / 2),
                   (0.70, 0.70, ANCHOR_FOOTING_TOP - ANCHOR_FOOTING_BOTTOM),
                   foundation, foundations, bevel=0.022)
    mark(footing, "anchor_footing", fixed=True)
    footing["ground_level"] = PLINTH_TOP
    support_top = footing.location.z + max(p.co.z for p in footing.data.vertices)
    plate_center = Vector((foot_xy.x, foot_xy.y, support_top + FOOTPLATE_THICKNESS / 2))
    footplate = box("anchored footplate", plate_center, (0.23, 0.23, FOOTPLATE_THICKNESS), "footplate")
    plate_top = footplate.location.z + max(p.co.z for p in footplate.data.vertices)
    lower = Vector((foot_xy.x, foot_xy.y, plate_top + 0.060))
    upper = center + u * (0.22 + 0.015 + 0.060) + z * 2.65

    # Receiver and its visible fasteners are part of the column unit.
    receiver = box("column receiver plate", center + u * 0.2275 + z * upper.z,
                   (0.015, 0.22, 0.26), "column_insert_plate",
                   parent=column_root, fixed=True)
    column_parts.append(receiver)
    for index, dz in enumerate((-0.095, 0.095), 1):
        fastener = center + z * (upper.z + dz)
        for label, offset, length, radius, verts in (
                ("stud", 0.217, 0.096, 0.008, 12),
                ("washer", 0.238, 0.005, 0.023, 20),
                ("hex head", 0.251, 0.022, 0.017, 6)):
            obj = cylinder(f"receiver {index} {label}", fastener + u * offset, u,
                           length, radius, "column_insert_fastener", parent=column_root,
                           fixed=True, vertices=verts)
            column_parts.append(obj)

    # Four illustrative anchor fasteners penetrate the footing cap and footplate.
    for i, (du, dv) in enumerate(((a, b) for a in (-0.078, 0.078) for b in (-0.078, 0.078)), 1):
        point = Vector((foot_xy.x, foot_xy.y, 0)) + u * du + v * dv
        cylinder(f"anchor {i} shaft", point + z * (support_top - 0.010), z,
                 FOOTPLATE_THICKNESS + 0.130, 0.008, "anchor_fastener")
        cylinder(f"anchor {i} washer", point + z * (plate_top + 0.003), z,
                 0.005, 0.023, "anchor_fastener", vertices=20)
        cylinder(f"anchor {i} nut", point + z * (plate_top + 0.017), z,
                 0.022, 0.017, "anchor_fastener", vertices=6)

    for end, point in (("upper", upper), ("lower", lower)):
        for side in (-1, 1):
            ear_center = point + v * (side * 0.052)
            if end == "upper":
                ear_center -= u * 0.010
            box(f"{end} clevis ear {side}", ear_center,
                (0.10 if end == "upper" else 0.11, 0.014, 0.12), f"{end}_clevis")
        pin = cylinder(f"{end} hinge pin", point, v, 0.155, 0.011, f"{end}_pin")
        cylinder(f"{end} rod eye", point, v, 0.075, 0.045, f"{end}_eye", mat=steel)
        for side in (-1, 1):
            cylinder(f"{end} pin head {side}", point + v * (side * 0.081), v,
                     0.012, 0.018, f"{end}_pin_head")
        root[f"{end}_pin"] = pin.name

    rod = mark(tube(f"{identity} · brace rod", upper, lower, 0.032, steel,
                    collection, parent=root), "rod")
    collar = mark(tube(f"{identity} · adjustment collar", upper.lerp(lower, 0.58),
                       upper.lerp(lower, 0.74), 0.045, padmat, collection, parent=root), "collar")
    root["rod"], root["footplate"], root["footing"] = rod.name, footplate.name, footing.name
    visible_schedule(detachable, [(1, True), (90, True), (91, False),
                                  (finish - 1, False), (finish, True), (900, True)])
    return root


def corbel(name, x, y, direction, mat, collection, parent):
    # Trapezoidal underside, broad horizontal bearing seat. Local +X template.
    vertices = [(a, b, z) for a, z in ((0.19, 2.98), (0.73, 3.32), (0.73, CORBEL_TOP), (0.19, CORBEL_TOP)) for b in (-0.19, 0.19)]
    faces = [(0, 2, 4, 6), (1, 7, 5, 3), (0, 1, 3, 2), (2, 3, 5, 4), (4, 5, 7, 6), (6, 7, 1, 0)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = (x, y, 0)
    obj.rotation_euler.z = math.atan2(direction[1], direction[0])
    obj.data.materials.append(mat)
    obj.parent = parent
    bevel = obj.modifiers.new("Cast edge bevel", "BEVEL")
    bevel.width = 0.014
    bevel.segments = 3
    obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def key(obj, data_path, value, frame):
    setattr(obj, data_path, value)
    obj.keyframe_insert(data_path=data_path, frame=frame)


def curves(obj):
    anim = obj.animation_data
    if not anim or not anim.action:
        return []
    action = anim.action
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    return [f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]


def interpolation(obj, constant=False):
    for fcurve in curves(obj):
        is_visibility = "hide_" in fcurve.data_path
        for p in fcurve.keyframe_points:
            p.interpolation = "CONSTANT" if constant or is_visibility else "BEZIER"
            if not (constant or is_visibility):
                p.handle_left_type = "AUTO_CLAMPED"
                p.handle_right_type = "AUTO_CLAMPED"


def visible_schedule(objects, states):
    for obj in objects:
        for frame, visible in states:
            key(obj, "hide_render", not visible, frame)
            key(obj, "hide_viewport", not visible, frame)
        interpolation(obj, constant=True)


def assembly_motion(root, children, start, finish, lift=5.2):
    for frame, location in ((1, (0, 0, 0)), (90, (0, 0, 0)), (91, (0, 0, lift)), (start, (0, 0, lift)), (finish, (0, 0, 0)), (900, (0, 0, 0))):
        key(root, "location", location, frame)
    interpolation(root)
    visible_schedule(children, [(1, True), (90, True), (91, False), (start - 1, False), (start, True), (900, True)])


def camera(name, scene, collection, start, end, positions, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36
    data.clip_end = 250
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    for frame, pos in ((start, positions[0]), (end, positions[1])):
        obj.location = pos
        obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    interpolation(obj)
    return obj


def light(name, location, energy, size, color, collection):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, 1.5)) - obj.location).to_track_quat("-Z", "Y").to_euler()


def fit_wide_camera(scene, cam, frames):
    """Keep the complete display plinth and roof clear of the native caption bands."""
    points = [Vector((x, y, z)) for x in (-7.9, 7.9) for y in (-5.0, 5.0) for z in (-0.48, -0.12)]
    points += [Vector((x, y, SLAB_BOTTOM + 0.25)) for x in (-6.12, 6.12) for y in (-3.22, 3.22)]
    boxes = []
    for f in frames:
        scene.frame_set(f)
        scene.view_layers[0].update()
        coords = [world_to_camera_view(scene, cam, p) for p in points]
        boxes.append((min(p.x for p in coords), max(p.x for p in coords), min(p.y for p in coords), max(p.y for p in coords)))
    factor = min(min(0.86 / (b[1] - b[0]), 0.66 / (b[3] - b[2])) for b in boxes)
    cam.data.lens *= min(1, factor)
    centers = []
    for f in frames:
        scene.frame_set(f)
        scene.view_layers[0].update()
        coords = [world_to_camera_view(scene, cam, p) for p in points]
        centers.append((min(p.y for p in coords) + max(p.y for p in coords)) / 2)
    cam.data.shift_y += (sum(centers) / len(centers) - 0.555) * 9 / 16


def prepare_assets(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    candidates = [args.font_dir, assets, Path.cwd() / "tmp/pdfs/design-review/fonts"]
    for filename in ("Pretendard-Regular.ttf", "Pretendard-SemiBold.ttf"):
        found = next((p / filename for p in candidates if p and (p / filename).exists()), None)
        if not found:
            raise FileNotFoundError(f"Missing {filename}; provide --font-dir")
        if found.resolve() != (assets / filename).resolve():
            shutil.copy2(found, assets / filename)
    license_source = next((p / "Pretendard-LICENSE.txt" for p in candidates if p and (p / "Pretendard-LICENSE.txt").exists()), None)
    if license_source and license_source.resolve() != (assets / "Pretendard-LICENSE.txt").resolve():
        shutil.copy2(license_source, assets / "Pretendard-LICENSE.txt")
    source_dir = output / "source"
    source_dir.mkdir(exist_ok=True)
    if Path(__file__).resolve() != (source_dir / Path(__file__).name).resolve():
        shutil.copy2(__file__, source_dir / Path(__file__).name)
    audit_source = Path(__file__).resolve().parent / "audit_kmong_227330.py"
    if audit_source.exists() and audit_source.resolve() != (source_dir / audit_source.name).resolve():
        shutil.copy2(audit_source, source_dir / audit_source.name)
    return output, assets


def setup_scene(scene, width, height, samples):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.fps, scene.render.fps_base = FPS, 1
    scene.frame_start, scene.frame_end = 1, FRAME_END
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 35
    scene.render.film_transparent = False
    scene.eevee.taa_render_samples = samples
    # 4K virtual shadow maps exceed the factory 512 MB pool in the wide shot.
    scene.eevee.shadow_pool_size = "2048" if width >= 3840 else "512"
    if width >= 3840:
        scene.eevee.shadow_resolution_scale = 0.5
    if hasattr(scene.eevee, "use_fast_gi"):
        scene.eevee.use_fast_gi = True


def make_slab_template(mat, collection):
    slab = cube("Slab geometry master", (0, 0, 0), (6.10, 1.18, 0.25), mat, collection, bevel=0)
    cutters = bpy.data.collections.new("Temporary hollow-core cutters")
    bpy.context.scene.collection.children.link(cutters)
    for i in range(5):
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.080, depth=6.4, location=(0, (i - 2) * 0.225, 0))
        cutter = bpy.context.object
        cutter.rotation_euler.y = math.pi / 2
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        move_to(cutter, cutters)
    bpy.context.view_layer.objects.active = slab
    modifier = slab.modifiers.new("Five longitudinal hollow cores", "BOOLEAN")
    modifier.operation, modifier.operand_type = "DIFFERENCE", "COLLECTION"
    modifier.collection = cutters
    modifier.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for obj in list(cutters.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(cutters)
    bevel = slab.modifiers.new("Slab arrises", "BEVEL")
    bevel.width, bevel.segments = 0.008, 2
    slab.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return slab


def build_model(args, width, height, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Assembly"
    setup_scene(scene, width, height, samples)
    scene.render.use_sequencer = False
    root = bpy.data.collections.new("PRECAST · Procedural study")
    scene.collection.children.link(root)
    groups = {}
    for name in ("01 Foundations", "02 Columns and corbels", "03 Beams and pads", "04 Hollow-core slabs", "05 Temporary braces", "06 Connection guides", "07 Studio", "08 Cameras"):
        groups[name] = bpy.data.collections.new(name)
        root.children.link(groups[name])
    concrete = material("Concrete · warm fine aggregate", "B9B9AF", texture=True)
    foundation = material("Foundation concrete", "A7ACA5", texture=True)
    padmat = material("Bearing pad · charcoal", "263A3B", 0.88)
    steel = material("Temporary braces · teal steel", "507577", 0.37, 0.45)
    hardware = material("Anchor and hinge hardware · galvanized steel", "8D9C9C", 0.30, 0.72)
    orange = material("Safety orange · explanatory accent", "D64C2F", 0.42)
    stage = material("Display plinth", "DBDED7", 0.7)
    backdrop = material("Studio floor", "EBEDE7", 0.86)
    gridmat = material("Construction grid", "C0C6BE", 0.8)

    studio = groups["07 Studio"]
    cube("Continuous studio floor", (0, 0, -0.55), (200, 200, 0.12), backdrop, studio, bevel=0)
    cube("Architectural display plinth", (0, 0, -0.30), (15.8, 10.0, 0.36), stage, studio, bevel=0.09)
    cube("Front plinth accent", (-5.9, -5.007, -0.23), (2.2, 0.025, 0.038), orange, studio, bevel=0.006)
    for x in GRID_X:
        tube(f"Grid x={x}", (x, -4.35, -0.111), (x, 4.35, -0.111), 0.008, gridmat, studio)
    for y in GRID_Y:
        tube(f"Grid y={y}", (-7.25, y, -0.111), (7.25, y, -0.111), 0.008, gridmat, studio)

    all_children = []
    col_roots = []
    columns = groups["02 Columns and corbels"]
    pads_by_key = {}
    for xi, x in enumerate(GRID_X):
        for yi, y in enumerate(GRID_Y):
            tag = f"C{xi + 1}{yi + 1}"
            cube(f"{tag} · foundation pad", (x, y, 0.015), (1.45, 1.45, 0.37), foundation, groups["01 Foundations"], bevel=0.035)
            parent = empty(f"{tag} · column animation", columns)
            parts = [cube(f"{tag} · precast column", (x, y, (COL_BOTTOM + COL_TOP) / 2), (0.44, 0.44, COL_TOP - COL_BOTTOM), concrete, columns, bevel=0.018, parent=parent)]
            directions = []
            if xi > 0:
                directions.append((-1, 0))
            if xi < 2:
                directions.append((1, 0))
            directions.append((0, 1 if yi == 0 else -1))
            for dx, dy in directions:
                parts.append(corbel(f"{tag} · corbel {dx},{dy}", x, y, (dx, dy), concrete, columns, parent))
                pos = (x + dx * 0.49, y + dy * 0.49, CORBEL_TOP + 0.01)
                dims = (0.43, 0.33, 0.02) if dx else (0.33, 0.43, 0.02)
                pad = cube(f"{tag} · bearing pad {dx},{dy}", pos, dims, padmat, columns, bevel=0.006, parent=parent)
                pads_by_key[(x, y, dx, dy)] = pad
                parts.append(pad)
            # Front/rear pairs erect in three clear waves.
            start = 96 + xi * 36 + yi * 8
            finish = start + 43
            guides = []
            for dx in (-1, 1):
                for dy in (-1, 1):
                    guides.append(cube("Column target · corner X", (x + dx * 0.275, y + dy * 0.34, 0.211), (0.15, 0.015, 0.012), orange, groups["06 Connection guides"], bevel=0.003))
                    guides.append(cube("Column target · corner Y", (x + dx * 0.34, y + dy * 0.275, 0.211), (0.015, 0.15, 0.012), orange, groups["06 Connection guides"], bevel=0.003))
            visible_schedule(guides, [(1, False), (start - 1, False), (start, True), (finish + 8, True), (finish + 9, False), (900, False)])
            col_roots.append((parent, parts, start, finish, x, y))
            all_children.extend(parts)

    beam_collection = groups["03 Beams and pads"]
    beam_parts = []
    selected = None
    schedule_index = 0
    # Three transverse beams support the hollow-core planks.
    for i, x in enumerate(GRID_X):
        parent = empty(f"BY{i + 1} · beam animation", beam_collection)
        obj = cube(f"BY{i + 1} · transverse beam", (x, 0, PAD_TOP + BEAM_HEIGHT / 2), (0.38, 5.56, BEAM_HEIGHT), concrete, beam_collection, bevel=0.018, parent=parent)
        roof_pad = cube(f"BY{i + 1} · slab bearing strip", (x, 0, PAD_TOP + BEAM_HEIGHT + 0.009), (0.34, 5.56, 0.018), padmat, beam_collection, bevel=0.003, parent=parent)
        start = 246 + schedule_index * 17
        assembly_motion(parent, [obj, roof_pad], start, start + 38, lift=4.2)
        beam_parts.append(obj)
        schedule_index += 1
    for yi, y in enumerate(GRID_Y):
        for bay, x in enumerate((-3.0, 3.0)):
            parent = empty(f"BX{yi + 1}{bay + 1} · beam animation", beam_collection)
            obj = cube(f"BX{yi + 1}{bay + 1} · longitudinal beam", (x, y, PAD_TOP + BEAM_HEIGHT / 2), (5.56, 0.38, BEAM_HEIGHT), concrete, beam_collection, bevel=0.018, parent=parent)
            if yi == 0 and bay == 1:
                selected = (parent, obj)
            else:
                start = 246 + schedule_index * 17
                assembly_motion(parent, [obj], start, start + 38, lift=4.2)
                schedule_index += 1
            beam_parts.append(obj)

    parent, obj = selected
    # The final beam remains separated for the macro shot, then seats without bounce.
    for frame, pos in ((1, (0, 0, 0)), (90, (0, 0, 0)), (91, (0, 0, 0.85)), (391, (0, 0, 0.85)), (440, (0, 0, 0.85)), (513, (0, 0, 0)), (900, (0, 0, 0))):
        key(parent, "location", pos, frame)
    interpolation(parent)
    visible_schedule([obj], [(1, True), (90, True), (91, False), (390, False), (391, True), (900, True)])

    slab_collection = groups["04 Hollow-core slabs"]
    template = make_slab_template(concrete, slab_collection)
    slab_objects = []
    for bay, x in enumerate((-3.07, 3.07)):
        for row in range(5):
            index = bay * 5 + row
            slab = template.copy()
            slab.name = f"S{index + 1:02d} · hollow-core roof slab"
            slab_collection.objects.link(slab)
            slab.location = (x, (row - 2) * 1.20, SLAB_BOTTOM + 0.125)
            parent = empty(f"S{index + 1:02d} · slab animation", slab_collection)
            slab.parent = parent
            start = 575 + index * 12
            assembly_motion(parent, [slab], start, start + 37, lift=4.2)
            slab_objects.append(slab)
    bpy.data.objects.remove(template, do_unlink=True)

    brace_collection = groups["05 Temporary braces"]
    for parent, parts, start, finish, x, y in col_roots:
        directions = [(0, -1 if y < 0 else 1)]
        if x != 0:
            directions.append((-1 if x < 0 else 1, 0))
        for dx, dy in directions:
            tag = parent.name.split(" · ")[0]
            axis = ("X+" if dx > 0 else "X-") if dx else ("Y+" if dy > 0 else "Y-")
            build_brace(f"B-{tag}-{axis}", x, y, (dx, dy), parent, parts, finish,
                        foundation, steel, hardware, padmat, groups["01 Foundations"], brace_collection)
        assembly_motion(parent, parts, start, finish, lift=5.3)

    guide_collection = groups["06 Connection guides"]
    # Four small edges clarify the otherwise dark bearing pad during the detail shot.
    pad = pads_by_key[(6.0, -3.0, -1, 0)]
    px, py, pz = pad.location
    guide_objects = []
    for dy in (-0.173, 0.173):
        guide_objects.append(cube("Bearing-pad outline", (px, py + dy, pz + 0.014), (0.45, 0.012, 0.013), orange, guide_collection, bevel=0.003))
    for dx in (-0.223, 0.223):
        guide_objects.append(cube("Bearing-pad outline", (px + dx, py, pz + 0.014), (0.012, 0.35, 0.013), orange, guide_collection, bevel=0.003))
    visible_schedule(guide_objects, [(1, False), (390, False), (391, True), (506, True), (507, False), (900, False)])

    world = bpy.data.worlds.new("Soft neutral studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.78, 0.83, 0.88, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    scene.world = world
    light("Large key softbox", (1, -6, 12), 2400, 8, (1.0, 0.94, 0.84), studio)
    light("Cool fill softbox", (-8, -1, 8), 1600, 7, (0.83, 0.91, 1.0), studio)
    light("Top rim softbox", (5, 7, 11), 2600, 7, (1.0, 0.98, 0.93), studio)

    cams = groups["08 Cameras"]
    hero = camera("CAM 01 · overview", scene, cams, 1, 90, ((18, -22, 13), (20, -20.3, 12.6)), (0, 0, 0.20), 42)
    wide = camera("CAM 02 · assembly", scene, cams, 91, 750, ((18.8, -23.3, 14.2), (19.4, -22.6, 13.8)), (0, 0, 0.25), 43)
    detail = camera("CAM 03 · bearing detail", scene, cams, 391, 570, ((2.20, -7.7, 5.85), (2.55, -7.4, 5.55)), (5.48, -3.0, 3.64), 51)
    final = camera("CAM 04 · positioning study", scene, cams, 751, 840, ((19.4, -21.8, 12.6), (22.0, -19.0, 12.2)), (0, 0, 0.20), 42)
    scene.camera = hero
    cuts = [(1, hero), (91, wide), (391, detail), (571, wide), (751, final)]
    for frame, cam in cuts:
        marker = scene.timeline_markers.new(cam.name, frame=frame)
        marker.camera = cam
    for cam, frames in ((hero, (1, 90)), (wide, (91, 750)), (final, (751, 840))):
        fit_wide_camera(scene, cam, frames)
    scene["concept_notice"] = "Generic visualization only. Client drawings and engineering determine final erection and connections."
    scene["component_counts"] = "6 columns / 7 beams / 10 hollow-core slabs"
    scene["revision"] = "v2 · architecture-reviewed positioning concept"
    scene["support_details"] = "Illustrative embedded anchor footings and fittings; no structural capacity verification"
    scene.frame_set(1)
    return scene, root, cuts


def effect(editor, name, kind, channel, start, end):
    return editor.strips.new_effect(name=name, type=kind, channel=channel, frame_start=start, length=end - start + 1)


def text(editor, name, content, font, size, x, y, channel, start=1, end=900, color="233D3D", align="LEFT"):
    strip = effect(editor, name, "TEXT", channel, start, end)
    strip.text, strip.font, strip.font_size = content, font, size
    strip.color = (*srgb(color), 1)
    strip.location = (x, y)
    strip.anchor_x = align
    strip.anchor_y = "CENTER"
    strip.alignment_x = align
    strip.use_shadow = False
    strip.blend_type = "ALPHA_OVER"
    return strip


def rect(editor, name, x, y, width, height, channel, resolution, start=1, end=900, color="F5F6F1", opacity=1):
    strip = effect(editor, name, "COLOR", channel, start, end)
    strip.color = srgb(color)
    strip.blend_type = "ALPHA_OVER"
    strip.blend_alpha = opacity
    strip.transform.scale_x = width
    strip.transform.scale_y = height
    strip.transform.offset_x = (x - 0.5) * resolution[0]
    strip.transform.offset_y = (y - 0.5) * resolution[1]
    return strip


def make_edit(source, root, cuts, assets, width, height, samples):
    edit = bpy.data.scenes.new("FinalEdit")
    setup_scene(edit, width, height, samples)
    edit.collection.children.link(root)
    edit.world = source.world
    edit.camera = cuts[0][1]
    for frame, cam in cuts:
        edit.timeline_markers.new(cam.name, frame=frame).camera = cam
    edit.render.use_sequencer = True
    edit.view_settings.view_transform = "AgX"
    editor = edit.sequence_editor_create()
    strip = editor.strips.new_scene("Procedural assembly · 900 frames", source, channel=1, frame_start=1)
    strip.scene_input = "CAMERA"
    regular = bpy.data.fonts.load(str(assets / "Pretendard-Regular.ttf"))
    bold = bpy.data.fonts.load(str(assets / "Pretendard-SemiBold.ttf"))
    scale = height / 1080
    res = (width, height)

    # The graphic layer stays native and editable in Blender's Video Sequencer.
    rect(editor, "Caption panel", 0.5, 0.095, 1.0, 0.19, 2, res, color="F5F6F1")
    rect(editor, "Header panel", 0.5, 0.957, 1.0, 0.086, 3, res, color="F5F6F1")
    rect(editor, "Header rule", 0.5, 0.914, 0.89, 0.0012, 4, res, color="CCD3CD")
    text(editor, "Studio wordmark", "KIMCHISTAN STUDIO", bold, 22 * scale, 0.055, 0.954, 5)
    text(editor, "Concept disclosure", "프리캐스트 조립 시각화 · 콘셉트 샘플", regular, 19 * scale, 0.945, 0.954, 6, align="RIGHT", color="62716D")
    rect(editor, "Wordmark accent", 0.048, 0.954, 0.003, 0.022, 7, res, color="D64C2F")

    # Six progress segments and a quiet editorial metadata line.
    for i, (start, end, number, title, subtitle, english) in enumerate(SHOTS):
        text(editor, f"Shot {i} · index", number, bold, (23 if number == "DETAIL" else 42) * scale, 0.055, 0.128, 10, start, end, color="D64C2F")
        text(editor, f"Shot {i} · heading", title, bold, 39 * scale, 0.145, 0.13, 11, start, end)
        text(editor, f"Shot {i} · explanation", subtitle, regular, 23 * scale, 0.146, 0.082, 12, start, end, color="62716D")
        text(editor, f"Shot {i} · English marker", english, bold, 15 * scale, 0.945, 0.040, 13, start, end, color="62716D", align="RIGHT")
        for j in range(6):
            rect(editor, f"Shot {i} · progress {j}", 0.066 + j * 0.025, 0.032, 0.018, 0.004, 14 + j, res, start, end, "D64C2F" if j == i else "CDD4CE")
    # Small information chips keep the bearing close-up focused on one relationship.
    text(editor, "Detail · element labels", "COLUMN  /  BEARING PAD  /  BEAM", bold, 16 * scale, 0.055, 0.867, 22, 391, 570, color="62716D")
    text(editor, "Detail · motion cue", "정렬", bold, 26 * scale, 0.945, 0.847, 23, 391, 440, color="D64C2F", align="RIGHT")
    text(editor, "Detail · seating cue", "안착", bold, 26 * scale, 0.945, 0.847, 23, 441, 570, color="D64C2F", align="RIGHT")
    edit.frame_set(1)
    bpy.context.window.scene = edit
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
    return edit


def write_docs(output, args, width, height):
    manifest = {
        "title": "Precast Component Positioning Study",
        "revision": "v2 · architecture-review corrections",
        "duration_seconds": 30,
        "fps": FPS,
        "frame_start": 1,
        "frame_end": FRAME_END,
        "blender": bpy.app.version_string,
        "model": {"columns": 6, "beams": 7, "hollow_core_slabs": 10, "bays": 2, "grid_metres": [6, 6]},
        "geometry": "Original procedural geometry built with bpy; no imported model assets",
        "audio": "Silent; native Korean caption strips",
        "notice": "Generic braced component-positioning study; permanent connections and grouting are omitted",
        "engineering_validation": False,
        "supports": {"brace_assemblies": 10, "kept_in_opening_and_closing": True,
                     "anchor_footings": "Illustrative 0.70 m square bodies embedded in the represented ground",
                     "anchor_design_verified": False},
        "shots": [{"start": a, "end": b, "heading": t, "explanation": sub} for a, b, n, t, sub, eng in SHOTS],
        "outputs": ["precast-assembly-30s-4k.mp4", "precast-assembly-30s-1080p.mp4", "thumbnail.png", "precast-assembly.blend"],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (output / "README.md").write_text('''# Precast Component Positioning Study — v2

30-second silent Korean-captioned component-positioning concept sample.
All geometry, materials, animation, cameras and caption strips are generated with
Blender's Python API. No client or third-party model assets are used.

## Files

- `precast-assembly-30s-4k.mp4`: native 3840 x 2160, 30 fps, H.264 MP4.
- `precast-assembly-30s-1080p.mp4`: 1920 x 1080 presentation version.
- `thumbnail.png`: opening composition at 4K.
- `precast-assembly.blend`: editable 3D scene and native Video Sequencer captions.
- `source/kmong_227330.py`: generator and render/encoding entry point.
- `source/audit_kmong_227330.py`: native geometry, visibility and caption checks.
- `assets/`: Pretendard fonts and their SIL Open Font License.
- `manifest.json`: timing and component inventory.
- `source-audit.json` and `qa-report.json`: geometry/media verification results.

## Architecture-review revision

All ten temporary braces are visible in the opening overview and remain installed
through the closing positioning state. Their plates contact embedded anchor-footing
caps, with illustrative fasteners, receiver plates, clevises and pins. Receiver plates
travel with the columns; removable brace hardware appears after column placement.
The footing bodies extend below the represented ground, rather than resting as loose
blocks on the display base. Their proportions do not specify a structural anchor design.

The captions identify omitted column-base connections, permanent beam connections,
and slab joint/grouting operations. The closing state is "구조부재 배치 완료" and
"POSITIONING STUDY", with the braces retained.

## Open and edit

Use Blender 5.2 or newer. `FinalEdit` contains the final composited sequence;
`Assembly` contains the underlying 3D scene. Both expose the same model for editing.
The numbered collections organize foundations, columns, beams, slabs, temporary
braces, guides, lighting and cameras. Captions remain editable text strips.
Fonts are packed into the blend and also supplied separately.
Rendering `FinalEdit` directly from the blend writes PNGs to its relative
`renders/` directory; the generator uses a separate work directory instead.

## Regenerate

From this directory, with Blender and FFmpeg installed:

```sh
"/Applications/Blender.app/Contents/MacOS/Blender" --background --factory-startup --python source/kmong_227330.py -- --mode build
"/Applications/Blender.app/Contents/MacOS/Blender" --background --factory-startup --python source/kmong_227330.py -- --mode preview
"/Applications/Blender.app/Contents/MacOS/Blender" --background --factory-startup --python source/kmong_227330.py -- --mode final
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python-exit-code 1 --python source/audit_kmong_227330.py -- precast-assembly.blend
```

Replace the Blender executable path on other operating systems. `--font-dir`,
`--output` and `--work-dir` can be supplied explicitly. Final mode resumes existing
PNG frames; remove only frames you intend to replace after an animation change.
Use `--start` and `--end` with `--skip-encode` for a partial rerender.
Stills mode accepts `--frames 45,210,350,430,525,690,840`.
It also renders a separate anchor-detail image for geometry review.
The final preset renders native 4K with 32 temporal samples and a 2 GB shadow
pool. `--samples 64` is available for a slower supersampled render.

## Concept limits

This is a representative two-bay positioning study. Geometry proportions,
temporary supports, illustrative anchorage and bearing-pad seating explain visual
relationships. Permanent connections, structural fixity, joint filling and curing
are outside the sample. The commissioned film must follow the client's actual
models, connection details and approved sequence. Geometry/media audits do not
verify structural capacity, anchorage design or an erection method.

No sound track or external contact details are included.
''')


def encode(frames_dir, output):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required for MP4 encoding")
    missing = [f for f in range(1, 901) if not (frames_dir / f"frame_{f:04d}.png").exists()]
    if missing:
        raise RuntimeError(f"Cannot encode: {len(missing)} frames missing, first: {missing[:8]}")
    master = output / "precast-assembly-30s-4k.mp4"
    common = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-an"]
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "warning", "-y", "-framerate", "30", "-start_number", "1", "-i", str(frames_dir / "frame_%04d.png"), "-frames:v", "900", "-vf", "scale=out_color_matrix=bt709:out_range=tv", *common, str(master)], check=True)
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "warning", "-y", "-i", str(master), "-vf", "scale=1920:1080:flags=lanczos:in_color_matrix=bt709:out_color_matrix=bt709", *common, str(output / "precast-assembly-30s-1080p.mp4")], check=True)
    shutil.copy2(frames_dir / "frame_0045.png", output / "thumbnail.png")
    verify_videos(output)


def verify_videos(output):
    """Check actual encoded streams, and detect caption dropouts in every frame."""
    report = {"status": "passed", "videos": []}
    for filename, size in (("precast-assembly-30s-4k.mp4", (3840, 2160)), ("precast-assembly-30s-1080p.mp4", (1920, 1080))):
        path = output / filename
        probe = subprocess.run([shutil.which("ffprobe"), "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path)], check=True, capture_output=True, text=True)
        data = json.loads(probe.stdout)
        streams = data["streams"]
        video = next(s for s in streams if s["codec_type"] == "video")
        assert (video["width"], video["height"]) == size, f"Wrong dimensions: {filename}"
        assert video["avg_frame_rate"] == "30/1", f"Wrong frame rate: {filename}"
        assert int(video["nb_read_frames"]) == 900, f"Wrong frame count: {filename}"
        assert abs(float(data["format"]["duration"]) - 30) < 0.001, f"Wrong duration: {filename}"
        assert video["codec_name"] == "h264" and video["pix_fmt"] == "yuv420p"
        assert not any(s["codec_type"] == "audio" for s in streams)
        # Caption area contains dark Korean glyphs on a light solid panel. This
        # catches a missing overlay even when the rendered 3D image is valid.
        decode = subprocess.run([shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-i", str(path), "-vf", "scale=960:540,crop=640:50:130:450,format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"], check=True, capture_output=True)
        assert not decode.stderr.strip(), f"Decode errors: {filename}"
        pixels_per_frame = 640 * 50
        assert len(decode.stdout) == pixels_per_frame * 900
        counts = [sum(v < 80 for v in decode.stdout[i:i + pixels_per_frame]) for i in range(0, len(decode.stdout), pixels_per_frame)]
        assert min(counts) > 100, f"Caption dropout detected: {filename}"
        assert max(counts) < pixels_per_frame * 0.70, f"Black caption region detected: {filename}"
        report["videos"].append({"file": filename, "width": video["width"], "height": video["height"], "frames": 900, "fps": 30, "duration_seconds": 30, "codec": "H.264", "pixel_format": video["pix_fmt"], "audio_streams": 0, "decode_errors": 0, "caption_frames_checked": 900, "minimum_caption_dark_pixels": min(counts)})
    (output / "qa-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("VIDEO_QA_PASSED", json.dumps(report))


def main():
    args = arguments()
    output, assets = prepare_assets(args)
    args.work_dir = args.work_dir.resolve()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    final = args.mode in ("build", "final")
    width, height = (3840, 2160) if final else (1920, 1080) if args.mode == "stills" else (960, 540)
    samples = args.samples or (32 if final or args.mode == "stills" else 16)
    source, root, cuts = build_model(args, width, height, samples)
    edit = make_edit(source, root, cuts, assets, width, height, samples)
    source.render.filepath = "//renders/assembly_"
    edit.render.filepath = "//renders/frame_"
    write_docs(output, args, width, height)
    bpy.ops.file.pack_all()
    # Avoid version backup files in the delivery folder on iterative builds.
    bpy.context.preferences.filepaths.save_version = 0
    if final:
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "precast-assembly.blend"))
    if args.mode == "build":
        print("BUILD_COMPLETE", json.dumps({"objects": len(bpy.data.objects), "output": str(output)}))
        return
    if args.mode == "stills":
        frames = [int(f) for f in args.frames.split(",")] if args.frames else [45, 210, 350, 420, 475, 525, 690, 840]
        target = args.work_dir / "stills"
        target.mkdir(exist_ok=True)
        for frame in frames:
            edit.frame_set(frame)
            edit.render.filepath = str(target / f"frame_{frame:04d}.png")
            bpy.ops.render.render(write_still=True)
        # QA-only camera override; it never changes the saved movie shot list.
        qa = camera("QA · illustrative anchor detail", source,
                    bpy.data.collections["08 Cameras"], 240, 241,
                    ((8.8, -4.6, 1.4), (8.8, -4.6, 1.4)), (7.3, -3.0, 0.14), 60)
        source_strip = next(s for s in edit.sequence_editor.strips if s.type == "SCENE")
        source_strip.scene_camera = qa
        edit.frame_set(240)
        edit.render.filepath = str(target / "anchor-detail.png")
        bpy.ops.render.render(write_still=True)
        source_strip.scene_camera = None
        print("STILLS_COMPLETE", str(target))
        return
    target = args.work_dir / ("frames-4k" if args.mode == "final" else "frames-preview")
    target.mkdir(exist_ok=True)
    edit.frame_start, edit.frame_end = args.start, args.end
    edit.render.filepath = str(target / "frame_")
    edit.render.use_overwrite = False
    before = time.perf_counter()
    bpy.ops.render.render(animation=True)
    print("RENDER_SECONDS", round(time.perf_counter() - before, 2))
    if args.mode == "final" and not args.skip_encode:
        encode(target, output)
    elif args.mode == "preview" and not args.skip_encode:
        subprocess.run([shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "warning", "-y", "-framerate", "30", "-start_number", str(args.start), "-i", str(target / "frame_%04d.png"), "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.work_dir / "preview.mp4")], check=True)
    print("COMPLETE", args.mode, str(output))


if __name__ == "__main__":
    main()
