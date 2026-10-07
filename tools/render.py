"""Render pictures of the plate with the fans and joiners, for the README.

Needs pyvista in the venv. All meshes come from tools/render_meshes.py (preview/render/), which tessellates
the fans, the plate and the joiner far finer than the printable STLs. Writes to renders/.

Usage: python tools/render.py
"""
import os, numpy as np, pyvista as pv
from PIL import Image
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(HERE, "renders"); os.makedirs(OUT, exist_ok=True)
pv.OFF_SCREEN = True

# layout, as in fan_plate.py
PLATE_T, FAN_OFF_Y, FAN_T = 3.0, -0.75, 25.0
SUPERSAMPLE = 2   # stills are rendered this many times larger and scaled down, on top of VTK's own anti-aliasing
FANS = [(-105.9, "nf-a12x25"), (1.0, "nf-a9"), (107.9, "nf-a12x25")]
X92 = 1.0

PLASTIC = dict(color="#5a5a5a", specular=0.04, specular_power=8)   # matte dark grey: light enough that the plate's features still read
FRAME   = dict(color="#e7ceb4", specular=0.03, specular_power=8)   # Noctua beige, matte
ROTOR   = dict(color="#653025", specular=0.03, specular_power=8)   # Noctua brown, matte

def mesh(path):
    m = pv.read(os.path.join(HERE, path)).clean()
    return m.compute_normals(split_vertices=True, feature_angle=40)

def assembly(explode=0.0):
    """Returns [(mesh, style)] in the plate's design frame: Z = 0 fin tops, fans on +Z."""
    parts = []
    parts.append((mesh("preview/render/plate.stl"), PLASTIC))
    for fx, name in FANS:
        for kind, style in (("frame", FRAME), ("rotor", ROTOR)):
            parts.append((mesh(f"preview/render/{name}_{kind}.stl").translate((fx, FAN_OFF_Y, PLATE_T + explode)), style))
        if name == "nf-a12x25":   # rubber pads only on the two outer corners, away from the joiner
            pads = mesh("preview/render/nf-a12x25_pads.stl")
            outer = 1 if fx > X92 else -1
            pads = pads.clip(normal=(outer, 0, 0), origin=(0, 0, 0), invert=False)
            parts.append((pads.translate((fx, FAN_OFF_Y, PLATE_T + explode)), ROTOR))
    z = PLATE_T + FAN_T + 2*explode
    for sgn in (1, -1):   # joiner on each long edge; its local X points at the card's edge, Y along the row
        j = mesh("preview/render/joiner.stl").rotate_z(-90 if sgn > 0 else 90).translate((X92, FAN_OFF_Y, z))
        parts.append((j, PLASTIC))
    return parts

# Classic (Phong) shading on purpose: VTK's PBR material has no environment map here and renders every colour grey.
def scene(parts, size=(1800, 1100)):
    p = pv.Plotter(off_screen=True, window_size=size, lighting="none")
    p.set_background("white")   # the screenshots are saved with a transparent background
    for m, style in parts:
        p.add_mesh(m, smooth_shading=True, ambient=0.3, diffuse=1.0, **style)
    # Two soft lights and a fair amount of ambient: light colours stay their colour instead of clipping to white,
    # and the shadows keep their hue. Stronger key/fill/rim setups made the beige frames look washed out.
    p.add_light(pv.Light(position=(-0.3, -0.6, 3.0), focal_point=(0, 0, 0), intensity=0.55, light_type="camera light"))  # key, high and slightly to the front
    p.add_light(pv.Light(position=(1.5, 1.0, 1.0), focal_point=(0, 0, 0), intensity=0.3, light_type="camera light"))     # fill from the other side
    p.add_light(pv.Light(position=(0, 0, 600), focal_point=(0, 0, 0), intensity=0.15, light_type="scene light"))        # soft top light, fixed above the plate (does not turn with the camera)
    p.enable_anti_aliasing("ssaa")
    p.enable_ssao(radius=5.0, bias=0.45, kernel_size=256, blur=True)   # much larger and the frames go grey
    return p

def look(p, direction, up=(0, 0, 1), zoom=1.0):
    p.camera_position = "iso"
    p.view_vector(direction, viewup=up)
    p.reset_camera(); p.camera.zoom(zoom)

def save(p, name, size=(1800, 1100)):
    """Screenshot with a transparent background at SUPERSAMPLE times the size, then scale down with a Lanczos filter."""
    img = Image.fromarray(p.screenshot(return_img=True, transparent_background=True))
    img.resize(size, Image.LANCZOS).save(f"{OUT}/{name}.png", optimize=True)
    p.close()

def stills(size=(1800, 1100)):
    big = (size[0]*SUPERSAMPLE, size[1]*SUPERSAMPLE)
    parts = assembly()
    p = scene(parts, big); look(p, (-0.55, -1.0, 0.75), zoom=1.45); save(p, "hero", size)
    p = scene(parts, big); look(p, (0.55, 1.0, -0.75), up=(0, 0, -1), zoom=1.45); save(p, "underside", size)
    p = scene(assembly(explode=45.0), big); look(p, (-0.55, -1.0, 0.6), zoom=1.3); save(p, "exploded", size)
    print("stills written")

if __name__ == "__main__":
    stills()
