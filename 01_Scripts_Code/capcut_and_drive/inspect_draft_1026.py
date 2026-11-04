import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')
proj_dir = r"C:/Users/DELL/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1026 (1)"
print("Files in project:", os.listdir(proj_dir))
content_path = os.path.join(proj_dir, "draft_content.json")
with open(content_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Duration (us):", data.get("duration"))
print("Canvas config:", data.get("canvas_config"))
print("FPS:", data.get("fps"))
materials = data.get("materials", {})
print("\nVideos:")
for v in materials.get("videos", []):
    print("  id:", v.get("id"), "path:", v.get("path"), "duration:", v.get("duration"), f"{v.get('width')}x{v.get('height')}")

print("\nAudios:")
for a in materials.get("audios", []):
    print("  id:", a.get("id"), "name:", a.get("name"), "path:", a.get("path"), "duration:", a.get("duration"))

print("\nSpeeds:")
for s in materials.get("speeds", []):
    print("  id:", s.get("id"), "speed:", s.get("speed"))

print("\nTracks:")
for idx, tr in enumerate(data.get("tracks", [])):
    print(f"Track {idx} ({tr.get('type')}):")
    for seg in tr.get("segments", []):
        print("   material_id:", seg.get("material_id"))
        print("   target_timerange:", seg.get("target_timerange"))
        print("   source_timerange:", seg.get("source_timerange"))
        print("   speed:", seg.get("speed"))
        print("   volume:", seg.get("volume"))
        print("   extra_material_refs:", seg.get("extra_material_refs"))
