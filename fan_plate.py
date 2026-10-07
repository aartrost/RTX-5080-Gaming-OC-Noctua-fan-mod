"""
Screw-on fan plate for deshrouded Gigabyte RTX 5080 Gaming OC
2x NF-A12x25 (120 mm) with 1x NF-A9 (92 mm) in the middle, rubber corner pads removed (25 mm thick).

Viewed from the fan side: -X = port end, +X = rear, +Y = "top" bar (318 mm), -Y = "bottom" bar (315 mm).
Z=0 sits on the fin tops, fans sit on Z=PLATE_T. A 1 mm ridge under each long edge rests on the rail.
Fans are screwed on from the underside with the standard Noctua fan screws (heads recessed).
Rail screws: four M2 screws dropped in from the fan side before the fans go on (heads sit in snug pockets
under the fan frames), with nuts tightened from under the rails.
Print fan side down (the STLs are already flipped), no supports.
"""
import cadquery as cq, os, math

# ---------- measured on the card ----------
FIN_L, FIN_W = 319.0, 121.0
RAIL_CC_Y    = 112.25
TOP_BAR, TOP_INSET = 318.0, 3.875
BOT_BAR, BOT_INSET = 315.0, 4.125     # both bars flush at the rear end
RAIL_STRETCH = 0.5                    # extra lengthwise hole spacing found with the paper template (split between both ends)
RAIL_DROP    = 0.75                   # rails sit this far below the fin tops
WIRE_START, WIRE_END, WIRE_DEPTH = 160.0, 124.0, 6.0   # edge cutout on the bottom bar: from the port hole, from the rear hole (shortened 4 mm at the rear end), in from the edge

FIN_GAP_START, FIN_GAP_W = 115.0, 21.0   # gap in the fin stack: distance from the port end of the heatsink (as checked against the printed slot), and its width
RAIL_W = 7.0                             # width of the metal bar at that gap

# ---------- screws ----------
M2_HEAD_D, M2_HEAD_H = 3.75, 2.0      # rail screws
FS_HEAD_D, FS_TAPER_H, FS_THREAD_D = 6.5, 1.5, 4.85   # standard fan screws (9.9 mm long)
FS_RECESS = 1.0                       # fan screw head sits this far below the underside

# ---------- design choices ----------
PLATE_T   = 3.0
FAN_GAP   = 0.9      # gap between fan frames: moves the rear fan back so its screws clear the rear rail screws
FAN_OFF_Y = -0.75    # whole fan row shifted toward the bottom bar: more room between screws at the top port corner
FAN_SHIFT = -6.4     # fan row starts 6.4 mm in FRONT of the heatsink's port end: fan corner screws sit just port-side of the rail screws
RAIL_HOLE_D = 2.4    # clearance hole for the M2 rail screws
HEAD_D, HEAD_DEPTH = 3.8, 2.2         # snug pocket for the 3.75 mm M2 heads, so they don't spin when the nut is tightened
PAD_D, PAD_H = 5.0, 1.0               # ridge: inner edge is PAD_D/2 inboard of the rail holes, outer edge is the plate edge; 5 layers at 0.2 mm
CORNER_R, NOTCH_R_IN, NOTCH_R_OUT = 3.0, 2.0, 1.5   # rounded corners: plate, inside of the wire cutout, mouth of the wire cutout
F92_FRAME_HALF = 45.75   # half-width of the 92 mm fan frame without pads (45.5 in Noctua's CAD) plus 0.25 clearance
WIRE_HOLE_R = 1.5        # corner radius of the wire/connector openings
CONN_W, WIRE_SLOT_H = 12.0, 4.0   # stepped openings: full-depth part for the 11 x 6 mm connector (rear end), shallow part for the wire (port end, beside the fan screw)
JOINT_CLEAR = 0.1    # clearance around the dovetails only; the flat seam faces butt together
TAB_NECK, TAB_LEN = 2.0, 3.0   # dovetail: half-width at the seam, length; 45 degree flanks
SPLIT_X = 0.0        # where the two halves join (inside the 92 mm opening, clear of the wire cutout)

F120 = dict(size=120.0, pitch=105.0, bore=116.0)   # from Noctua's CAD
F92  = dict(size=92.0,  pitch=82.5,  bore=88.0)

xr, h = FIN_L/2, RAIL_STRETCH/2
rear_holes = [(xr - TOP_INSET + h,  RAIL_CC_Y/2), (xr - BOT_INSET + h, -RAIL_CC_Y/2)]
port_holes = [(xr - TOP_BAR + TOP_INSET - h,  RAIL_CC_Y/2), (xr - BOT_BAR + BOT_INSET - h, -RAIL_CC_Y/2)]

x0 = -FIN_L/2 + FAN_SHIFT
fans, x = [], x0
for f in (F120, F92, F120):
    fans.append((x + f["size"]/2, f)); x += f["size"] + FAN_GAP
x1 = x - FAN_GAP
px0, px1, W = min(-FIN_L/2, x0 + 0.5), max(FIN_L/2, x1 - 0.5), max(FIN_W, F120["size"])   # plate ends flush with the 119 mm fan frames
floor_z = PLATE_T - HEAD_DEPTH
WP = lambda z=0.0: cq.Workplane("XY").workplane(offset=z)

# outline: rounded rectangle with the fan-wire cutout in the bottom edge
wx0, wx1 = port_holes[1][0] + WIRE_START, rear_holes[1][0] - WIRE_END
def outline(z0, height):
    o = WP(z0).center((px0 + px1)/2, 0).rect(px1 - px0, W).extrude(height)
    o = o.cut(WP(z0).center((wx0 + wx1)/2, -W/2 + WIRE_DEPTH/2 - 0.5).rect(wx1 - wx0, WIRE_DEPTH + 1.0).extrude(height))
    zc = z0 + height/2
    sel = lambda xa, xb, ya, yb: cq.selectors.BoxSelector((xa, ya, z0 - 1), (xb, yb, z0 + height + 1))
    o = o.edges("|Z").edges(sel(wx0 - 0.1, wx1 + 0.1, -W/2 + WIRE_DEPTH - 0.1, -W/2 + WIRE_DEPTH + 0.1)).fillet(NOTCH_R_IN)
    o = o.edges("|Z").edges(sel(wx0 - 0.1, wx1 + 0.1, -W/2 - 0.1, -W/2 + 0.1)).fillet(NOTCH_R_OUT)
    for cx in (px0, px1):
        for cy in (-W/2, W/2):
            o = o.edges("|Z").edges(sel(cx - 0.1, cx + 0.1, cy - 0.1, cy + 0.1)).fillet(CORNER_R)
    return o
plate = outline(0, PLATE_T)

# ridges on the underside, one over each rail, running the full length of the plate (trimmed to the outline)
ridges = None
r_in, r_out = RAIL_CC_Y/2 - PAD_D/2, W/2
for sgn in (1, -1):
    r = WP(-PAD_H).center((px0 + px1)/2, sgn*(r_in + r_out)/2).rect(px1 - px0, r_out - r_in).extrude(PAD_H)
    ridges = r if ridges is None else ridges.union(r)
ridges = ridges.intersect(outline(-PAD_H, PAD_H))
ridges = ridges.cut(WP(-PAD_H).center((wx0 + wx1)/2, -(r_in + r_out)/2).rect(wx1 - wx0 + 2*NOTCH_R_OUT + 1.0, r_out - r_in + 1).extrude(PAD_H))   # no sliver beside the cutout
plate = plate.union(ridges)

# fan openings and countersunk fan screw holes (heads on the underside)
fan_holes = []
cb_d, thr_d = FS_HEAD_D + 0.5, FS_THREAD_D + 0.25
for fx, f in fans:
    p = f["pitch"]/2
    pts = [(fx + a, FAN_OFF_Y + b) for a in (-p, p) for b in (-p, p)]; fan_holes += pts
    plate = plate.cut(WP(-PAD_H).center(fx, FAN_OFF_Y).circle(f["bore"]/2).extrude(PLATE_T + PAD_H))
    for (ax, ay) in pts:
        plate = plate.cut(WP(-PAD_H).center(ax, ay).circle(thr_d/2).extrude(PLATE_T + PAD_H))
        plate = plate.cut(WP(-PAD_H).center(ax, ay).circle(cb_d/2).extrude(FS_RECESS + PAD_H))
        cone = cq.Solid.makeCone((FS_HEAD_D + 0.2)/2, thr_d/2, FS_TAPER_H, cq.Vector(ax, ay, FS_RECESS), cq.Vector(0, 0, 1))
        plate = plate.cut(cq.Workplane("XY").add(cone))

# rail screws: plain through-hole with a head pocket on the fan side, same at all four corners
for hx, hy in port_holes + rear_holes:
    plate = plate.cut(WP(-PAD_H).center(hx, hy).circle(RAIL_HOLE_D/2).extrude(PAD_H + PLATE_T))
    plate = plate.cut(WP(floor_z).center(hx, hy).circle(HEAD_D/2).extrude(HEAD_DEPTH))

def rounded(pts, r, n=8):
    """Polygon with every corner rounded (works for right-angle corners, inside or outside)."""
    out, m = [], len(pts)
    for i in range(m):
        p, a, b = pts[i], pts[i - 1], pts[(i + 1) % m]
        la, lb = math.hypot(a[0] - p[0], a[1] - p[1]), math.hypot(b[0] - p[0], b[1] - p[1])
        rr = min(r, 0.45*la, 0.45*lb)
        ua, ub = ((a[0] - p[0])/la, (a[1] - p[1])/la), ((b[0] - p[0])/lb, (b[1] - p[1])/lb)
        c = (p[0] + rr*(ua[0] + ub[0]), p[1] + rr*(ua[1] + ub[1]))
        a0 = math.atan2(p[1] + rr*ua[1] - c[1], p[0] + rr*ua[0] - c[0]); a1 = math.atan2(p[1] + rr*ub[1] - c[1], p[0] + rr*ub[0] - c[0])
        d = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
        out += [(c[0] + rr*math.cos(a0 + d*k/n), c[1] + rr*math.sin(a0 + d*k/n)) for k in range(n + 1)]
    return out

# wire/connector openings over the gap in the fins, one beside each bar. Stepped: the rear part runs from the bar's inner
# edge to the 92 mm fan frame so a connector passes; the port part is shallow, leaving plastic around the fan screw.
gx0, gx1 = -FIN_L/2 + FIN_GAP_START, -FIN_L/2 + FIN_GAP_START + FIN_GAP_W
gxs = gx1 - CONN_W
wire_holes = []
for sgn in (1, -1):
    y_out = W/2 - RAIL_W                                  # inner edge of the bar
    y_in = F92_FRAME_HALF + sgn*FAN_OFF_Y                 # edge of the 92 mm fan frame on this side
    y_n = y_out - WIRE_SLOT_H                             # inner edge of the shallow part
    pts = [(gx0, sgn*y_n), (gxs, sgn*y_n), (gxs, sgn*y_in), (gx1, sgn*y_in), (gx1, sgn*y_out), (gx0, sgn*y_out)]
    wire_holes.append((sgn, y_in, y_out, y_n, pts))
    hole = cq.Workplane("XY").workplane(offset=-PAD_H).polyline(rounded(pts, WIRE_HOLE_R)).close().extrude(PLATE_T + PAD_H)
    plate = plate.cut(hole)

c92 = fans[1][0]

# split through the 92 mm opening with a dovetail in each side strip
sx = SPLIT_X
yt = (math.sqrt((F92["bore"]/2)**2 - (sx - c92)**2) + abs(FAN_OFF_Y) + W/2)/2
def tab(sign_x, yc, grow=0.0):
    n, hd = TAB_NECK, TAB_NECK + TAB_LEN
    pts = [(sx - sign_x, yc - n), (sx, yc - n), (sx + sign_x*TAB_LEN, yc - hd),
           (sx + sign_x*TAB_LEN, yc + hd), (sx, yc + n), (sx - sign_x, yc + n)]
    w = cq.Workplane("XY").polyline(pts).close()
    if grow: w = w.offset2D(grow)
    return w.extrude(PLATE_T + PAD_H + 2).translate((0, 0, -PAD_H - 1))
def region_a(grow=0.0):
    r = WP(-PAD_H - 1).center(sx - 500, 0).rect(1000, 1000).extrude(PLATE_T + PAD_H + 2)   # seam itself has no clearance
    return r.union(tab(+1, yt, grow)).cut(tab(-1, -yt, -grow if grow else 0.0))
half_a = plate.intersect(region_a())
half_b = plate.cut(region_a(JOINT_CLEAR))

HERE = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(HERE, "models"); os.makedirs(out, exist_ok=True)         # STLs, STEP and joiner (tracked in git)
preview = os.path.join(HERE, "preview"); os.makedirs(preview, exist_ok=True)   # SVG previews only (not tracked in git)
def report(name, wp):
    s = wp.val(); bb = s.BoundingBox()
    print("%-8s valid=%s solids=%d  x[%.1f, %.1f]  %.1f x %.1f x %.1f mm  %.1f cm3" % (
        name, s.isValid(), wp.solids().size(), bb.xmin, bb.xmax, bb.xlen, bb.ylen, bb.zlen, s.Volume()/1000))
for n, w in (("full", plate), ("half A", half_a), ("half B", half_b)): report(n, w)
print("port rail holes:", [(round(a, 3), round(b, 3)) for a, b in port_holes], " rear:", [(round(a, 3), round(b, 3)) for a, b in rear_holes])
print("wire cutout x %.3f..%.3f (%.2f long), y %.1f..%.1f" % (wx0, wx1, wx1 - wx0, -W/2, -W/2 + WIRE_DEPTH))
def _seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p; dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
    return math.hypot(px - ax - t*dx, py - ay - t*dy)
for sgn, y_in, y_out, y_n, pts in wire_holes:
    seat = min(_seg_dist(h, pts[i], pts[(i + 1) % len(pts)]) for h in fan_holes for i in range(len(pts))) - (FS_HEAD_D + 0.5)/2
    print("wire opening %s side: connector part x %.1f..%.1f (%.1f x %.2f), wire part x %.1f..%.1f (%.1f x %.1f); plastic to nearest fan screw seat %.2f mm" % (
        "top" if sgn > 0 else "bottom", gxs, gx1, gx1 - gxs, y_out - y_in, gx0, gxs, gxs - gx0, WIRE_SLOT_H, seat))
print("fan centres:", [round(fx, 2) for fx, _ in fans], " plate %.1f..%.1f: %.1f mm past port end, %.1f mm past rear end" % (px0, px1, -FIN_L/2 - px0, px1 - FIN_L/2))
for hx, hy in port_holes + rear_holes:
    d = min(math.hypot(hx - a, hy - b) for a, b in fan_holes)
    print("  rail hole (%.3f, %.3f): nearest fan hole %.2f mm; wall pocket/fan hole %.2f, pocket/seat cone %.2f, to bore %.2f" % (
        hx, hy, d, d - HEAD_D/2 - thr_d/2, d - HEAD_D/2 - (FS_HEAD_D + 0.2)/2,
        min(math.hypot(hx - fx, hy - FAN_OFF_Y) - f["bore"]/2 for fx, f in fans) - HEAD_D/2))
flip = lambda wp: wp.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, PLATE_T))   # fan side onto the bed
cq.exporters.export(plate,  f"{out}/5080-gaming-oc-fan-plate_full.step")
cq.exporters.export(flip(half_a), f"{out}/5080-gaming-oc-fan-plate_half-A-ports.stl", tolerance=0.02, angularTolerance=0.1)
cq.exporters.export(flip(half_b), f"{out}/5080-gaming-oc-fan-plate_half-B-rear.stl", tolerance=0.02, angularTolerance=0.1)
cq.exporters.export(flip(plate), f"{out}/5080-gaming-oc-fan-plate_full.stl", tolerance=0.02, angularTolerance=0.1)
cq.exporters.export(plate, f"{preview}/top.svg", opt=dict(projectionDir=(0, 0, 1), showHidden=False, width=1400, height=560))
cq.exporters.export(plate, f"{preview}/bottom.svg", opt=dict(projectionDir=(0, 0, -1), showHidden=False, width=1400, height=560))

# ---------- top joiner ----------
# Generated by joiner.py from the same fan layout, so its holes always match the plate.
from joiner import make_joiner, report as joiner_report
joiner, joiner_holes = make_joiner(fans)
joiner_report(joiner, joiner_holes)
cq.exporters.export(joiner, f"{out}/top_joiner.stl", tolerance=0.02, angularTolerance=0.1)

# ---------- README and docs ----------
README = """# Fan plate for a deshrouded Gigabyte RTX 5080 Gaming OC

A 3D-printed plate that mounts two Noctua NF-A12x25 (120 mm) fans and one NF-A9 (92 mm) on the bare heatsink
of a Gigabyte RTX 5080 Gaming OC, using four existing holes in the heatsink. The fans screw to the plate from
underneath, with their rubber corner pads removed, and two joiners tie them together on their outer face.

![The plate with the three fans and the two joiners, seen from the fan side](renders/hero.png)

Designed around my own card, no guarantees this will fit every other card of the same model. You can
optionally forego the adapter plate and just zip tie the fans to the heatsink.

## Files

| File | What it is |
|---|---|
| `models/5080-gaming-oc-fan-plate_half-A-ports.stl` | Port-side half of the plate |
| `models/5080-gaming-oc-fan-plate_half-B-rear.stl` | Rear half of the plate |
| `models/5080-gaming-oc-fan-plate_full.stl` | The plate in one piece ({plate_l:.1f} x {plate_w:.1f} mm), for beds that fit it |
| `models/top_joiner.stl` | Joiner for the outer face of the fans. Print two and turn one around |
| `models/5080-gaming-oc-fan-plate_full.step` | The plate as a solid model, for CAD programs |
| `templates/5080-plate-hole-template_*.pdf` | 1:1 paper templates of the hole layout (US Letter in two pages, US Legal in one) |

## Printing

- **The files are true size. Scale them for shrinkage.** Print one half at 100%, measure the plate width
  (modelled at {plate_w:.1f} mm), and scale X and Y by {plate_w:.1f} divided by your measurement. The parts
  shown here were printed in ABS at 100.7%, Z at 100%. Over the {hole_top:.2f} mm between the rail screw holes,
  even 0.5% is 1.5 mm, so do not skip this.
- Use a material that tolerates heat. ABS, ASA or PETG; not PLA.

## Hardware

- 4 M2 screws with a {m2_head:.2f} mm cylindrical head, 6 mm or longer, and 4 M2 nuts.
- 12 standard case-fan screws for the plate, plus 8 for the two joiners.

## Assembly

![Exploded view: plate, fans and joiners](renders/exploded.png)

1. Push the two halves together until the flat faces touch.
2. Fit the four M2 screws into their pockets from the fan side. The pockets are made slightly too tight on
   purpose: push each screw in with the tip of a soldering iron, like a heat-set insert, and the plastic
   closes around the head so the screw is held firmly and cannot spin.
3. Screw the fans to the plate from the underside.
4. Pass the fan connectors through the stepped openings beside the 92 mm fan and slide each wire into the
   shallow end of its opening. Do this before the plate goes on the card.

   <p>
   <img src="reference/fans-top.jpeg" width="49%" alt="Fans and joiners on the plate, seen from the intake side">
   <img src="reference/fans-bottom.jpeg" width="49%" alt="The same assembly from the heatsink side, wires routed through the openings">
   </p>

5. Lower the plate onto the heatsink so the ridges rest on the bars and the M2 screws pass through the bar
   holes, then fit the nuts from below.
6. Screw a joiner across the outer face of the fans on each long side.

![The finished assembly on the card](reference/fully-assembled.jpeg)

## Fan harness

The card has a single fan header, a 2.0 mm pitch JST PHD 2 x 6 connector, so the three fans need a custom
harness. This is the pinout of the harness's own connector, the female JST plug that goes onto the card's header:

![Pinout of the harness connector](reference/connector-pinout.png)

The harness in the pictures was made from two kits: [4-pin fan connector plugs](https://www.amazon.com/dp/B08HYTGH7D)
for the fan side and a [JST PHD connector kit](https://www.amazon.com/dp/B0CKZF94RR) for the card side. You need
a crimp tool to attach the JST connector wires to the fan header pins.

Before printing, lay the paper template on the heatsink at 100% and check that the four ringed crosses sit
over the bar holes. The plate extends {over_port:.1f} mm past the port end of the heatsink and {over_rear:.1f} mm
past the rear; make sure your card and case have that room.

## Changing the design

Everything is generated by a Python script. Parameters, what they do, and how to regenerate the files are in
[docs/changing-the-design.md](docs/changing-the-design.md).

## License

Models, templates and documentation: [CC BY 4.0](LICENSE-CC-BY-4.0). Scripts: [MIT](LICENSE). Noctua's fan
CAD files in `reference/` are Noctua's, included as downloaded from their website.
"""

DOCS = """# Changing the design

The plate, the joiner, this file and the README are all written by `fan_plate.py`. Change a number at the top
of the script, run it, and every file follows. All dimensions are in millimetres. The view is from the fan
side with the ports on the left: X runs along the card, Y across it, Z = 0 is the fin tops.

![The underside of the plate, which faces the heatsink](../renders/underside.png)

## Setting up

You need Python 3.10 to 3.12 with CadQuery. The paper templates need `reportlab` and the renders `pyvista`.
Install into a virtual environment:

    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt

## Regenerating

    .venv/bin/python fan_plate.py              # models/ (STL, STEP, joiner), README.md, this file, preview/*.svg
    .venv/bin/python joiner.py                 # the joiner on its own
    .venv/bin/python tools/paper_template.py   # templates/*.pdf (its numbers are typed in by hand: update them
                                               # whenever holes, fans, cutout or openings move)
    .venv/bin/python tools/render_meshes.py    # fine meshes of the fans, plate and joiner for rendering, into preview/render/
    .venv/bin/python tools/render.py           # renders/: the pictures

The fan screws and the rail screws sit very close together at the corners. After any change to the holes or
the fans, read the lines the script prints for each rail hole: they give the plastic left between the screw
pocket and the nearest fan screw hole. Keep that above about 1 mm.

## Shrinkage, in more detail

Rough shrinkage by material. Treat these as starting points, since brand, chamber temperature and part
position on the bed all change the result:

| Material | Typical shrinkage |
|---|---|
| PLA | 0.2% to 0.5% (softens near a hot GPU, so not recommended) |
| PETG | 0.3% to 0.6% |
| ABS, ASA | 0.4% to 0.8% (the original prints measured 0.5% to 0.7%; the final print used 100.7%) |
| Polycarbonate | 0.5% to 0.8% |
| Nylon | 1% to 2%, less for fibre-filled grades |

Shrinkage can differ along and across a long part. To check, also measure the port-side half from its outer
end to the flat face where the halves meet (modelled at {half_a:.1f} mm) and use a separate factor for that axis.
Measure on a single half, never across the joint. Print the final parts with the same material, settings and
bed position as the test.

## Parameters

**Different rail screws**

- `HEAD_D`: diameter of the head pocket. Use the head diameter plus about 0.05 for a snug fit.
- `HEAD_DEPTH`: depth of the pocket. Use the head height plus about 0.2.
- `RAIL_HOLE_D`: clearance hole for the thread.
- `PLATE_T`: keep it at least 0.8 more than `HEAD_DEPTH`, so there is a floor under the head.

**Different fan screws**

- `FS_HEAD_D`, `FS_TAPER_H`, `FS_THREAD_D`: head diameter, height of the tapered part of the head, and thread diameter.
- `FS_RECESS`: how far the head sits below the underside of the plate.

**Different hole positions on the heatsink**

- `RAIL_CC_Y`: distance between the two rows of holes, across the card.
- `TOP_BAR`, `BOT_BAR`: length of each bar. Both bars are assumed to end flush at the rear of the heatsink.
- `TOP_INSET`, `BOT_INSET`: distance from the end of each bar to the centre of its hole.
- `RAIL_STRETCH`: a correction added to the lengthwise spacing, split between both ends.
- `FIN_L`, `FIN_W`: length and width of the heatsink.
- `PAD_H`: height of the ridges. Set it to how far the bars sit below the fin tops, or slightly more.

**Fan positions**

- `FAN_SHIFT`: where the fan row starts, measured from the port end of the heatsink (negative is in front of it).
- `FAN_GAP`: gap between neighbouring fans.
- `FAN_OFF_Y`: sideways offset of the whole fan row.
- `F120`, `F92`, `F92_FRAME_HALF`: fan sizes, screw spacing and opening diameters, for fans other than these Noctuas.
  The joiner (`joiner.py`) takes its hole positions from the same layout.

**Wire openings and cutout**

- `FIN_GAP_START`, `FIN_GAP_W`: position and width of the gap in the fins that the wire openings sit over.
- `RAIL_W`: width of the bar there. The openings start at its inner edge.
- `CONN_W`, `WIRE_SLOT_H`: width of the connector part and depth of the wire slot.
- `WIRE_START`, `WIRE_END`, `WIRE_DEPTH`: the cutout in the bottom edge, measured from the two bottom rail holes.

**Splitting for the print bed**

- `SPLIT_X`: where the halves join. Keep it inside the 92 mm opening and clear of the edge cutout.
- `JOINT_CLEAR`, `TAB_NECK`, `TAB_LEN`: fit and size of the dovetails.

The paper templates are drawn for this exact design and are not regenerated by the script, so after changing
hole positions, check the new layout another way, for example by printing a thin test piece of each corner.
"""

numbers = dict(plate_l=px1 - px0, plate_w=W, plate_t=PLATE_T, ridge_h=PAD_H, total_t=PLATE_T + PAD_H,
               hole_top=rear_holes[0][0] - port_holes[0][0], half_a=SPLIT_X - px0, m2_head=M2_HEAD_D,
               fs_recess=FS_RECESS, over_port=-FIN_L/2 - px0, over_rear=px1 - FIN_L/2)
with open(os.path.join(HERE, "README.md"), "w") as fh:
    fh.write(README.format(**numbers))
os.makedirs(os.path.join(HERE, "docs"), exist_ok=True)
with open(os.path.join(HERE, "docs", "changing-the-design.md"), "w") as fh:
    fh.write(DOCS.format(**numbers))
print("README.md and docs/changing-the-design.md written")
