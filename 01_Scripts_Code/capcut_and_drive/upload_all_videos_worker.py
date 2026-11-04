import subprocess, os, sys, json, time

sys.stdout.reconfigure(encoding='utf-8')

TRACKER_FILE = r"C:\Users\DELL\Documents\CODE\DU_AN\upload_tracker.json"
PROGRESS_FILE = r"C:\Users\DELL\Documents\CODE\DU_AN\upload_live_progress.txt"

def load_tracker():
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tracker(data):
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def upload_file(file_path, parent_id):
    ps_cmd = f'& gdrive mutate upload "{file_path}" --parent "{parent_id}"'
    res = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, encoding='utf-8')
    for line in res.stdout.splitlines():
        if "Uploaded:" in line and "ID:" in line:
            fid = line.split("ID:")[1].strip().rstrip(")")
            return fid, None
    err = res.stderr.strip() or res.stdout.strip()
    return None, err

def delete_to_recycle_bin(file_path):
    # Escape quotes if any
    safe_path = file_path.replace('"', '`"')
    ps_del = f'Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile("{safe_path}", "OnlyErrorDialogs", "SendToRecycleBin")'
    res = subprocess.run(['powershell', '-Command', ps_del], capture_output=True, text=True, encoding='utf-8')
    if os.path.exists(file_path):
        # Fallback to os.remove if still exists
        try:
            os.remove(file_path)
        except Exception as e:
            return False, str(e)
    return True, None

def main():
    data = load_tracker()
    items = data["items"]
    total_files = len(items)
    total_bytes = data["total_bytes"]
    
    # Category priority order
    cat_priority = {
        "06_Du_An_Video_Giao_Duc": 1,
        "05_Hoc_Tap_Dai_Hoc_UET": 2,
        "07_Camera_Roll_Laptop": 3,
        "03_Day_Hoc_Va_Gia_Su": 4,
        "04_Quay_Man_Hinh_PC": 5,
        "01_Bo_Nho_Dien_Thoai/Redmi_Note_12": 6,
        "01_Bo_Nho_Dien_Thoai/Redmi_Note_11S": 7,
        "02_GoogleDrive_Videos_Goc": 8
    }
    
    # Sort items by category priority then file size
    items.sort(key=lambda x: (cat_priority.get(x["category"], 99), x["size"]))
    
    uploaded_bytes = sum(i["size"] for i in items if i["status"] in ("UPLOADED", "DELETED"))
    uploaded_count = sum(1 for i in items if i["status"] in ("UPLOADED", "DELETED"))
    deleted_count = sum(1 for i in items if i["status"] == "DELETED")
    
    print(f"=== BẮT ĐẦU TIẾN TRÌNH TỰ ĐỘNG UPLOAD & DỌN DẸP ===")
    print(f"Tổng số: {total_files} video | Dung lượng: {total_bytes / (1024**3):.2f} GB")
    print(f"Đã xử lý trước đó: {uploaded_count}/{total_files} ({uploaded_bytes / (1024**3):.2f} GB)\n")

    start_time = time.time()
    
    for idx, item in enumerate(items, 1):
        if item["status"] == "DELETED":
            continue
            
        fpath = item["path"]
        fname = item["filename"]
        fsize = item["size"]
        parent_id = item["parent_id"]
        cat = item["category"]
        
        # Check if already uploaded single test file earlier
        if fname == "WIN_20260410_02_05_07_Pro.mp4" and not os.path.exists(fpath):
            item["status"] = "DELETED"
            item["drive_id"] = "1ZhHsMkypQAV5C7y61sj4386U8uwLRJKZ"
            deleted_count += 1
            uploaded_count += 1
            uploaded_bytes += fsize
            continue

        if not os.path.exists(fpath):
            # File already removed or missing
            item["status"] = "MISSING"
            continue

        print(f"[{idx}/{total_files}] Uploading: [{cat}] {fname} ({fsize/(1024*1024):.2f} MB)...")
        
        # Retry loop
        success = False
        drive_id = None
        for attempt in range(1, 4):
            drive_id, err = upload_file(fpath, parent_id)
            if drive_id:
                success = True
                break
            print(f"   [Thử lại {attempt}/3] Lỗi upload: {err}. Chờ 3s...")
            time.sleep(3)
            
        if success:
            item["status"] = "UPLOADED"
            item["drive_id"] = drive_id
            uploaded_count += 1
            uploaded_bytes += fsize
            
            # Now delete safely to recycle bin
            del_ok, del_err = delete_to_recycle_bin(fpath)
            if del_ok:
                item["status"] = "DELETED"
                deleted_count += 1
                del_msg = "ĐÃ CHUYỂN THÙNG RÁC"
            else:
                del_msg = f"LỖI XÓA: {del_err}"
                
            elapsed = time.time() - start_time
            pct = (uploaded_bytes / total_bytes) * 100
            status_line = (f"-> XONG ({drive_id}) | {del_msg} | "
                           f"Tiến độ: {pct:.1f}% ({uploaded_bytes/(1024**3):.2f}/{total_bytes/(1024**3):.2f} GB) - "
                           f"{uploaded_count}/{total_files} video")
            print(f"   {status_line}\n")
            
            # Write live status to file
            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                pf.write(f"Tiến độ: {pct:.2f}%\n"
                         f"Đã tải & dọn dẹp: {uploaded_count}/{total_files} video ({uploaded_bytes/(1024**3):.2f} GB)\n"
                         f"File gần nhất: {fname}\n"
                         f"Nhóm: {cat}\n"
                         f"Thời gian đã chạy: {int(elapsed)}s\n")
        else:
            item["status"] = "FAILED"
            item["error"] = err
            print(f"   ❌ THẤT BẠI sau 3 lần: {fname} -> {err}\n")

        # Save tracker every 5 files
        if idx % 5 == 0:
            data["uploaded_bytes"] = uploaded_bytes
            data["uploaded_files"] = uploaded_count
            data["deleted_files"] = deleted_count
            save_tracker(data)

    # Final save
    data["uploaded_bytes"] = uploaded_bytes
    data["uploaded_files"] = uploaded_count
    data["deleted_files"] = deleted_count
    save_tracker(data)
    
    print("\n==========================================")
    print(f"HOÀN TẤT TOÀN BỘ TIẾN TRÌNH!")
    print(f"Đã upload và dọn dẹp an toàn: {uploaded_count}/{total_files} video ({uploaded_bytes/(1024**3):.2f} GB)")
    print("==========================================")

if __name__ == "__main__":
    main()
