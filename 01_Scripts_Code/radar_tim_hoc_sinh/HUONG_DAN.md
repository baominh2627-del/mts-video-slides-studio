# 📡 Radar tìm học sinh

Tự phát hiện bài **tìm gia sư Toán / Lý / Hóa 10–12 (online)** mới trong các Group Facebook → đẩy **thông báo về app riêng của bạn** trên **điện thoại + máy tính** → bạn bấm **"Copy & mở bài"** rồi tự bình luận.

Tool chỉ đọc **email thông báo** Facebook gửi vào Gmail của bạn, không đăng nhập hay thao tác gì trên Facebook.

```
Facebook ──email──▶ Gmail ──▶ radar.py (máy tính bạn) ──▶ Firebase ──push──▶ App (điện thoại + PC)
                               lọc + AI soạn bình luận      lưu bài
```

## Cấu trúc
| File | Vai trò |
|---|---|
| `radar.py` | Đọc Gmail, lọc bài, soạn bình luận, gửi thông báo |
| `firebase_app.py` | Lưu bài vào Firestore + gửi push (FCM) |
| `config.example.json` | Cấu hình mẫu (từ khoá, kênh thông báo...) |
| `app/public/` | Web app (PWA) cài được lên điện thoại & máy tính |
| `app/firestore.rules` | Chỉ tài khoản của bạn đọc/ghi được dữ liệu |

## Quy tắc lọc hiện tại
1. **Bỏ** nếu có: `offline`, `off`, `trực tiếp`, `dạy/học ở nhà`, `tại nhà`, `đến nhà`, `kèm 1:1`, `1:1`, `1-1`, `nhận dạy`, `tuyển gia sư`, `đã tìm được`…
2. **Phải có** cụm nhu cầu: `tìm gia sư`, `cần gs`, `tìm thầy/cô`…
3. **Phải có** môn: `Toán`, `Lý`, `Hóa` (có dấu hay không dấu đều được).
4. **Lớp**: ghi lớp 10/11/12 → nhận; **không ghi lớp → vẫn nhận**; ghi lớp khác (8, 9…) → bỏ.

Thêm/bớt từ khoá: sửa `bo_loc` trong `config.json`. `cum_de_nham` là các cụm bị xoá trước khi tìm môn (ví dụ "toàn bộ" không bị hiểu là "Toán", "Thanh Hóa" không bị hiểu là "Hóa").

Thử nhanh bộ lọc: `python radar.py --test-text "Cần tìm gia sư hóa 11 online"`

---

## Cài đặt (làm 1 lần, ~20 phút)

### Bước 1 — Facebook & Gmail
1. Với mỗi Group: **🔔 Thông báo → Tất cả bài viết**. Trong *Cài đặt → Thông báo → Email*, bật email cho **Nhóm**.
2. Bật xác minh 2 bước Google → tạo **mật khẩu ứng dụng** tại https://myaccount.google.com/apppasswords

### Bước 2 — Tạo project Firebase (miễn phí, gói Spark)
1. Vào https://console.firebase.google.com → **Add project**.
2. **Build → Authentication → Get started → Google → Enable**.
3. **Build → Firestore Database → Create database** (production mode, khu vực `asia-southeast1`).
4. **Project settings → General → Your apps → Web (`</>`)** → đăng ký app → copy `firebaseConfig` vào `app/public/firebase-config.js`.
5. **Project settings → Cloud Messaging → Web Push certificates → Generate key pair** → copy vào `VAPID_KEY`.
6. **Project settings → Service accounts → Generate new private key** → lưu file vào thư mục này với tên `service-account.json` (**không chia sẻ file này**).
7. Sửa email của bạn trong `firebase-config.js` (`OWNER_EMAIL`) và `app/firestore.rules`.

### Bước 3 — Đưa app lên mạng
```powershell
cd 01_Scripts_Code\radar_tim_hoc_sinh
python deploy.py
```
App sẽ chạy tại địa chỉ `https://tool-tu-dong-fb.web.app`.

### Bước 4 — Cài app lên thiết bị
- **Máy tính (Chrome/Edge):** mở địa chỉ app → biểu tượng **Cài đặt** trên thanh địa chỉ → đăng nhập → **🔔 Bật thông báo**.
- **Android (Chrome):** mở link → menu ⋮ → **Thêm vào màn hình chính / Cài đặt ứng dụng** → mở app → **Bật thông báo**.
- **iPhone (iOS 16.4+, Safari):** mở link → **Chia sẻ → Thêm vào MH chính** → mở app **từ màn hình chính** → **Bật thông báo**.

Mỗi thiết bị bấm "Bật thông báo" một lần là sẽ nhận được thông báo.

### Bước 5 — Chạy radar
```powershell
cd 01_Scripts_Code\radar_tim_hoc_sinh
copy config.example.json config.json      # rồi điền Gmail + app_password
python radar.py --test-notify             # điện thoại + máy tính phải hiện thông báo thử
python radar.py --once --dry-run          # quét Gmail, chỉ in ra màn hình
python radar.py                           # chạy thật, quét mỗi 3 phút
```
Muốn tự chạy khi bật máy: dùng **Task Scheduler** → chạy `pythonw radar.py` khi đăng nhập (Start in = thư mục này).

### Tuỳ chọn
- **AI soạn bình luận:** lấy key tại https://aistudio.google.com/apikey → `"ai": {"bat": true, ...}` và điền `ho_so_gia_su`.
- **Gửi thêm Telegram:** `"kenh_thong_bao": ["app", "telegram"]`.

> ⚠️ Radar chạy trên máy tính của bạn, nên **tắt máy thì không có thông báo**. Sau này có thể chuyển lên chạy trên cloud.
