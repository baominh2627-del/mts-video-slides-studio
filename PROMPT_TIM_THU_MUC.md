# 🧭 HƯỚNG DẪN & BỘ PROMPT TÌM NHANH CÁC THƯ MỤC / DỰ ÁN TRONG `DU_AN`

Tài liệu này lưu lại **cấu trúc thư mục sau khi dọn dẹp**, **danh sách các kho lưu trữ (GitHub Repositories)** và **các câu lệnh Prompt mẫu** để bạn copy-paste trực tiếp cho AI (Antigravity / ChatGPT / Cursor) mỗi khi cần tìm hoặc làm tiếp bất kỳ dự án nào.

---

## 📂 1. SƠ ĐỒ CẤU TRÚC THƯ MỤC `C:\Users\DELL\Documents\CODE\DU_AN`

```text
C:\Users\DELL\Documents\CODE\DU_AN\
├── 📁 01_Scripts_Code\                 # Toàn bộ mã nguồn Python, PowerShell, Web bài giảng
│   ├── 📁 render_video\                # Script dựng & render video bài giảng Vật Lý (Câu 16, Nhiệt, Cyclotron, Khí lý tưởng, Demo Web...)
│   ├── 📁 slides_builder\              # Script tạo slide TikTok, ôn thi GKI, HSG Vật lý, đọc DOCX & chạy OCR (run_ocr.ps1)
│   ├── 📁 covers_and_badges\           # Script tạo ảnh bìa TikTok, logo MTS overlay, vivid cards, xoá watermark/banner
│   ├── 📁 audio_tts_subtitles\         # Script tạo giọng đọc AI (TTS/gTTS), ghép audio nền, tạo phụ đề (.ass)
│   ├── 📁 capcut_and_drive\            # Script tự động hóa CapCut (UI automation, xuất video) & đồng bộ Google Drive (.json)
│   ├── 📁 web_demos\                   # Web bài giảng "Khí Thực vs Khí Lý Tưởng" (.html) & bản lưu Đề 4 HSA (NHAP_HSA_De4)
│   └── 📁 utils_and_tests\             # Các script kiểm tra frame, lọc màu, xử lý ảnh/watermark và script phụ trợ
│
├── 📁 02_San_Pham_Hoan_Chinh\          # Toàn bộ thành phẩm hoàn thiện (Ảnh bìa, Slide PDF/JPG, Audio gốc)
│   ├── 📁 Anh_Bia_TikTok\              # 9 ảnh bìa TikTok/TT chất lượng cao (.png): Cân bằng nhiệt, Câu 16, Cyclotron, Van der Waals...
│   ├── 📁 Slides_Va_PDF\               # Bộ slide hoàn chỉnh: TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation (.pdf + 23 ảnh), GKI slides, AR_RS_Slides.zip
│   └── 📁 Audio_Va_Timeline\           # File thu âm thuyết minh hoàn chỉnh (.wav, .mp3) và kịch bản phân cảnh (timeline.json, scenes_info.json)
│
├── 📁 03_Tai_Nguyen_Goc\               # Tài nguyên thiết kế gốc để tái sử dụng cho các video/slide mới
│   ├── 📁 Logo_Va_Font\                # Bộ logo MTS Education (trắng, cyan, trong suốt), favicon và font PlayfairDisplay.ttf
│   ├── 📁 Hinh_Minh_Hoa_Vat_Ly\        # Hình minh họa Vật lý (real_assets) và bộ thẻ công thức (vivid_cards, vivid_cards_v2)
│   ├── 📁 Giao_Dien_Web_MTSedu\        # Ảnh chụp màn hình giao diện Web/Mobile MTSedu (web_captures)
│   └── 📁 Slides_Goc_Raw\              # Ảnh slide gốc chưa qua xử lý (khi_ly_tuong_raw, tiktok_slides_raw)
│
├── 📁 FREE_MUSIC\                      # Dự án Web Đánh Đàn hợp âm (Repo riêng: baominh2627-del/free-music)
├── 📄 README.md                        # Tổng quan dự án & liên kết GitHub
└── 📄 PROMPT_TIM_THU_MUC.md            # File hướng dẫn & bộ Prompt tìm kiếm nhanh này
```

---

## 🌐 2. DANH SÁCH REPO GITHUB ĐÃ ĐỒNG BỘ

| Dự án / Nội dung | Đường dẫn trên máy (Local) | Link GitHub Repository |
| :--- | :--- | :--- |
| **Bộ công cụ Video, Slide TikTok & Vật Lý MTSedu** | `C:\Users\DELL\Documents\CODE\DU_AN` | https://github.com/baominh2627-del/mts-video-slides-studio |
| **Web Đánh Đàn Hợp Âm (Free Music)** | `C:\Users\DELL\Documents\CODE\DU_AN\FREE_MUSIC` | https://github.com/baominh2627-del/free-music |
| **Đề Thi Định Lượng HSA - Đề Số 4** | `C:\Users\DELL\Documents\CODE\DU_AN\01_Scripts_Code\web_demos\NHAP_HSA_De4` | https://github.com/baominh2627-del/de-4-hsa-dinh-luong-vnes |
| **Web MTSedu chính** | *(Trên GitHub)* | https://github.com/baominh2627-del/MTSedu |

---

## 🤖 3. BỘ PROMPT MẪU ĐỂ HỎI AI (COPY & PASTE KHI CẦN)

Khi mở phiên chat mới với AI, bạn chỉ cần **copy 1 trong các đoạn Prompt dưới đây** tùy theo công việc bạn muốn làm:

### 🔹 Prompt 1: Tìm & chỉnh sửa hoặc tạo mới Slide TikTok / Slide Ôn Thi Vật Lý
> ```text
> Hãy vào thư mục C:\Users\DELL\Documents\CODE\DU_AN:
> - Đọc các script tạo slide trong `01_Scripts_Code\slides_builder` (như build_gki_1206_slides.py, build_nhiet_nang_cao_slides.py, process_tiktok_slides.py)
> - Sử dụng logo/font trong `03_Tai_Nguyen_Goc\Logo_Va_Font`
> - Xuất kết quả mới vào `02_San_Pham_Hoan_Chinh\Slides_Va_PDF`.
> Yêu cầu của tôi: [Mô tả chủ đề slide mới bạn muốn tạo...]
> ```

### 🔹 Prompt 2: Tạo Ảnh Bìa (Cover) TikTok mới đồng bộ phong cách MTS Education
> ```text
> Hãy kiểm tra các script tạo ảnh bìa trong `C:\Users\DELL\Documents\CODE\DU_AN\01_Scripts_Code\covers_and_badges` (ví dụ generate_tiktok_cover.py, generate_cau16_cover.py, generate_cyclotron_cover.py) và các mẫu ảnh bìa hoàn chỉnh trong `02_San_Pham_Hoan_Chinh\Anh_Bia_TikTok`.
> Hãy tạo cho tôi một ảnh bìa TikTok mới với tiêu đề: "[Tên chủ đề]" và lưu vào `02_San_Pham_Hoan_Chinh\Anh_Bia_TikTok`.
> ```

### 🔹 Prompt 3: Render Video Bài Giảng Vật Lý / Ghép Audio Thuyết Minh & Phụ Đề
> ```text
> Hãy tham khảo các script dựng video trong `C:\Users\DELL\Documents\CODE\DU_AN\01_Scripts_Code\render_video`, các script xử lý giọng đọc/phụ đề trong `01_Scripts_Code\audio_tts_subtitles`, và tài nguyên gốc trong `03_Tai_Nguyen_Goc`.
> Tôi muốn dựng/chỉnh sửa video bài giảng về: [Mô tả yêu cầu video...]
> ```

### 🔹 Prompt 4: Tự động hóa CapCut hoặc Upload hàng loạt Video lên Google Drive
> ```text
> Hãy xem các script trong `C:\Users\DELL\Documents\CODE\DU_AN\01_Scripts_Code\capcut_and_drive` (đặc biệt là upload_all_videos_worker.py, upload_manifest.json, drive_folder_ids.json và các script điều khiển CapCut).
> Giúp tôi thực hiện: [Yêu cầu xuất video CapCut hoặc tiếp tục đồng bộ video lên Google Drive...]
> ```

### 🔹 Prompt 5: Tìm kiếm bất kỳ file hoặc tính năng cũ nào trong thư mục `DU_AN`
> ```text
> Hãy đọc file `C:\Users\DELL\Documents\CODE\DU_AN\PROMPT_TIM_THU_MUC.md` và `README.md` để nắm toàn bộ cấu trúc thư mục `DU_AN`, sau đó tìm giúp tôi các file liên quan đến [tên bài toán / chủ đề bạn cần tìm].
> ```

### 🔹 Prompt 6: Edit Video trên Google Drive (Chuẩn Ngang 16:9 - `1920x1080`, Full Edit & Phụ Đề Nhỏ Bên Dưới)
> ```text
> Làm việc tại `C:\Users\DELL\Documents\CODE\DU_AN`, tham khảo các script trong `01_Scripts_Code\render_video`, `01_Scripts_Code\audio_tts_subtitles`, `01_Scripts_Code\capcut_and_drive` và tài nguyên trong `03_Tai_Nguyen_Goc`. Dùng CLI `gdrive` (tài khoản `baominh2627@gmail.com`) để edit video trên Google Drive theo đúng các thông số sau:
>
> 1. Đầu vào từ Google Drive:
> - Video gốc: [Tên file / File ID / Link Google Drive hoặc thư mục cần tìm]
> - Dùng `gdrive readonly info` và `gdrive readonly download` tải video gốc (cùng file lời thoại/nhạc nền nếu có trên Drive) về thư mục tạm trong `DU_AN`, sau đó kiểm tra thông số bằng `ffprobe`.
>
> 2. Tỷ lệ khung hình & Quy cách xuất (BẮT BUỘC NGANG 16:9):
> - Xuất video chuẩn ngang 16:9 (`1920x1080`, `30fps`, `libx264`, `yuv420p`, `aac`). KHÔNG dùng kích thước dọc `1080x1920` của các script TikTok cũ.
> - Nếu video gốc khác tỷ lệ 16:9 thì [crop an toàn / thêm nền mờ 2 bên] để không méo hình.
>
> 3. Cắt ghép, Nhịp độ & Chuyển cảnh:
> - Cắt bỏ đoạn: [ghi mốc thời gian hoặc "tự phát hiện và cắt khoảng lặng/nói vấp"].
> - Tốc độ phát: [1.0x / 1.15x - 1.35x].
> - Chuyển cảnh & chuyển động: [jump cut / fade-dissolve mượt / zoom-in nhẹ tại điểm nhấn].
>
> 4. Âm thanh (Voice + Nhạc nền + SFX):
> - Giọng nói: [giữ giọng gốc lọc ồn & chuẩn hóa `loudnorm` / tạo lại bằng TTS].
> - Nhạc nền (BGM): [file hoặc thể loại nhạc], mix âm lượng nhỏ vừa phải không át giọng nói, có fade-in/out.
> - SFX: chèn hiệu ứng nhẹ ([whoosh / pop / ding]) ở điểm chuyển cảnh hoặc nhấn ý chính.
>
> 5. Hình ảnh, Màu sắc, Overlay & Branding:
> - Chỉnh màu/ánh sáng: [sáng rõ sạch nét kiểu bài giảng / tương phản cao / cinematic].
> - Branding: [gắn / không gắn] logo/watermark & Outro card từ `03_Tai_Nguyen_Goc\Logo_Va_Font` (căn tọa độ chuẩn 1920x1080).
> - B-roll / Minh họa: chèn [ảnh / thẻ công thức / text callout / B-roll AI] tại [các đoạn cần nhấn mạnh].
> - Ảnh bìa (Thumbnail 16:9): [Có / Không] tạo thêm thumbnail `1920x1080`.
>
> 6. Phụ đề nhỏ ở bên dưới:
> - Nguồn lời thoại: [file kịch bản có sẵn / AI tự nghe nhận diện giọng nói Whisper].
> - Tạo file `.ass` chuẩn `PlayResX: 1920`, `PlayResY: 1080`, `Alignment: 2` (căn giữa sát mép dưới), cỡ chữ nhỏ gọn (~34-40px), tối đa 1-2 dòng, `MarginV` thấp (~35-55px), [chữ trắng viền đen mảnh / có hộp nền mờ nhẹ], [có / không] highlight từ khóa. Burn cứng vào video và xuất kèm file `.ass`/`.srt`.
>
> 7. Kiểm tra & Cập nhật lại lên Google Drive:
> - Kiểm tra frame mẫu ở vài mốc thời gian để đảm bảo phụ đề nhỏ gọn, không che nội dung chính và khớp tiếng.
> - Đồng bộ lại lên Google Drive bằng: [`gdrive mutate update <FILE_ID> <file_moi.mp4>` (ghi đè giữ nguyên link cũ) / `gdrive mutate upload <file_moi.mp4> --parent <FOLDER_ID>` (upload bản mới)].
> - Sau khi upload thành công lên Drive, [xóa file tạm & video local để nhẹ máy / giữ lại tại ...].
> ```

---

## 💻 4. LỆNH POWERSHELL TÌM NHANH TRÊN MÁY (NẾU KHÔNG DÙNG AI)

Mở PowerShell tại `C:\Users\DELL\Documents\CODE\DU_AN` và chạy:

```powershell
# Tìm file theo từ khóa trong tên file (ví dụ: tìm tất cả file liên quan đến "cyclotron" hoặc "nhiet")
Get-ChildItem -Recurse -File | Where-Object { $_.Name -match "nhiet" } | Select-Object FullName

# Tìm script Python có chứa một đoạn chữ/tiêu đề cụ thể bên trong code
Get-ChildItem .\01_Scripts_Code -Recurse -Filter *.py | Select-String -Pattern "CÂN BẰNG NHIỆT"
```
