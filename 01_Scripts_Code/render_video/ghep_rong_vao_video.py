"""
Script ghép trực tiếp Con Rồng Nhảy (Toothless Dancing - đã tách nền trong suốt)
vào bất kỳ video bài giảng / TikTok nào bằng FFmpeg.

Cách dùng trên Terminal / PowerShell:
    py ghep_rong_vao_video.py --input "duong_dan_video_goc.mp4" --output "video_da_ghep_rong.mp4" --pos bottom-right --scale 0.35
"""
import argparse
import os
import subprocess

FFMPEG_EXE = r"C:\Users\DELL\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"

DRAGON_MOV = r"c:\Users\DELL\Documents\CODE\DU_AN\02_San_Pham_Hoan_Chinh\Video_Rong_Nhay\rong_nhay_trong_suot.mov"


def overlay_dragon(input_video: str, output_video: str, pos: str = "bottom-right", scale: float = 0.35, margin: int = 30, loop_dragon: bool = True):
    pos_map = {
        "bottom-right": f"W-w-{margin}:H-h-{margin}",
        "bottom-left": f"{margin}:H-h-{margin}",
        "top-right": f"W-w-{margin}:{margin}",
        "top-left": f"{margin}:{margin}",
        "center": "(W-w)/2:(H-h)/2",
    }
    overlay_expr = pos_map.get(pos, pos)
    dragon_w = int(1040 * scale)
    if dragon_w % 2 == 1:
        dragon_w += 1

    cmd = [FFMPEG_EXE, "-y", "-i", input_video]
    if loop_dragon:
        cmd += ["-stream_loop", "-1", "-i", DRAGON_MOV]
    else:
        cmd += ["-i", DRAGON_MOV]

    filter_complex = f"[1:v]scale={dragon_w}:-1[dragon];[0:v][dragon]overlay={overlay_expr}:shortest=1[outv]"
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-c:a", "copy",
        output_video,
    ]
    subprocess.run(cmd, check=True)
    print(f"Đã ghép rồng nhảy thành công vào: {output_video}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ghép con rồng nhảy (đã tách nền) vào video bất kỳ")
    parser.add_argument("--input", "-i", required=True, help="Đường dẫn video gốc")
    parser.add_argument("--output", "-o", required=True, help="Đường dẫn video xuất ra")
    parser.add_argument("--pos", default="bottom-right", help="Vị trí: bottom-right, bottom-left, top-right, top-left, center hoặc X:Y")
    parser.add_argument("--scale", type=float, default=0.35, help="Tỉ lệ thu phóng con rồng (mặc định 0.35)")
    parser.add_argument("--no-loop", action="store_true", help="Không lặp lại động tác nhảy nếu video dài hơn 10.3s")
    args = parser.parse_args()
    overlay_dragon(args.input, args.output, args.pos, args.scale, loop_dragon=not args.no_loop)
