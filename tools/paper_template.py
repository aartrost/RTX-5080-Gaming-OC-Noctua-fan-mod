from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter, legal, landscape
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")   # PDFs are written to templates/

# geometry (same numbers as the plate model); fan-side view: -X ports, +X rear, +Y top bar
FIN_L, FIN_W = 319.0, 121.0
PX0, PX1, W = -165.4, 167.4, 121.0
FY = -0.75   # fan row offset toward the bottom bar
FANS = [(-105.9, 105.0, 116.0), (1.0, 82.5, 88.0), (107.9, 105.0, 116.0)]   # centre x, hole pitch, bore
RAIL = [(-154.875, 56.125, "top bar, port end"), (155.875, 56.125, "top bar, rear end"),
        (-151.625, -56.125, "bottom bar, port end"), (155.625, -56.125, "bottom bar, rear end")]
JOIN_X = 15.0

def cross(c, x, y, r, lw=0.2):
    c.setLineWidth(lw); c.line((x - r)*mm, y*mm, (x + r)*mm, y*mm); c.line(x*mm, (y - r)*mm, x*mm, (y + r)*mm)

def drawing(c, show_join, label_x=-40):
    # heatsink footprint
    c.setStrokeGray(0.55); c.setLineWidth(0.3); c.setDash(3, 2)
    c.rect(-FIN_L/2*mm, -FIN_W/2*mm, FIN_L*mm, FIN_W*mm)
    c.setDash(); c.setStrokeGray(0)
    # plate outline
    c.setLineWidth(0.5); c.rect(PX0*mm, -W/2*mm, (PX1 - PX0)*mm, W*mm)
    # fan-wire cutout in the bottom edge
    c.setLineWidth(0.5); c.setFillGray(0.85); c.rect(8.375*mm, -W/2*mm, 23.25*mm, 6.0*mm, stroke=1, fill=1); c.setFillGray(0)
    c.setFont('Helvetica', 6.5); c.drawCentredString(20*mm, (-W/2 + 7.5)*mm, 'edge cutout')
    # wire/connector openings over the gap in the fins, plus the gap itself
    c.setLineWidth(0.4)
    for pts in ([(-44.5, 49.5), (-35.5, 49.5), (-35.5, 45.0), (-23.5, 45.0), (-23.5, 53.5), (-44.5, 53.5)],
                [(-44.5, -49.5), (-35.5, -49.5), (-35.5, -46.5), (-23.5, -46.5), (-23.5, -53.5), (-44.5, -53.5)]):
        p = c.beginPath(); p.moveTo(pts[0][0]*mm, pts[0][1]*mm)
        for q in pts[1:]: p.lineTo(q[0]*mm, q[1]*mm)
        p.close(); c.drawPath(p, stroke=1, fill=0)
    c.setStrokeGray(0.55); c.setLineWidth(0.25); c.setDash(2, 2)
    c.line(-44.5*mm, -W/2*mm, -44.5*mm, W/2*mm); c.line(-23.5*mm, -W/2*mm, -23.5*mm, W/2*mm)
    c.setDash(); c.setStrokeGray(0)
    c.setFont('Helvetica', 6.5); c.drawCentredString(-34*mm, 30*mm, 'gap in fins'); c.drawCentredString(-34*mm, 55*mm, 'wire opening'); c.drawCentredString(-34*mm, -57*mm, 'wire opening')
    # fan openings and fan screw holes
    for fx, pitch, bore in FANS:
        c.setStrokeGray(0.45); c.setLineWidth(0.3); c.circle(fx*mm, FY*mm, bore/2*mm)
        cross(c, fx, FY, 3)
        for a in (-pitch/2, pitch/2):
            for b in (-pitch/2, pitch/2):
                c.setLineWidth(0.3); c.circle((fx + a)*mm, (b + FY)*mm, 2.55*mm); cross(c, fx + a, b + FY, 4.0, 0.15)
    c.setStrokeGray(0)
    # rail holes: the ones to verify
    for x, y, name in RAIL:
        c.setLineWidth(0.35); c.circle(x*mm, y*mm, 1.125*mm)
        cross(c, x, y, 7, 0.25)
        c.setLineWidth(0.2); c.circle(x*mm, y*mm, 4.5*mm)
    # fan frame outlines
    c.setStrokeGray(0.6); c.setLineWidth(0.25)
    for fx, pitch, bore in FANS:
        hw = 59.5 if bore > 100 else 46.0
        c.rect((fx - hw)*mm, (FY - hw)*mm, 2*hw*mm, 2*hw*mm)
    c.setStrokeGray(0)
    # labels
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(label_x*mm, (W/2 + 3)*mm, "TOP BAR SIDE (318 mm bar)")
    c.drawCentredString(label_x*mm, (-W/2 - 6)*mm, "BOTTOM BAR SIDE (315 mm bar, PCIe connector side)")
    c.setFont("Helvetica", 7)
    for x, y, name in RAIL:
        s = 1 if x < 0 else -1
        tx = x + s*9
        ty = y - 9 if y > 0 else y + 7
        (c.drawString if s > 0 else c.drawRightString)(tx*mm, ty*mm, "rail hole: " + name)
    c.setFont("Helvetica", 6.5); c.setFillGray(0.35)
    c.drawString((FANS[0][0] + 4)*mm, 6*mm, "120 mm fan (119 mm frame without pads)"); c.drawString((FANS[1][0] + 4)*mm, 6*mm, "92 mm fan"); c.drawString((FANS[2][0] + 4)*mm, 6*mm, "120 mm fan")
    c.drawString((-FIN_L/2 + 10)*mm, -8*mm, "dashed = heatsink, 319 x 121"); c.drawRightString((PX1 - 1.5)*mm, -8*mm, "solid = plate")
    c.setFillGray(0)
    if show_join:
        c.setStrokeGray(0); c.setLineWidth(0.3); c.setDash(6, 2, )
        c.line(JOIN_X*mm, -92*mm, JOIN_X*mm, 92*mm); c.setDash()
        for yy in (-84, 84):
            cross(c, JOIN_X, yy, 5, 0.3); c.setLineWidth(0.3); c.circle(JOIN_X*mm, yy*mm, 2.5*mm)

def header(c, pw, ph, title, note):
    c.setFont("Helvetica-Bold", 11); c.drawString(10*mm, ph - 11*mm, title)
    c.setFont("Helvetica", 8); c.drawString(10*mm, ph - 16*mm, note)
    # scale check: 100 mm ruler
    x0, y0 = 10*mm, 9*mm
    c.setLineWidth(0.4); c.line(x0, y0, x0 + 100*mm, y0)
    for i in range(0, 101, 10):
        c.setLineWidth(0.4 if i % 50 == 0 else 0.25)
        c.line(x0 + i*mm, y0, x0 + i*mm, y0 + (4 if i % 50 == 0 else 2.5)*mm)
    c.setFont("Helvetica", 7.5)
    c.drawString(x0 + 103*mm, y0, "Scale check: this ruler must measure exactly 100 mm. Print at 100% / \"Actual size\", not \"Fit to page\".")

def page(c, size, title, note, origin_x_mm, clip=None, show_join=False, label_x=-40):
    pw, ph = size
    c.setPageSize(size)
    header(c, pw, ph, title, note)
    c.saveState()
    c.translate(origin_x_mm*mm, ph/2 + 1*mm)
    if clip:
        p = c.beginPath(); p.rect(clip[0]*mm, -95*mm, (clip[1] - clip[0])*mm, 190*mm); c.clipPath(p, stroke=0, fill=0)
    drawing(c, show_join, label_x)
    c.restoreState()
    c.showPage()

# --- US Letter, two pages ---
L = landscape(letter)
c = canvas.Canvas(os.path.join(ROOT, "5080-plate-hole-template_letter-2-pages.pdf"), pagesize=L)
c.setTitle("RTX 5080 Gaming OC fan plate - hole template (Letter, 2 pages)")
page(c, L, "Hole template, page 1 of 2: PORT END  (view from the fan side; ports to the left)",
     "Cut page 2 along its dashed join line, lay it over this page so the join lines and both ringed crosses line up, then tape.",
     origin_x_mm=175.0, clip=(-173, JOIN_X + 22), show_join=True, label_x=-75)
page(c, L, "Hole template, page 2 of 2: REAR END  (view from the fan side; rear to the right)",
     "Cut along the dashed join line on the left, then overlay on page 1 matching the two ringed crosses.",
     origin_x_mm=60.0, clip=(JOIN_X - 22, 186), show_join=True, label_x=95)
c.save()

# --- US Legal, one page ---
G = landscape(legal)
c = canvas.Canvas(os.path.join(ROOT, "5080-plate-hole-template_legal-1-page.pdf"), pagesize=G)
c.setTitle("RTX 5080 Gaming OC fan plate - hole template (Legal, 1 page)")
page(c, G, "Hole template, full length  (view from the fan side; ports to the left, rear to the right)",
     "Rail holes: 310.75 mm apart on the top bar, 307.25 mm on the bottom bar, 112.25 mm across.",
     origin_x_mm=355.6/2 - (PX0 + PX1)/2, label_x=10)
c.save()
