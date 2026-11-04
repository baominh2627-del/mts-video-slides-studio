import re, sys, zipfile, xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
docx_path = r"C:\Users\DELL\Documents\Downloads\Lời thuyết minh video giải Câu 16 (bản 3 phút 10 giây).docx"

with zipfile.ZipFile(docx_path) as z:
    xml_content = z.read("word/document.xml")
    tree = ET.fromstring(xml_content)
    paragraphs = []
    for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
        if texts:
            paragraphs.append("".join(texts))

# Pattern for timestamp lines: e.g. "0:00 – 0:04.5 Câu mười sáu: ... Màn hình: ..."
# or "1:05.5 – 1:09.5 dV bằng ..."
pattern = re.compile(r'^(\d+:\d+(?:\.\d+)?)\s*[–-]\s*(\d+:\d+(?:\.\d+)?)\s+(.*?)(?:\s+Màn hình:\s*(.*))?$', re.IGNORECASE)

def parse_time(t_str):
    parts = t_str.split(':')
    return int(parts[0]) * 60 + float(parts[1])

items = []
for p in paragraphs:
    m = pattern.match(p.strip())
    if m:
        t_start = parse_time(m.group(1))
        t_end = parse_time(m.group(2))
        speech = m.group(3).strip()
        screen = m.group(4).strip() if m.group(4) else ""
        items.append({
            'start_str': m.group(1),
            'end_str': m.group(2),
            'start': t_start,
            'end': t_end,
            'speech': speech,
            'screen': screen
        })

print(f"Parsed {len(items)} speech cues:")
for i, it in enumerate(items):
    print(f"[{i:02d}] {it['start_str']} -> {it['end_str']} ({it['start']:.1f}s - {it['end']:.1f}s): {it['speech']}")
