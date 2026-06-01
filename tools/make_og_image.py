#!/usr/bin/env python3
"""Generate the social-preview (Open Graph) thumbnail for the interactive page.

Recreates the page's key visual — the genetic-expectation vs. phenotype scatter,
with a neutral diagonal "aligned" band and red/blue "misaligned" tails — at the
1200x630 size used by Open Graph / Twitter cards, with the page's headline.

Output: og-preview.png (repo root).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---- palette (from index.html :root) ----
INK   = (22, 20, 15)
PAPER = (251, 250, 246)
RULE  = (227, 18, 11)
GREY  = (184, 180, 170)
HIGH  = (198, 54, 47)
LOW   = (47, 111, 158)
GOLD  = (211, 155, 31)
MUTED = (110, 106, 96)

W, H = 1200, 630
SS = 2                      # supersample for crisp dots/text
img = Image.new("RGB", (W * SS, H * SS), PAPER)
d = ImageDraw.Draw(img, "RGBA")

def font(path, size):
    return ImageFont.truetype(path, size * SS)

F_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
F_BOLD  = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
F_SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"

# ---- layout: text on the left, scatter on the right ----
PADX = 64
top_rule_y = 54
# masthead rule
d.rectangle([PADX*SS, top_rule_y*SS, (W-PADX)*SS, (top_rule_y+6)*SS], fill=RULE)

# kicker
fk = font(F_BOLD, 19)
d.text((PADX*SS, (top_rule_y+22)*SS), "INTERACTIVE · THE MISALIGNMENT MODEL",
       font=fk, fill=RULE)

# headline (wrapped), left column ~ 620px wide
fh = font(F_BLACK, 44)
headline = ["Why do some", "individuals defy their", "polygenic score?"]
y = (top_rule_y + 60) * SS
for line in headline:
    d.text((PADX*SS, y), line, font=fh, fill=INK)
    y += int(52 * SS)

# standfirst
fs = font(F_SERIF, 21)
sub = ["A polygenic score predicts a trait from common DNA.",
       "A burden of rare, damaging variants can override that",
       "prediction — pulling a person away from expectation."]
y += int(16 * SS)
for line in sub:
    d.text((PADX*SS, y), line, font=fs, fill=MUTED)
    y += int(31 * SS)

# ---- scatter panel (right) ----
rng = np.random.default_rng(7)
N = 2600
panel_l, panel_r = 700, W - 56
panel_t, panel_b = 150, H - 60
pw, ph = panel_r - panel_l, panel_b - panel_t

g = rng.normal(0, 1, N)                       # genetic expectation (x)
noise = rng.normal(0, 0.62, N)
p = g + noise                                  # phenotype (y)
# inject a misaligned cohort: rare-variant burden pushing phenotype off-diagonal
nmis = 360
gi = rng.normal(0, 0.9, nmis)
sign = rng.choice([-1, 1], nmis)
pi = gi + sign * rng.uniform(1.9, 3.4, nmis)
g = np.concatenate([g, gi]); p = np.concatenate([p, pi])

LIM = 3.6
def X(v): return panel_l + (v + LIM) / (2 * LIM) * pw
def Y(v): return panel_b - (v + LIM) / (2 * LIM) * ph

# faint diagonal guide
d.line([X(-LIM)*SS, Y(-LIM)*SS, X(LIM)*SS, Y(LIM)*SS],
       fill=(*GREY, 150), width=2*SS)

r = p - g                                      # residual: distance off-diagonal
for xi, yi, ri in zip(g, p, r):
    if -LIM < xi < LIM and -LIM < yi < LIM:
        if abs(ri) < 1.0:                      # aligned
            col, rad = (*GREY, 200), 3.0
        elif ri > 0:                           # phenotype above expectation
            col, rad = (*HIGH, 235), 3.4
        else:
            col, rad = (*LOW, 235), 3.4
        cx, cy = X(xi)*SS, Y(yi)*SS
        d.ellipse([cx-rad*SS, cy-rad*SS, cx+rad*SS, cy+rad*SS], fill=col)

# axis labels
fa = font(F_BOLD, 15)
d.text((((panel_l+panel_r)/2 - 92)*SS, (panel_b+16)*SS),
       "GENETIC EXPECTATION", font=fa, fill=MUTED)
# rotated y-label
lbl = Image.new("RGBA", (260*SS, 22*SS), (0,0,0,0))
ld = ImageDraw.Draw(lbl)
ld.text((0,0), "OBSERVED PHENOTYPE", font=fa, fill=MUTED)
lbl = lbl.rotate(90, expand=True)
img.paste(lbl, ((panel_l-30)*SS, int((panel_t+ph/2-130)*SS)), lbl)

# downsample
img = img.resize((W, H), Image.LANCZOS)
img.save("og-preview.png", optimize=True)
print("wrote og-preview.png", img.size)
