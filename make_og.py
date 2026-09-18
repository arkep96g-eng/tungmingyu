#!/usr/bin/env python3
"""Render assets/og.png (1200x630) — the link-preview card for LinkedIn / X / Slack.
Mirrors the "bold" theme: white ground, black rules, condensed uppercase name, blue accent.
Run after build.py whenever the headline numbers change.  Requires Pillow."""
import json
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent
site = json.loads((ROOT / "data/site.json").read_text("utf-8"))
patents = json.loads((ROOT / "data/patents.json").read_text("utf-8"))
papers = json.loads((ROOT / "data/publications.json").read_text("utf-8"))

fams = patents["itri"]["families"] + patents["somnics"]["families"]
pubs = [p for f in fams for p in f["pubs"]]
juris = {p["cc"] for p in pubs} | {v for p in pubs for v in p.get("validated", [])}
juris.discard("WO")
figures = [(len(fams), "PATENT FAMILIES"), (len(pubs), "GRANTED / PUBLISHED"),
           (len(juris), "JURISDICTIONS"), (len(papers["journal"]) + len(papers["conference"]), "PAPERS")]

W, H = 1200, 630
INK, MUTED, LINE, ACCENT = (10, 10, 10), (90, 90, 90), (226, 226, 226), (23, 48, 208)
FONTS = "C:/Windows/Fonts/"
f_name = ImageFont.truetype(FONTS + "ARIALNB.TTF", 150)
f_zh = ImageFont.truetype(FONTS + "msjhbd.ttc", 40)
f_tag = ImageFont.truetype(FONTS + "segoeuib.ttf", 24)
f_num = ImageFont.truetype(FONTS + "ARIALNB.TTF", 76)
f_lab = ImageFont.truetype(FONTS + "segoeuib.ttf", 18)
f_url = ImageFont.truetype(FONTS + "segoeui.ttf", 22)

im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
M = 72
d.rectangle([M, 56, W - M, 60], fill=INK)                       # top rule
d.text((M, 84), "INVENTOR PORTFOLIO", font=f_lab, fill=MUTED)
d.text((M - 4, 118), site["name_en"].upper(), font=f_name, fill=INK)
d.text((M, 285), site["name_zh"], font=f_zh, fill=MUTED)
d.text((M + 150, 293), site["tagline_en"].upper(), font=f_tag, fill=MUTED)
d.rectangle([M, 356, W - M, 360], fill=INK)                     # figures rule
x = M
for n, label in figures:
    d.text((x, 384), str(n), font=f_num, fill=INK)
    d.text((x, 470), label, font=f_lab, fill=MUTED)
    x += 258
d.rectangle([M, 516, W - M, 517], fill=LINE)
d.rectangle([M, 516, M + 120, 520], fill=ACCENT)                # accent tick
d.text((M, 540), site.get("base_url", "").replace("https://", ""), font=f_url, fill=MUTED)
out = ROOT / "assets" / "og.png"
out.parent.mkdir(exist_ok=True)
im.save(out, optimize=True)
print("wrote", out, im.size)
