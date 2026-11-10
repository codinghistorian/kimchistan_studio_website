"""Read-only source audit; writes a report beside the delivered blend."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

path = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(path))
assembly = bpy.data.scenes["Assembly"]
edit = bpy.data.scenes["FinalEdit"]
assembly.frame_set(900)
assembly.view_layers[0].update()

columns = [o for o in assembly.objects if o.name.endswith("· precast column")]
beams = [o for o in assembly.objects if o.name.endswith(("· longitudinal beam", "· transverse beam"))]
slabs = [o for o in assembly.objects if o.name.endswith("· hollow-core roof slab")]
slab_pads = [o for o in assembly.objects if o.name.endswith("· slab bearing strip")]
assert (len(columns), len(beams), len(slabs)) == (6, 7, 10)
assert len(slab_pads) == 3
assert len({o.data.as_pointer() for o in slabs}) == 1
assert len(slabs[0].data.vertices) > 200, "Hollow-core boolean geometry missing"

def bounds(obj):
    points = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return tuple(min(v[a] for v in points) for a in range(3)), tuple(max(v[a] for v in points) for a in range(3))

assert all(abs(bounds(o)[0][2] - 0.20) < 0.00001 for o in columns)
assert all(abs(bounds(o)[0][2] - 3.58) < 0.00001 for o in beams)
roof_pad_top = bounds(slab_pads[0])[1][2]
assert all(abs(bounds(o)[0][2] - roof_pad_top) < 0.00001 for o in slabs), "Slabs do not touch bearing strips"

font_info = []
for f in bpy.data.fonts:
    if "Pretendard" in f.name:
        assert f.packed_file and f.packed_file.size > 0
        font_info.append({"name": f.name, "packed_bytes": f.packed_file.size})
assert len(font_info) == 2
assert not list(bpy.data.libraries)
assert (edit.frame_start, edit.frame_end, edit.render.fps) == (1, 900, 30)
assert (edit.render.resolution_x, edit.render.resolution_y) == (3840, 2160)
assert edit.render.use_sequencer
assert edit.render.filepath == "//renders/frame_"
assert assembly.eevee.shadow_pool_size == "2048"
assert len([m for m in assembly.timeline_markers if m.camera]) == 5

texts = [s for s in edit.sequence_editor.strips if s.type == "TEXT"]
assert len(texts) == 29
assert all(not any(w in s.text.lower() for w in ("http", "@", "031-")) for s in texts)
for frame in range(1, 901):
    active = [s for s in texts if s.frame_final_start <= frame < s.frame_final_end]
    assert any("heading" in s.name for s in active), f"No heading at frame {frame}"
    assert any(s.name == "Concept disclosure" for s in active)

report = {
    "status": "passed",
    "blender": bpy.app.version_string,
    "counts": {"columns": len(columns), "beams": len(beams), "hollow_core_slabs": len(slabs)},
    "slab_mesh_shared": True,
    "slab_vertices": len(slabs[0].data.vertices),
    "columns_touch_foundations": True,
    "beams_at_bearing_pad_height": True,
    "slabs_touch_bearing_strips": True,
    "packed_fonts": font_info,
    "external_libraries": 0,
    "caption_coverage_frames": 900,
    "camera_cuts": 5,
    "native_4k_source": True,
    "shadow_pool_mb": 2048,
}
(path.parent / "source-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print("SOURCE_AUDIT_PASSED", json.dumps(report))
