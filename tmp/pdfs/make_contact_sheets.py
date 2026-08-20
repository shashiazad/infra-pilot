from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

src = Path("/Users/shashi/Projects/Personal/infra-pilot/tmp/pdfs/rendered")
pages = sorted(src.glob("page-*.png"))
out = src / "contact"
out.mkdir(exist_ok=True)

for group_no in range(0, len(pages), 10):
    selected = pages[group_no:group_no + 10]
    thumbs = []
    for idx, path in enumerate(selected, start=group_no + 1):
        im = Image.open(path).convert("RGB")
        w = 250
        h = round(im.height * w / im.width)
        im = im.resize((w, h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (w + 8, h + 30), "white")
        canvas.paste(im, (4, 24))
        draw = ImageDraw.Draw(canvas)
        draw.text((6, 5), f"Page {idx}", fill="black")
        canvas = ImageOps.expand(canvas, border=1, fill="#9aa7b4")
        thumbs.append(canvas)
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    cw = max(i.width for i in thumbs)
    ch = max(i.height for i in thumbs)
    sheet = Image.new("RGB", (cols * cw + 30, rows * ch + 30), "#dde4ea")
    for i, im in enumerate(thumbs):
        x = 10 + (i % cols) * cw
        y = 10 + (i // cols) * ch
        sheet.paste(im, (x, y))
    sheet.save(out / f"contact-{group_no // 10 + 1}.jpg", quality=88)
