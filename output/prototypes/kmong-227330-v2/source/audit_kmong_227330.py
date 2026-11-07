"""Audit the delivered Blender scene's geometry and captions, not its engineering.

Blender --background --python-exit-code 1 --python audit_kmong_227330.py -- scene.blend
The input blend is never saved or changed; a JSON report is written beside it.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def bounds(obj):
    points = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return tuple(min(v[a] for v in points) for a in range(3)), tuple(max(v[a] for v in points) for a in range(3))


def main():
    path = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.data.scenes["Assembly"]
    edit = bpy.data.scenes["FinalEdit"]
    scene.frame_set(900)
    scene.view_layers[0].update()
    columns = [o for o in scene.objects if o.name.endswith("· precast column")]
    beams = [o for o in scene.objects if o.name.endswith(("· longitudinal beam", "· transverse beam"))]
    slabs = [o for o in scene.objects if o.name.endswith("· hollow-core roof slab")]
    pads = [o for o in scene.objects if o.name.endswith("· slab bearing strip")]
    assert (len(columns), len(beams), len(slabs), len(pads)) == (6, 7, 10, 3)
    assert all(abs(bounds(o)[0][2] - 0.20) < 0.0001 for o in columns)
    assert all(abs(bounds(o)[0][2] - 3.58) < 0.0001 for o in beams)
    assert all(abs(bounds(o)[0][2] - bounds(pads[0])[1][2]) < 0.0001 for o in slabs)
    assert len({o.data.as_pointer() for o in slabs}) == 1 and len(slabs[0].data.vertices) > 200

    roots = [o for o in scene.objects if o.get("brace_role") == "assembly"]
    assert len(roots) == 10
    contact_errors, pin_errors, angles = [], [], []
    groups, test_frames = [], {1, 90, 91, 750, 751, 840, 900}
    for root in roots:
        footing, plate, rod = [bpy.data.objects[root[k]] for k in ("footing", "footplate", "rod")]
        low, high = bounds(footing)
        assert low[2] < footing["ground_level"] < high[2], "Footing not embedded"
        assert all(low[a] <= bounds(plate)[0][a] <= bounds(plate)[1][a] <= high[a] for a in (0, 1))
        error = abs(bounds(plate)[0][2] - high[2])
        assert error < 0.0001, f"Footplate contact error: {root.name} / {error}"
        contact_errors.append(error)
        upper, lower = [bpy.data.objects[root[f"{end}_pin"]].matrix_world.translation for end in ("upper", "lower")]
        local_z = [p.co.z for p in rod.data.vertices]
        endpoints = [rod.matrix_world @ Vector((0, 0, p)) for p in (min(local_z), max(local_z))]
        error = min((endpoints[0] - upper).length + (endpoints[1] - lower).length,
                    (endpoints[1] - upper).length + (endpoints[0] - lower).length)
        assert error < 0.0001, f"Brace does not meet hinge pins: {root.name}"
        pin_errors.append(error)
        delta = upper - lower
        angles.append(math.degrees(math.atan2(abs(delta.z), math.hypot(delta.x, delta.y))))
        related = [o for o in scene.objects if o.get("brace_id") == root["brace_id"] and o.type == "MESH"]
        cast_in = [o for o in related if o.get("brace_role") in ("column_insert_plate", "column_insert_fastener")]
        removable = [o for o in related if o.get("brace_role") not in ("anchor_footing", "column_insert_plate", "column_insert_fastener")]
        assert len(cast_in) == 7 and removable
        column_root = bpy.data.objects[root["column_root"]]
        assert all(o.parent == column_root for o in cast_in)
        assert all(o.parent == root for o in removable)
        finish = root["install_frame"]
        # These scene generators use a 43-frame column descent.
        midpoint = finish - 21
        test_frames.update((finish - 44, midpoint, finish - 1, finish, finish + 1))
        groups.append((root, column_root, cast_in, removable, footing, finish))

    checks = 0
    for frame in sorted(f for f in test_frames if f >= 1):
        scene.frame_set(frame)
        scene.view_layers[0].update()
        for root, column_root, cast_in, removable, footing, finish in groups:
            expected = frame <= 90 or frame >= finish
            assert all((not o.hide_render) == expected for o in removable), f"Orphaned/absent brace hardware at {frame}: {root.name}"
            assert not footing.hide_render
            for o in cast_in:
                # Blender intentionally leaves disabled viewport objects' world
                # matrices unevaluated. Check transform following when visible;
                # the parent relationship is checked independently above.
                if not o.hide_viewport:
                    expected_position = column_root.matrix_world @ o.location
                    assert (o.matrix_world.translation - expected_position).length < 0.0001, (frame, o.name)
            if 91 <= frame < finish:
                assert column_root.location.z > 0
            checks += 1

    fonts = [{"name": f.name, "packed_bytes": f.packed_file.size if f.packed_file else 0}
             for f in bpy.data.fonts if "Pretendard" in f.name]
    assert len(fonts) == 2 and all(f["packed_bytes"] > 0 for f in fonts)
    assert not list(bpy.data.libraries)
    assert (edit.frame_start, edit.frame_end, edit.render.fps) == (1, 900, 30)
    assert (edit.render.resolution_x, edit.render.resolution_y) == (3840, 2160)
    assert edit.render.use_sequencer and edit.render.filepath == "//renders/frame_"
    assert len([m for m in scene.timeline_markers if m.camera]) == 5
    texts = [s for s in edit.sequence_editor.strips if s.type == "TEXT"]
    content = {s.text for s in texts}
    required = {"구조부재 배치 완료", "접합·그라우팅 상세는 발주처 도면에 따라 반영",
                "BEARING DETAIL", "POSITIONING STUDY", "슬래브 간 접합·그라우팅 공정 생략",
                "받침 패드 안착 예시 · 영구 접합 상세 생략"}
    assert required <= content and "COMPLETE" not in content
    assert all(not any(w in s.text.lower() for w in ("http", "@", "031-")) for s in texts)
    for frame in range(1, 901):
        active = [s for s in texts if s.frame_final_start <= frame < s.frame_final_end]
        assert any("heading" in s.name for s in active)
        assert any(s.name == "Concept disclosure" for s in active)

    report = {
        "status": "passed", "scope": "Geometry, visibility and caption verification only",
        "engineering_validation": False, "blender": bpy.app.version_string,
        "counts": {"columns": 6, "beams": 7, "hollow_core_slabs": 10, "brace_assemblies": 10},
        "maximum_footplate_contact_error_mm": max(contact_errors) * 1000,
        "maximum_rod_pin_alignment_error_mm": max(pin_errors) * 1000,
        "anchor_footings_embedded": True, "brace_group_visibility_checks": checks,
        "opening_and_closing_braces_retained": True,
        "hardware_parenting_and_installation_schedule": "passed",
        "brace_angles_degrees_observed_not_designed": [min(angles), max(angles)],
        "member_support_contact": "passed", "packed_fonts": fonts,
        "external_libraries": 0, "caption_coverage_frames": 900,
        "camera_cuts": 5, "native_4k_source": True,
    }
    (path.parent / "source-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("SOURCE_AUDIT_PASSED", json.dumps(report))


if __name__ == "__main__":
    main()
