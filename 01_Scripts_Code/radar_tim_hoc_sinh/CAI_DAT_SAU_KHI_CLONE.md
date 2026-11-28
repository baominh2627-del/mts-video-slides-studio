# 🛠️ Hướng Dẫn Cài Đặt Sau Khi Clone Repo (`Radar Tìm Học Sinh v3.2`)

Tài liệu này hướng dẫn từng bước cho **người mới sau khi `git clone` dự án** để tự dựng bản **Radar Tìm Học Sinh** hoàn toàn riêng tư (tài khoản Firebase riêng, tên miền App riêng, mẫu bình luận riêng và danh sách Group Facebook riêng).

> **Ưu điểm:** Không cần cài Node.js/npm, không cần `pip install` thư viện ngoài — chỉ cần có sẵn **Python 3.9+** và **Google Chrome**.

---

## 0. Yêu cầu trước khi bắt đầu
- Máy tính Windows *(macOS/Linux vẫn chạy được bằng lệnh `python3 radar.py`)*.
- Đã cài **Python 3.9+** (kiểm tra bằng lệnh `python --version`).
- Trình duyệt **Google Chrome** đã đăng nhập sẵn Facebook cá nhân của bạn.
- Một tài khoản **Google (Gmail)** miễn phí để tạo Firebase (gói Spark $0/tháng).

---

## Bước 1 — Clone mã nguồn & mở thư mục dự án

```powershell
git clone https://github.com/baominh2627-del/mts-video-slides-studio.git
cd mts-video-slides-studio\01_Scripts_Code\radar_tim_hoc_sinh
```

Kiểm tra nhanh môi trường Python:
```powershell
python --version
```

---

## Bước 2 — Tạo dự án Firebase miễn phí của riêng bạn (~5 phút)

Mỗi người dùng cần **1 dự án Firebase riêng** để lưu bài viết và bắn thông báo đẩy về điện thoại/máy tính của chính mình.

1. Mở https://console.firebase.google.com → bấm **Create a project / Add project** → đặt tên bất kỳ (ví dụ `radar-gia-su-cua-toi`) → tạo xong dự án.
   - Ghi lại **Project ID** (dạng chữ thường không dấu, ví dụ `radar-gia-su-cua-toi`).
2. **Bật đăng nhập Google:**
   - Menu trái → **Security** *(hoặc Build)* → **Authentication** → bấm **Get started / To start**.
   - Chọn **Google** → gạt **Enable** → chọn **Support email** là Gmail của bạn → bấm **Save**.
3. **Tạo cơ sở dữ liệu Firestore:**
   - Menu trái → **Databases and storage** *(hoặc Build)* → **Firestore Database** → bấm **Create database**.
   - Chọn vị trí gần nhất **`asia-southeast1` (Singapore)** → **Next** → chọn **Start in production mode** → **Create**.
4. **Lấy 3 thông tin kết nối** trong menu trái **⚙️ Settings → Project settings**:
   - **① `firebaseConfig` (Tab `General`):**
     Kéo xuống mục **Your apps** → bấm biểu tượng **`</>` (Web)** → đặt tên bất kỳ (vd `Radar HS`) → **Register app** → copy đoạn `const firebaseConfig = { ... };`.
   - **② `VAPID Key` (Tab `Cloud Messaging`):**
     Đảm bảo **Firebase Cloud Messaging API (V1)** đang ở trạng thái **Activated/Enabled** → cuộn xuống mục **Web configuration → Web Push certificates** → bấm **Generate key pair** → copy chuỗi dài ở cột **Key pair** (bắt đầu bằng `B...`).
   - **③ Khóa `service-account.json` (Tab `Service accounts`):**
     Bấm **Generate new private key** → **Generate key** để tải file `.json` về máy.
     → **Đổi tên file đó thành `service-account.json`** và chép thẳng vào thư mục:
     `01_Scripts_Code\radar_tim_hoc_sinh\service-account.json`
     *(⚠️ File này đã nằm trong `.gitignore` — tuyệt đối không chia sẻ hay đẩy lên GitHub).*

---

## Bước 3 — Thay thông tin cá nhân vào 5 file cấu hình

Vì repo đang chứa địa chỉ dự án gốc của tác giả, bạn cần đổi sang thông tin **của riêng bạn** tại đúng **5 vị trí** sau:

| # | File cần sửa | Nội dung cần thay đổi |
| :---: | :--- | :--- |
| **1** | `app\public\firebase-config.js` | Thay toàn bộ `self.FIREBASE_CONFIG`, `self.VAPID_KEY`, và đổi `self.OWNER_EMAIL` thành **Gmail của bạn**. |
| **2** | `app\firestore.rules` | Đổi `"baominh2627@gmail.com"` ở dòng `request.auth.token.email == ...` thành **Gmail của bạn** (phải trùng khớp 100% với `OWNER_EMAIL`). |
| **3** | `extension_radar\popup.js` | Đổi URL `"https://tool-tu-dong-fb.web.app/"` ở dòng `$("#open-app").onclick` thành **`"https://<PROJECT-ID-CUA-BAN>.web.app/"`**. |
| **4** | `chay_ngam_radar.vbs` | Sửa đường dẫn `s.CurrentDirectory = "..."` thành **đường dẫn thực tế** thư mục `radar_tim_hoc_sinh` trên máy bạn (ví dụ `D:\radar_tim_hoc_sinh`). |
| **5** | `config.json` *(tạo mới từ file mẫu)* | Chạy lệnh `copy config.example.json config.json` rồi mở `config.json` sửa các mục dưới đây. |

### Chi tiết các mục cần điền trong `config.json`
Mở `config.json` (file này không đẩy lên Git) và cập nhật:
1. **`firebase.app_url`:** đổi thành `"https://<PROJECT-ID-CUA-BAN>.web.app"`.
2. **`mau_theo_mon`** (`toan`, `ly`, `hoa`) và **`mau_binh_luan_mac_dinh`:** thay bằng số Zalo, thành tích, học phí và lời giới thiệu của bạn.
3. **`bo_loc`:** giữ nguyên nếu bạn dạy **Toán / Lý / Hóa lớp 10–12 (online)**, hoặc tự thêm/bớt môn học, lớp học, từ khóa loại trừ theo nhu cầu của bạn.
4. **`gmail`** *(tuỳ chọn — có thể bỏ qua)*: bản `v3.2` quét trực tiếp từ tiện ích Chrome nên không bắt buộc dùng Gmail. Nếu muốn hết thông báo lỗi Gmail trong file log (hoặc muốn bật thêm kênh phụ đọc mail), thay `email` bằng Gmail của bạn và điền **Mật khẩu ứng dụng 16 ký tự** tạo tại https://myaccount.google.com/apppasswords.
5. **`ai`** *(tuỳ chọn)*: nếu muốn AI Gemini tự viết lại bình luận theo từng bài, đổi `"bat": true`, lấy API key miễn phí tại https://aistudio.google.com/apikey dán vào `gemini_api_key` và điền thông tin vào `ho_so_gia_su`.

---

## Bước 4 — Đưa Web App (PWA) lên mạng (~3 giây)

Tại thư mục `01_Scripts_Code\radar_tim_hoc_sinh`, chạy đúng 1 lệnh:

```powershell
python deploy.py
```

Kết quả thành công sẽ hiện:
```text
✅ Đã cập nhật Firestore Rules (...)
✅ Đã đưa Web App lên mạng (...): https://<PROJECT-ID-CUA-BAN>.web.app
```

---

## Bước 5 — Cài App lên Máy tính & Điện thoại và lưu 3 mẫu bình luận

1. **Trên máy tính (Chrome / Edge):**
   - Mở địa chỉ `https://<PROJECT-ID-CUA-BAN>.web.app` → bấm **Đăng nhập bằng Google** (dùng đúng Gmail đã điền ở Bước 3).
   - Bấm nút **🔔 Bật thông báo** ở góc trên bên phải → chọn **Cho phép (Allow)**.
   - Cuộn xuống mục **📌 Mẫu bình luận nhanh** ở cuối trang → dán 3 mẫu Toán / Lý / Hóa của bạn → bấm **💾 Lưu chỉnh sửa** để đồng bộ lên điện thoại.
   - *(Tuỳ chọn)* Bấm biểu tượng **Cài đặt ứng dụng** trên thanh địa chỉ trình duyệt để ghim thành app riêng trên Desktop.
2. **Trên điện thoại:**
   - **Android (Chrome):** Mở link app → menu `⋮` → **Cài đặt ứng dụng / Thêm vào màn hình chính** → mở app → đăng nhập → bấm **🔔 Bật thông báo**.
   - **iPhone (Safari, iOS 16.4+):** Mở link app bằng Safari → bấm nút **Chia sẻ** → **Thêm vào MH chính** → mở app từ biểu tượng ngoài màn hình chính → đăng nhập → bấm **🔔 Bật thông báo**.

### Kiểm tra kết nối thông báo đẩy (Test ngay)
Chạy lệnh sau trên máy tính:
```powershell
python radar.py --test-notify
```
Nếu thấy dòng `→ app: OK` và cả **điện thoại + máy tính đều rung/hiện thông báo thử**, phần kết nối Firebase đã hoàn tất 100%! *(Sau khi test xong, bấm **Bỏ qua** trên thẻ thử nghiệm để ẩn đi).*

---

## Bước 6 — Cài Tiện ích Chrome `extension_radar` & chọn Group canh

1. Mở tab mới trên Chrome, gõ **`chrome://extensions`** → nhấn `Enter`.
2. Gạt bật **Chế độ dành cho nhà phát triển** *(Developer mode)* ở góc trên bên phải.
3. Bấm **Tải tiện ích đã giải nén** *(Load unpacked)* → chọn thư mục:
   `...\01_Scripts_Code\radar_tim_hoc_sinh\extension_radar`
4. Bấm biểu tượng mảnh ghép 🧩 góc phải thanh công cụ Chrome → ghim tiện ích **Radar Tìm Học Sinh** ra ngoài cho dễ nhìn.
5. **Chống Chrome ngủ đông Facebook (rất quan trọng):**
   - Vào **`chrome://settings/performance`** → mục **Luôn giữ cho các trang web này hoạt động** → bấm **Thêm** → nhập **`facebook.com`** → lưu lại.

---

## Bước 7 — Khởi động Radar chạy ngầm & chọn các Group ruột

1. **Bật dịch vụ Python chạy ngầm:**
   - Nhấp đúp file **`chay_ngam_radar.vbs`** (chạy ẩn hoàn toàn dưới nền) hoặc **`chay_radar.bat`** (hiện cửa sổ xem log trực tiếp).
   - Nhìn icon tiện ích trên Chrome chuyển sang chữ **`ON` màu xanh lá** là kết nối thành công.
   - *(Mẹo tự bật cùng Windows: nhấn `Win + R` → gõ `shell:startup` → Enter → copy shortcut của `chay_ngam_radar.vbs` vào thư mục vừa mở).*
2. **Tích chọn danh sách Group Tìm Gia Sư của bạn:**
   - Bấm icon **`ON`** trên Chrome → bấm **`☑️ Tích chọn các Nhóm để canh`**.
   - Bấm **`Bỏ tích hết`** *(để xóa các nhóm mặc định cũ nếu muốn)* → bấm **`🔍 Mở danh sách Nhóm trên FB để tự quét tên nhóm`** → cuộn trang `facebook.com/groups/joins/` vài nhịp để lấy đủ 100% nhóm bạn đã tham gia.
   - Quay lại tab chọn nhóm, tích **`☑️`** khoảng **6–10 Group chất lượng nhất** (nhiều học sinh/phụ huynh thật đăng bài).
3. **Bắt đầu canh tự động:**
   - Bấm icon **`ON`** → chọn **Chế độ 1: Xoay vòng Group** (nên để **2 phút** hoặc **3 phút** để tiện ích đủ thời gian mở *"Xem thêm"* và cuộn quét sạch mọi bài dưới 2 ngày) → bấm **`⏭ Chuyển nhóm ngay`** 1 lần.

---

## Kiểm tra nhanh & Xử lý lỗi thường gặp

```powershell
# Thử bộ lọc với 1 câu bất kỳ xem ĐẠT hay BỎ QUA:
python radar.py --test-text "Em cần tìm gia sư Lý 12 học online ạ"

# Xem 30 dòng nhật ký mới nhất:
Get-Content -Encoding UTF8 radar.log -Tail 30
```

| Lỗi thường gặp | Cách xử lý nhanh |
| :--- | :--- |
| `Chưa có config.json` | Bạn chưa tạo file ở Bước 3. Chạy `copy config.example.json config.json` rồi điền thông tin. |
| `FileNotFoundError: service-account.json` | Tải khóa riêng tư từ Firebase (*Settings → Service accounts*), đổi đúng tên thành `service-account.json` đặt cùng thư mục với `radar.py`. |
| Đăng nhập Web App báo *không có quyền* hoặc *Missing permissions* | Kiểm tra Gmail trong `app/public/firebase-config.js` (`OWNER_EMAIL`) và `app/firestore.rules` phải giống hệt nhau, sau đó chạy lại `python deploy.py`. |
| Icon tiện ích báo **`OFF` màu đỏ** | Tiến trình `radar.py` chưa chạy — nhấp đúp `chay_ngam_radar.vbs` để bật lại. |
| Đã sửa code trong `extension_radar/` nhưng không thấy thay đổi | Vào `chrome://extensions` bấm nút xoay tròn **🔄 (Tải lại)** ở thẻ tiện ích. |

👉 Xem thêm giải thích nguyên lý 5 tầng lọc & mẹo tối ưu thực chiến tại [HUONG_DAN.md](./HUONG_DAN.md).
