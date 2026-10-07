"""
Joiner for the outer face of the fans on the deshrouded RTX 5080 fan plate.

A flat strip that screws across the outer face of the three fans along one long side of the card, using the
fans' own corner holes: the two 92 mm fan holes and the nearest corner hole of each 120 mm fan. It keeps the
fan row stiff and square. The part is symmetric end to end, so print two and turn one around for the other side.

Frame: X runs across the card with the outer edge of the fans at -X, Y runs along the fan row with the 92 mm fan
at Y = 0, Z = 0 is the face that touches the fans. The screws go in from the +Z face, which has the countersinks.
Export as is: the fan face is flat on the bed, no supports.

The outline follows the hand-made joiner from the original deshroud bracket (reference/joiner_original.stl);
the numbers below reproduce it. fan_plate.py imports make_joiner and passes its own fan layout, so the holes
always match the plate. Running this file on its own uses the defaults at the bottom.
"""
import cadquery as cq, os

T         = 3.5      # thickness
SPINE_W   = 4.0      # strip along the outer edge of the 120 mm fans, full length
PAD_REACH = 8.25     # body reaches this far past the 92 mm fan hole centres, toward the middle of the card
PAD_BACK  = 3.25     # the straight inner edge beside each 92 mm hole starts this far before the hole
MID_IN    = 2.0      # over the middle of the 92 mm fan the body stops this far inside the fan frame edge
MID_HALF  = 26.0     # half-length of that narrower middle section
END_PAST  = 16.6     # body ends this far past the outer (120 mm fan) holes
HOLE_D    = 4.7      # fan screw hole
CSK_D     = 8.7      # 90 degree countersink at the outer face, 2.0 deep
FILLET    = 1.0      # outer top edges
SLOT_W, SLOT_L, SLOT_WALL = 1.7, 4.0, 2.0   # three small slots along the outer edge (zip ties): width, length, wall left outside
SLOT_Y    = (-27.0, 0.0, 27.0)

def make_joiner(fans):
    """fans: [(x_along_row, spec), ...] for a big fan, the small middle fan, and a big fan, as in fan_plate.py.
    spec is a dict with "size" (frame) and "pitch" (screw spacing)."""
    (xa, fa), (xm, fm), (xb, fb) = fans
    edge     = -fa["size"]/2                     # outer edge of the big fans
    spine_in = edge + SPINE_W
    holes = [(-fa["pitch"]/2, xa - xm + fa["pitch"]/2),   # nearest corner hole of each 120 mm fan
             (-fb["pitch"]/2, xb - xm - fb["pitch"]/2),
             (-fm["pitch"]/2, -fm["pitch"]/2), (-fm["pitch"]/2, fm["pitch"]/2)]   # both outer holes of the 92 mm fan
    y_big = max(abs(y) for _, y in holes)
    y_mid = fm["pitch"]/2
    inner = -fm["pitch"]/2 + PAD_REACH            # inner edge beside the 92 mm holes
    mid_x = -fm["size"]/2 + MID_IN                # inner edge over the middle of the 92 mm fan
    end   = y_big + END_PAST
    diag  = inner - spine_in                      # 45 degree run from the spine out to the 92 mm pad
    half = [(mid_x, MID_HALF), (inner, y_mid - PAD_BACK), (inner, end - diag), (spine_in, end)]   # inner edge, middle to +Y end
    pts = [(edge, -end)] + [(x, -y) for x, y in reversed(half)] + half + [(edge, end)]
    body = cq.Workplane("XY").polyline(pts).close().extrude(T).edges(">Z").fillet(FILLET)
    body = body.faces(">Z").workplane(origin=(0, 0, T)).pushPoints(holes).cskHole(HOLE_D, CSK_D, 90)
    for y in SLOT_Y:
        body = body.cut(cq.Workplane("XY").center(edge + SLOT_WALL + SLOT_W/2, y).rect(SLOT_W, SLOT_L).extrude(T))
    return body, holes

def report(joiner, holes):
    s = joiner.val(); bb = s.BoundingBox()
    print("top joiner: valid=%s solids=%d  %.1f x %.1f x %.1f mm  %.2f cm3; outer holes %.2f mm from the 92 mm fan centre" % (
        s.isValid(), joiner.solids().size(), bb.xlen, bb.ylen, bb.zlen, s.Volume()/1000, max(abs(y) for _, y in holes)))

if __name__ == "__main__":
    # Defaults match fan_plate.py (Noctua NF-A12x25 and NF-A9 without pads, 0.9 mm between frames).
    F120 = dict(size=120.0, pitch=105.0); F92 = dict(size=92.0, pitch=82.5); FAN_GAP = 0.9
    fans, x = [], 0.0
    for f in (F120, F92, F120):
        fans.append((x + f["size"]/2, f)); x += f["size"] + FAN_GAP
    joiner, holes = make_joiner(fans)
    report(joiner, holes)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"); os.makedirs(out, exist_ok=True)
    cq.exporters.export(joiner, f"{out}/top_joiner.stl", tolerance=0.02, angularTolerance=0.1)
