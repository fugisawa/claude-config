"""Folha de contato de um PDF (todas as páginas em 1-2 imagens) para inspeção visual.

Uso:
    uv run --with pillow python contact_sheet.py arquivo.pdf /tmp/dir-saida
    # requer pdftoppm (poppler-utils) no PATH
"""
import glob
import os
import subprocess
import sys

from PIL import Image

PDF, OUTDIR = sys.argv[1], sys.argv[2]
COLS, THUMB_W, PER_SHEET = 6, 220, 24

os.makedirs(OUTDIR, exist_ok=True)
subprocess.run(["pdftoppm", "-png", "-r", "60", PDF, os.path.join(OUTDIR, "p")], check=True)

files = sorted(glob.glob(os.path.join(OUTDIR, "p-*.png")))
if not files:
    sys.exit("erro: pdftoppm não gerou páginas")
for sheet_i in range(0, len(files), PER_SHEET):
    batch = files[sheet_i:sheet_i + PER_SHEET]
    ims = [Image.open(f) for f in batch]
    th = int(ims[0].height * THUMB_W / ims[0].width)
    rows = (len(ims) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * (THUMB_W + 4), rows * (th + 4)), "white")
    for i, im in enumerate(ims):
        sheet.paste(im.resize((THUMB_W, th)),
                    ((i % COLS) * (THUMB_W + 4) + 2, (i // COLS) * (th + 4) + 2))
    out = os.path.join(OUTDIR, f"sheet{sheet_i // PER_SHEET + 1}.png")
    sheet.save(out)
    print(out)
