"""Generate the pipeline data-flow animation GIF for NN-Accel-Triage.

A failing test flows through the six pipeline stages; each stage lights up as
the data token arrives, and a caption band narrates the step.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("/home/user/nn-accel-triage/presentation/assets/pipeline_animation.gif")
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 1600, 720
BG = (247, 249, 252)
INK = (26, 32, 44)
MUTE = (113, 128, 150)
BORDER = (203, 213, 224)
ACCENT = (43, 108, 176)
ACCENT_LT = (224, 236, 250)
GREEN = (47, 133, 90)
GREEN_LT = (224, 242, 233)
BAND = (23, 30, 48)

FONT = "/usr/share/fonts/truetype/liberation/"
def f(name, size):
    return ImageFont.truetype(FONT + name, size)
F_TITLE = f("LiberationSans-Bold.ttf", 34)
F_STAGE = f("LiberationSans-Bold.ttf", 21)
F_SUB = f("LiberationSans-Regular.ttf", 17)
F_CAP = f("LiberationSans-Regular.ttf", 24)
F_CAPB = f("LiberationSans-Bold.ttf", 24)
F_TOK = f("LiberationSans-Bold.ttf", 18)
F_SMALL = f("LiberationSans-Regular.ttf", 15)
F_MONO = f("LiberationMono-Bold.ttf", 16)

# Six stages laid out in two rows of three (serpentine flow).
STAGES = [
    ("1  RTL Fault",        "fault_acc_overflow.sv"),
    ("2  Verilator Sim",    "N x N MAC - INT8"),
    ("3  Mismatch Record",  "regression_db.jsonl"),
    ("4  Cluster (DBSCAN)", "-> overflow_fault"),
    ("5  Claude Triage",    "RAG + agentic loop"),
    ("6  Root-Cause Report","cause + confidence"),
]
# token label + caption per stage
STEP = [
    ("BUG",    "Injected RTL fault variant selected from the frozen fault library."),
    ("SIM",    "Verilator simulates the tile; scoreboard checks DUT vs golden model."),
    ("{json}", "Output mismatch detected -> one JSON record appended to regression DB."),
    ("vec",    "13-D feature vector clustered by DBSCAN -> symptom label 'overflow_fault'."),
    ("LLM",    "Claude retrieves similar past cases (RAG) and reasons over the cluster."),
    ("card",   "Structured report: likely cause, confidence, and recommended debug steps."),
]

BOX_W, BOX_H = 430, 132
# positions (top-left) for serpentine: row0 L->R, row1 R->L
COLS = [90, 585, 1080]
ROW0, ROW1 = 150, 400
POS = [
    (COLS[0], ROW0), (COLS[1], ROW0), (COLS[2], ROW0),
    (COLS[2], ROW1), (COLS[1], ROW1), (COLS[0], ROW1),
]
CENTERS = [(x + BOX_W // 2, y + BOX_H // 2) for (x, y) in POS]


def rrect(d, box, r, fill, outline, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def draw_box(d, i, state):
    x, y = POS[i]
    title, sub = STAGES[i]
    if state == "active":
        rrect(d, (x - 5, y - 5, x + BOX_W + 5, y + BOX_H + 5), 20, ACCENT_LT, ACCENT, 4)
        tcol, scol = ACCENT, (74, 85, 104)
    elif state == "done":
        rrect(d, (x, y, x + BOX_W, y + BOX_H), 18, GREEN_LT, GREEN, 2)
        tcol, scol = GREEN, (74, 85, 104)
    else:
        rrect(d, (x, y, x + BOX_W, y + BOX_H), 18, (255, 255, 255), BORDER, 2)
        tcol, scol = INK, MUTE
    d.text((x + 26, y + 30), title, font=F_STAGE, fill=tcol)
    d.text((x + 26, y + 74), sub, font=F_MONO if "." in sub or "_" in sub or ">" in sub else F_SUB, fill=scol)
    if state == "done":
        # checkmark
        cx, cy = x + BOX_W - 40, y + 34
        d.line([(cx - 9, cy), (cx - 2, cy + 8), (cx + 11, cy - 10)], fill=GREEN, width=4)


def arrow(d, p0, p1, active):
    col = ACCENT if active else BORDER
    wd = 5 if active else 3
    d.line([p0, p1], fill=col, width=wd)
    # arrowhead
    import math
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    L = 16
    for da in (2.6, -2.6):
        d.line([p1, (p1[0] - L * math.cos(ang + da), p1[1] - L * math.sin(ang + da))], fill=col, width=wd)


def edge_points(i):
    """Return (start, end) points for the connector from stage i to i+1."""
    x0, y0 = POS[i]
    x1, y1 = POS[i + 1]
    if y0 == y1 and x1 > x0:            # same row, going right
        return (x0 + BOX_W, y0 + BOX_H // 2), (x1, y1 + BOX_H // 2)
    if y0 == y1 and x1 < x0:            # same row, going left
        return (x0, y0 + BOX_H // 2), (x1 + BOX_W, y1 + BOX_H // 2)
    # vertical drop (row0 -> row1, same column)
    return (x0 + BOX_W // 2, y0 + BOX_H), (x1 + BOX_W // 2, y1)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def draw_token(d, pt, label):
    x, y = pt
    r = 30
    # glow
    d.ellipse((x - r - 8, y - r - 8, x + r + 8, y + r + 8), fill=(43, 108, 176, 0))
    d.ellipse((x - r, y - r, x + r, y + r), fill=ACCENT, outline=(255, 255, 255), width=3)
    tb = d.textbbox((0, 0), label, font=F_TOK)
    d.text((x - (tb[2] - tb[0]) / 2, y - (tb[3] - tb[1]) / 2 - 2), label, font=F_TOK, fill=(255, 255, 255))


def base_frame(active_idx, done_upto):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # header
    d.text((90, 48), "How it works:  a failing test flows through the triage pipeline",
           font=F_TITLE, fill=INK)
    d.line([(90, 108), (W - 90, 108)], fill=BORDER, width=2)
    # connectors
    for i in range(len(STAGES) - 1):
        p0, p1 = edge_points(i)
        arrow(d, p0, p1, active=(i < done_upto or i == active_idx - 1 and active_idx > 0))
    # boxes
    for i in range(len(STAGES)):
        if i < done_upto:
            st = "done"
        elif i == active_idx:
            st = "active"
        else:
            st = "idle"
        draw_box(d, i, st)
    return img, d


def caption(d, idx):
    # caption band
    d.rounded_rectangle((90, 610, W - 90, 686), radius=14, fill=BAND)
    label, txt = STEP[idx][0], STEP[idx][1]
    tag = f"STEP {idx+1}/6"
    d.text((118, 636), tag, font=F_CAPB, fill=(120, 170, 235))
    d.text((250, 636), txt, font=F_CAP, fill=(237, 242, 247))


frames = []
DWELL = 5      # frames a stage stays highlighted
TRAVEL = 9     # frames the token travels an edge

# intro dwell on stage 0
for _ in range(DWELL + 2):
    img, d = base_frame(active_idx=0, done_upto=0)
    draw_token(d, CENTERS[0], STEP[0][0])
    caption(d, 0)
    frames.append(img)

for i in range(len(STAGES) - 1):
    p0, p1 = edge_points(i)
    # travel from stage i to i+1
    for k in range(1, TRAVEL + 1):
        t = k / TRAVEL
        img, d = base_frame(active_idx=i, done_upto=i)
        draw_token(d, lerp(p0, p1, t), STEP[i][0])
        caption(d, i)
        frames.append(img)
    # dwell on stage i+1
    for _ in range(DWELL):
        img, d = base_frame(active_idx=i + 1, done_upto=i + 1)
        draw_token(d, CENTERS[i + 1], STEP[i + 1][0])
        caption(d, i + 1)
        frames.append(img)

# final: all done, show result emphasis
for _ in range(10):
    img, d = base_frame(active_idx=-1, done_upto=len(STAGES))
    caption(d, len(STAGES) - 1)
    frames.append(img)

frames[0].save(
    OUT, save_all=True, append_images=frames[1:],
    duration=95, loop=0, optimize=True, disposal=2,
)
print("frames:", len(frames), "->", OUT, OUT.stat().st_size // 1024, "KB")
