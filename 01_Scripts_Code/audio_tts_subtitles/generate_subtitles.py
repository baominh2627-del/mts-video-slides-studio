import sys, zipfile, xml.etree.ElementTree as ET, re

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

pattern = re.compile(r'^(\d+:\d+(?:\.\d+)?)\s*[–-]\s*(\d+:\d+(?:\.\d+)?)\s+(.*?)(?:\s+Màn hình:\s*(.*))?$', re.IGNORECASE)

def parse_time(t_str):
    parts = t_str.split(':')
    return int(parts[0]) * 60 + float(parts[1])

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs == 100:
        s += 1
        cs = 0
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

items = []
for p in paragraphs:
    m = pattern.match(p.strip())
    if m:
        t_start = parse_time(m.group(1))
        t_end = parse_time(m.group(2))
        speech = m.group(3).strip()
        screen = m.group(4).strip() if m.group(4) else ""
        items.append({
            'start': t_start,
            'end': t_end,
            'speech': speech,
            'screen': screen
        })

print(f"Loaded {len(items)} items")

# Generate Advanced SubStation Alpha (.ass)
ass_header = """[Script Info]
Title: Giai Cau 16 - MTSEducation
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,38,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,50,50,140,1
Style: Highlight,Segoe UI,40,&H0038E5FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,50,50,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

events = []
for it in items:
    s_ass = format_ass_time(it['start'])
    e_ass = format_ass_time(it['end'])
    # clean speech text
    text = it['speech']
    # If text is too long, split into 2 lines
    if len(text) > 45:
        # split near middle
        words = text.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        text = f"{line1}\\N{line2}"
    
    events.append(f"Dialogue: 0,{s_ass},{e_ass},Default,,0,0,0,,{text}")

ass_content = ass_header + "\n".join(events) + "\n"

ass_file = r"c:\Users\DELL\Documents\CODE\DU_AN\subtitles_cau16.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write(ass_content)

print("Saved subtitles to:", ass_file)
