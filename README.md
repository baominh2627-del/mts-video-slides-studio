# 🎬 MTS Video & Slides Studio (`DU_AN`)

Kho lưu trữ bộ công cụ tự động hóa sản xuất Video bài giảng Vật Lý 12, Slide TikTok/PDF, Ảnh bìa (Covers), Thuyết minh AI (TTS/Subtitles), Tự động hóa CapCut và Đồng bộ Google Drive của **MTS Education**.

👉 **Xem hướng dẫn tra cứu & Bộ Prompt mẫu tìm nhanh thư mục tại:** [`PROMPT_TIM_THU_MUC.md`](./PROMPT_TIM_THU_MUC.md)

---

## 📁 Cấu trúc thư mục

| Thư mục | Mô tả nội dung |
| :--- | :--- |
| **`01_Scripts_Code/`** | Toàn bộ mã nguồn được chia thành 6 nhóm chức năng: `render_video`, `slides_builder`, `covers_and_badges`, `audio_tts_subtitles`, `capcut_and_drive`, `web_demos`, `utils_and_tests` |
| **`02_San_Pham_Hoan_Chinh/`** | Thành phẩm đầu ra: Bộ Ảnh bìa TikTok (`Anh_Bia_TikTok`), Bộ Slide PDF/JPG (`Slides_Va_PDF`), File thuyết minh & Kịch bản timeline (`Audio_Va_Timeline`) |
| **`03_Tai_Nguyen_Goc/`** | Tài nguyên thiết kế gốc: Logo MTS & Font chữ (`Logo_Va_Font`), Hình minh họa Vật lý & Vivid Cards (`Hinh_Minh_Hoa_Vat_Ly`), Ảnh chụp giao diện Web (`Giao_Dien_Web_MTSedu`), Slide gốc (`Slides_Goc_Raw`) |
| **`FREE_MUSIC/`** | Dự án Web Đánh Đàn hợp âm (được quản lý trong repo Git riêng: [`baominh2627-del/free-music`](https://github.com/baominh2627-del/free-music)) |

---

## 🚀 Các nhóm công cụ chính trong `01_Scripts_Code`

1. **`render_video/`**: Dựng video bài giảng tự động bằng FFmpeg / OpenCV / MoviePy (Cân bằng nhiệt, Giải câu 16, Máy gia tốc Cyclotron, Phương trình Van der Waals, Đề thi HSG, Demo Web MTSedu...).
2. **`slides_builder/`**: Xử lý hình ảnh, xóa watermark, đóng dấu thương hiệu MTS Education và xuất bộ slide bài giảng Vật lý (Khí lý tưởng, Nhiệt học nâng cao, Ôn thi GKI...).
3. **`covers_and_badges/`**: Tự động thiết kế ảnh bìa chuẩn tỷ lệ TikTok, tạo khung thẻ công thức (`vivid_cards`) và huy hiệu logo chính thức.
4. **`audio_tts_subtitles/`**: Tạo giọng đọc thuyết minh tự động, ghép nhạc nền và sinh phụ đề `.ass`.
5. **`capcut_and_drive/`**: Điều khiển tự động giao diện CapCut PC để xuất video và script worker đồng bộ toàn bộ video lên Google Drive.
6. **`web_demos/`**: Trang web bài giảng tương tác `video_khi_thuc_vs_khi_ly_tuong.html` và giao diện thi thử HSA.
