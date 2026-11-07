# Precast Component Positioning Study — v2

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
