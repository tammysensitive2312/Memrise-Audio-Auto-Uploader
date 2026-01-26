# 🎵 Memrise Audio Uploader

Công cụ tự động upload file âm thanh lên Memrise Community Courses sử dụng Selenium WebDriver.

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cấu hình](#-cấu-hình)
- [Chuẩn bị dữ liệu](#-chuẩn-bị-dữ-liệu)
- [Sử dụng](#-sử-dụng)
- [Xử lý lỗi](#-xử-lý-lỗi)
- [Lưu ý quan trọng](#-lưu-ý-quan-trọng)

## ✨ Tính năng

- ✅ Tự động đăng nhập vào Memrise
- ✅ Upload hàng loạt file MP3 theo tên từ vựng
- ✅ Tự động chuẩn hóa tên file về chữ thường
- ✅ Hiển thị tiến độ upload realtime
- ✅ Ghi log chi tiết các từ bị lỗi
- ✅ Xử lý ngoại lệ và báo cáo đầy đủ

## 🖥️ Yêu cầu hệ thống

- **Python**: 3.7 trở lên
- **Hệ điều hành**: Windows
- **Trình duyệt**: Google Chrome (phiên bản mới nhất)
- **Kết nối Internet**: Ổn định

## 📦 Cài đặt

### Bước 1: Clone hoặc tải xuống script

```bash
git clone <repository-url>
cd memrise-audio-uploader
```

### Bước 2: Cài đặt các thư viện Python cần thiết

```bash
pip install selenium webdriver-manager
```

Hoặc tạo file `requirements.txt`:

```txt
selenium==4.15.0
webdriver-manager==4.0.1
```

Sau đó chạy:

```bash
pip install -r requirements.txt
```

## ⚙️ Cấu hình

Mở file script và chỉnh sửa phần **CẤU HÌNH** ở đầu file:

```python
# --- 1. CẤU HÌNH ---
USERNAME = "your_email@example.com"      # Email đăng nhập Memrise
PASSWORD = "your_password_here"           # Mật khẩu
DATABASE_URL = "https://community-courses.memrise.com/course/6714335/m/edit/database/7775210/"
```

### Cách lấy DATABASE_URL:

1. Đăng nhập vào Memrise Community Courses
2. Vào khóa học của bạn
3. Chọn **Edit Course** → **Database**
4. Copy URL trên thanh địa chỉ trình duyệt
5. Dán vào biến `DATABASE_URL`

## 📂 Chuẩn bị dữ liệu

### Cấu trúc thư mục

Tạo thư mục `audios` trong cùng thư mục với script:

```
memrise-audio-uploader/
│
├── script.py
└── audios/
    ├── hello.mp3
    ├── world.mp3
    ├── python.mp3
    └── ...
```

### Quy tắc đặt tên file

- **Tên file MP3 phải trùng khớp CHÍNH XÁC với từ vựng trong Database**
- Ví dụ: Nếu từ vựng là `hello`, file phải là `hello.mp3`
- **Chữ hoa/thường**: Script tự động chuẩn hóa về chữ thường
  - `Hello.mp3` → tự động đổi thành `hello.mp3`
  - `WORLD.MP3` → tự động đổi thành `world.mp3`

### Chuẩn bị Database trên Memrise

Đảm bảo trong Database của khóa học có:

| Column 1 (Word) | Column 2 (Definition) |
|-----------------|----------------------|
| hello           | xin chào             |
| world           | thế giới             |
| python          | con trăn / ngôn ngữ  |

## 🚀 Sử dụng

### Chạy script

```bash
python script.py
```

### Quy trình thực hiện

1. **Khởi tạo trình duyệt Chrome**
2. **Đăng nhập tự động** vào Memrise
3. **Chuẩn hóa tên file** về chữ thường
4. **Upload từng file âm thanh** theo tên từ vựng
5. **Hiển thị tiến độ** realtime: `[1/50] Đang xử lý từ: 'hello' ... ✅ Thành công!`
6. **Tạo file log lỗi** nếu có từ không tìm thấy

### Ví dụ output

```
🚀 BẮT ĐẦU KHỞI CHẠY CHƯƠNG TRÌNH...
🌐 [BƯỚC 1] Đang khởi tạo trình duyệt Chrome...
🔑 [BƯỚC 2] Đang truy cập trang đăng nhập Memrise...
⏳ Đang điền thông tin đăng nhập...
✅ Đăng nhập thành công! Đã vào Dashboard.
📂 [BƯỚC 3.1] Đang chuẩn hóa tên file về chữ thường (lowercase)...
 -> Đã đổi tên 3 file.
📂 [BƯỚC 3.2] Đang tải cơ sở dữ liệu khóa học...
🎯 [BƯỚC 4] Bắt đầu quá trình Upload 50 file âm thanh...
--------------------------------------------------
[1/50] Đang xử lý từ: 'hello' ... ✅ Thành công!
[2/50] Đang xử lý từ: 'world' ... ✅ Thành công!
[3/50] Đang xử lý từ: 'python' ... ❌ THẤT BẠI (Không tìm thấy từ trên Web)
--------------------------------------------------
📝 [BƯỚC 5] Đang tổng hợp lỗi...
⚠️ Đã ghi lại 1 từ bị lỗi vào file 'error_log.txt'
🎉 HOÀN TẤT TOÀN BỘ QUÁ TRÌNH!
Nhấn Enter để đóng trình duyệt...
```

## 🔧 Xử lý lỗi

### File `error_log.txt`

Khi có từ không upload được, script tự động ghi vào file `error_log.txt`:

```
--- LOG LỖI NGÀY: 2025-01-27 14:30:15 ---
Không tìm thấy hoặc lỗi: python
Không tìm thấy hoặc lỗi: selenium
```

### Nguyên nhân lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| ❌ Không tìm thấy từ | Từ không tồn tại trong Database | Kiểm tra lại tên từ trong Memrise |
| ❌ Timeout | Mạng chậm hoặc trang load lâu | Tăng `WebDriverWait` timeout lên 30s |
| ❌ File không tồn tại | Tên file sai hoặc thiếu file | Đảm bảo file MP3 có trong thư mục `audios/` |

### Điều chỉnh timeout

Nếu mạng chậm, tăng thời gian chờ:

```python
wait = WebDriverWait(driver, 30)  # Tăng từ 15s lên 30s
```

## ⚠️ Lưu ý quan trọng

### Bảo mật

- ⚠️ **KHÔNG commit file chứa USERNAME và PASSWORD lên Git**
- Sử dụng biến môi trường hoặc file `.env`:

```python
import os
USERNAME = os.getenv("MEMRISE_EMAIL")
PASSWORD = os.getenv("MEMRISE_PASSWORD")
```

### Giới hạn upload

- Memrise có thể giới hạn số lượng upload trong 1 phiên
- Nếu upload quá nhiều file, script có thể bị chặn tạm thời
- Khuyến nghị: Upload không quá 100 file/lần

### Khắc phục sự cố

#### Chrome không tự động tải ChromeDriver

```bash
# Cài đặt thủ công
pip install --upgrade webdriver-manager
```

#### Script bị treo ở bước login

- Kiểm tra kết nối Internet
- Đảm bảo tài khoản Memrise hợp lệ
- Thử đăng nhập thủ công trước để kiểm tra

#### File không upload được

- Đảm bảo file MP3 không bị lỗi
- Dung lượng file không quá lớn (< 5MB khuyến nghị)
- Định dạng đúng chuẩn MP3

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra file `error_log.txt`
2. Xem lại phần **Traceback** nếu có lỗi Python
3. Đảm bảo đã làm theo đúng các bước trong README
4. Liên hệ với email : **dinhtruong1234lhp@gmail.com**

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa cho mục đích cá nhân.

---

**Chúc bạn upload thành công! 🎉**