import re, base64

svg_path = r"C:\Users\DELL\Documents\Downloads\net_ve.svg"
with open(svg_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

m = re.search(r'href="data:image/png;base64,([^"]+)"', content)
if m:
    b64_data = m.group(1)
    png_bytes = base64.b64decode(b64_data)
    out_png = r"c:\Users\DELL\Documents\CODE\DU_AN\mts_logo_extracted.png"
    with open(out_png, 'wb') as out_f:
        out_f.write(png_bytes)
    print(f"Extracted logo PNG! Size: {len(png_bytes)} bytes. Saved to: {out_png}")
else:
    print("Base64 image not found in SVG!")
