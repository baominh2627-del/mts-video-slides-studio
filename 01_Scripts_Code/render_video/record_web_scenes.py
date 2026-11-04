# -*- coding: utf-8 -*-
import os
import sys
import time
from playwright.sync_api import sync_playwright
import imageio_ffmpeg
import subprocess

sys.stdout.reconfigure(encoding='utf-8')
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
RECORD_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\web_records"
os.makedirs(RECORD_DIR, exist_ok=True)

def record_scene(name, duration_sec, action_func):
    temp_dir = os.path.join(RECORD_DIR, f"temp_{name}")
    os.makedirs(temp_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        # Standard 16:9 1280x720 recording of the web app
        ctx = browser.new_context(
            record_video_dir=temp_dir,
            record_video_size={'width': 1280, 'height': 720},
            viewport={'width': 1280, 'height': 720}
        )
        page = ctx.new_page()
        
        # Execute custom actions
        action_func(page, duration_sec)
        
        ctx.close()
        browser.close()
        
    # Find the recorded webm
    webms = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.webm')]
    if not webms:
        raise RuntimeError(f"No webm recorded for {name}")
    
    final_mp4 = os.path.join(RECORD_DIR, f"{name}.mp4")
    # Convert to mp4 at exact duration and 30fps
    cmd = [
        ffmpeg, '-y',
        '-i', webms[0],
        '-t', str(duration_sec),
        '-r', '30',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        final_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Recorded scene {name} -> {final_mp4} ({duration_sec}s)")

# Scene 1: Home page & brand
def action_scene_1(page, dur):
    page.goto('https://mtsedu.vercel.app', wait_until='networkidle')
    page.wait_for_timeout(3000)
    page.mouse.move(640, 360)
    page.wait_for_timeout(1000)
    page.mouse.move(300, 480)
    page.wait_for_timeout(int((dur - 4) * 1000))

# Scene 2: THPT Subjects
def action_scene_2(page, dur):
    page.goto('https://mtsedu.vercel.app', wait_until='networkidle')
    page.wait_for_timeout(1000)
    # Math
    page.click('text=Toán Học')
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(1500)
    # Physics
    page.click('text=Vật Lý')
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(1500)
    # Chemistry
    page.click('text=Hóa Học')
    page.wait_for_timeout(1500)
    # Mock exams
    page.click('text=Thi thử TNTHPT')
    page.wait_for_timeout(2500)

# Scene 3: Specialized Exams
def action_scene_3(page, dur):
    page.goto('https://mtsedu.vercel.app', wait_until='networkidle')
    page.wait_for_timeout(1000)
    # HSA
    page.click('text=Đề thi HSA')
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, 400)
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, 500)
    page.wait_for_timeout(2000)
    # TSA
    page.click('text=Đề thi TSA')
    page.wait_for_timeout(2000)
    # V-ACT
    page.click('text=Đề thi V-ACT')
    page.wait_for_timeout(2500)

# Scene 4: Real Quiz taking
def action_scene_4(page, dur):
    url = 'https://baominh2627-del.github.io/bai-ktra-vat-ly-nhiet-ly-12/?mtsedu_user=hocsinh2k9&mtsedu_name=Th%E1%BB%A7+Khoa+2K9'
    page.goto(url, wait_until='networkidle')
    page.wait_for_timeout(1000)
    page.click('#btn-start-exam')
    page.wait_for_timeout(1000)
    
    # Click Question 1 Option A
    opts = page.locator('.option-label')
    if opts.count() > 0:
        opts.nth(0).click()
        page.wait_for_timeout(1200)
    
    # Scroll to Question 2
    page.mouse.wheel(0, 250)
    page.wait_for_timeout(800)
    if opts.count() > 6:
        opts.nth(6).click()
        page.wait_for_timeout(1200)
        
    # Scroll to Question 3
    page.mouse.wheel(0, 250)
    page.wait_for_timeout(800)
    if opts.count() > 9:
        opts.nth(9).click()
        page.wait_for_timeout(1500)

# Scene 5: 100% Free highlights
def action_scene_5(page, dur):
    page.goto('https://mtsedu.vercel.app', wait_until='networkidle')
    page.wait_for_timeout(1000)
    page.click('text=Đề thi HSA')
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(2500)
    page.click('text=Vật Lý')
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(2000)

# Scene 6: Contact & CTA
def action_scene_6(page, dur):
    page.goto('https://mtsedu.vercel.app', wait_until='networkidle')
    page.wait_for_timeout(2000)
    page.mouse.move(250, 480)
    page.wait_for_timeout(1500)
    page.mouse.move(360, 480)
    page.wait_for_timeout(1500)
    page.mouse.move(460, 480)
    page.wait_for_timeout(1500)
    # Scroll down to contact buttons
    page.mouse.wheel(0, 200)
    page.wait_for_timeout(3500)

if __name__ == '__main__':
    record_scene('scene_1', 8.0, action_scene_1)
    record_scene('scene_2', 12.5, action_scene_2)
    record_scene('scene_3', 13.0, action_scene_3)
    record_scene('scene_4', 8.5, action_scene_4)
    record_scene('scene_5', 10.5, action_scene_5)
    record_scene('scene_6', 12.0, action_scene_6)
    print("ALL SCENES RECORDED SUCCESSFULLY!")
