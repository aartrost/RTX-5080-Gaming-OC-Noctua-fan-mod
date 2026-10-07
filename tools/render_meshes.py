"""Tessellate everything the renders need, much finer than the printable STLs, into preview/render/.

- The two Noctua fans from reference/, each as a frame and a rotor mesh, in one frame: fan axis along Z,
  exhaust face (motor struts) at Z = 0, intake at Z = 25, centred on the axis. The rubber corner pads on the
  plate side are left out (they are removed on the real fans); the 120 mm fans keep the four on the intake side.
- The plate, from models/5080-gaming-oc-fan-plate_full.step.
- The joiner, straight from joiner.py.

The printable STLs in models/ are tessellated for printing (0.02 mm) and show visible facets in a close-up
render; these meshes use a much tighter tolerance and are only for pictures. Run once, then tools/render.py.
"""
import cadquery as cq, os, sys
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(HERE, "preview", "render"); os.makedirs(OUT, exist_ok=True)
FINE   = (0.004, 0.03)   # linear and angular tolerance: plate and joiner (small meshes, big flat circles that facet visibly)
FAN    = (0.01, 0.06)    # the fans: Noctua's CAD is dense already; finer than this costs hundreds of MB for no visible gain

def export(name, shape, tol=FINE):
    cq.exporters.export(cq.Workplane().add(shape), os.path.join(OUT, name + ".stl"), tolerance=tol[0], angularTolerance=tol[1])
    bb = shape.BoundingBox(); print("%-18s x %6.1f..%5.1f  y %6.1f..%5.1f  z %5.1f..%5.1f" % (name, bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))

def solids(path):
    return sorted(cq.importers.importStep(os.path.join(HERE, path)).solids().vals(), key=lambda v: v.Volume(), reverse=True)

# NF-A12x25: axis Y, exhaust face at y = 0, intake at y = 25, already centred. Pads are the eight ~1014 mm3 solids.
sols = solids("reference/NF-A12x25_Public-CAD.stp")
frame, rotor, rest = sols[0], sols[1], [v for v in sols[2:] if not 900 < v.Volume() < 1200]
pads = [v for v in sols[2:] if 900 < v.Volume() < 1200 and v.BoundingBox().ymax > 25]   # the four on the intake face
fix = lambda v: v.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)          # y -> z
export("nf-a12x25_frame", fix(frame), FAN)
export("nf-a12x25_rotor", cq.Compound.makeCompound([fix(v) for v in [rotor] + rest]), FAN)
export("nf-a12x25_pads", cq.Compound.makeCompound([fix(v) for v in pads]), FAN)

# NF-A9: axis X, exhaust face (struts) at x = 6, intake at x = -19, centred at y 94.85, z -0.05. Pads are the ~555 mm3 solids.
sols = solids("reference/NF-A9_Public-Cad.stp")
frame, rotor, rest = sols[0], sols[1], [v for v in sols[2:] if not 500 < v.Volume() < 600]
fix = lambda v: v.translate(cq.Vector(-6, -94.85, 0.05)).rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 90)   # x -> -z, so -x (intake) -> +z
export("nf-a9_frame", fix(frame), FAN)
export("nf-a9_rotor", cq.Compound.makeCompound([fix(v) for v in [rotor] + rest]), FAN)

# The plate, in its design frame (Z = 0 fin tops, fans on +Z), and the joiner in its own frame.
export("plate", solids("models/5080-gaming-oc-fan-plate_full.step")[0])
sys.path.insert(0, HERE)
from joiner import make_joiner
F120 = dict(size=120.0, pitch=105.0); F92 = dict(size=92.0, pitch=82.5); FAN_GAP = 0.9   # as in fan_plate.py
fans, x = [], 0.0
for f in (F120, F92, F120):
    fans.append((x + f["size"]/2, f)); x += f["size"] + FAN_GAP
export("joiner", make_joiner(fans)[0].val())
