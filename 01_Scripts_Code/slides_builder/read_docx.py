import zipfile, xml.etree.ElementTree as ET, sys

sys.stdout.reconfigure(encoding='utf-8')
docx_path = r"C:\Users\DELL\Documents\Downloads\Lời thuyết minh video giải Câu 16 (bản 3 phút 10 giây).docx"

with zipfile.ZipFile(docx_path) as z:
    xml_content = z.read("word/document.xml")
    tree = ET.fromstring(xml_content)
    # namespaces
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
        if texts:
            paragraphs.append("".join(texts))

print(f"Total paragraphs: {len(paragraphs)}")
print("\n--- CONTENT ---")
for idx, p in enumerate(paragraphs):
    print(f"[{idx}] {p}")
