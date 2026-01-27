import os
import time
from datetime import datetime
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CẤU HÌNH ---
USERNAME = "your email"
PASSWORD = "your email password"
# link to database, ex: https://community-courses.memrise.com/course/6714335/m/edit/database/7775210/
DATABASE_URL = "https://community-courses.memrise.com/course/6714311/engrisk/edit/database/7775185/"
BASE_DIR = os.getcwd()


def setup_driver():
    print("🌐 [BƯỚC 1] Đang khởi tạo Chrome với Profile RIÊNG BIỆT...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # --- CẤU HÌNH PROFILE RIÊNG (KHÔNG DÙNG PROFILE CHÍNH NỮA) ---
    # Selenium sẽ tự động tạo dữ liệu vào thư mục này
    # Đảm bảo đường dẫn này tồn tại hoặc ngắn gọn, không có dấu tiếng Việt
    user_data_dir = r"E:\SeleniumProfile"
    options.add_argument(f"user-data-dir={user_data_dir}")

    # BỎ dòng profile-directory=Default (Không cần thiết với Custom Profile)
    # BỎ dòng remote-debugging-port=9222 (Để Chrome tự chọn cổng ngẫu nhiên -> Tránh xung đột)

    # Các tùy chọn ổn định
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Tắt cảnh báo
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-infobars")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def login(driver, wait):
    print("🔑 [BƯỚC 2] Truy cập Memrise (Sử dụng Cookie đã lưu)...")

    # 1. Truy cập trang Dashboard
    driver.get("https://community-courses.memrise.com/dashboard")

    print("⏳ Đang đợi trang web tải (Chờ 5 giây)...")
    time.sleep(5)  # Chờ cứng 5s để đảm bảo web load hết, kệ cho mạng chậm

    # 2. Lấy URL hiện tại để kiểm tra
    current_url = driver.current_url
    print(f"🔗 URL hiện tại mà Bot đang thấy: {current_url}")

    # 3. Logic kiểm tra đơn giản hơn:
    # Nếu URL KHÔNG chứa chữ "signin" hoặc "login" -> Nghĩa là đã vào được trong.
    if "signin" not in current_url and "login" not in current_url:
        print("✅ Xác nhận: Đã ở trong trạng thái đăng nhập!")
    else:
        # Trường hợp xấu: Vẫn bị đá về trang login
        print("❌ CẢNH BÁO: Bot vẫn đang ở trang Login. Có thể Cookie chưa ăn.")
        print("👉 Hãy thử chạy lại lệnh PowerShell để đăng nhập lại.")
        driver.quit()
        exit()


# --- TÍNH NĂNG MỚI: CHUẨN HÓA TÊN FILE ---
def normalize_audio_filenames(folder_path):
    print("🔄 [BƯỚC 3.1] Đang chuẩn hóa tên file về chữ thường (lowercase)...")
    count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):
            new_filename = filename.lower()  # Chuyển thành chữ thường
            # Chỉ đổi tên nếu tên cũ có chữ hoa
            if new_filename != filename:
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_filename)
                os.rename(old_path, new_path)
                count += 1
    if count > 0:
        print(f"   -> Đã đổi tên {count} file.")
    else:
        print("   -> Tất cả file đã ở dạng chữ thường, không cần đổi.")


# --- TÍNH NĂNG MỚI: GHI LOG LỖI ---
def write_error_log(failed_list):
    if not failed_list:
        return  # Nếu không có lỗi thì không tạo file log

    log_filename = "error_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Mở file ở chế độ 'a' (append) để nối tiếp log thay vì ghi đè
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"\n--- LOG LỖI NGÀY: {timestamp} ---\n")
        for word in failed_list:
            f.write(f"Không tìm thấy hoặc lỗi: {word}\n")

    print(f"⚠️ Đã ghi lại {len(failed_list)} từ bị lỗi vào file '{log_filename}'")


def upload_audios(driver, wait):
    print(f"📂 [BƯỚC 3.2] Đang tải cơ sở dữ liệu khóa học...")
    driver.get(DATABASE_URL)
    time.sleep(3)  # Đợi load trang database

    audio_folder = os.path.join(BASE_DIR, "audios")

    # CHUẨN HÓA TÊN FILE TRƯỚC KHI LẤY DANH SÁCH
    normalize_audio_filenames(audio_folder)

    audio_files = [f for f in os.listdir(audio_folder) if f.endswith(".mp3")]
    total_files = len(audio_files)
    print(f"🎯 [BƯỚC 4] Bắt đầu quá trình Upload {total_files} file âm thanh...")
    print("-" * 50)  # Dòng kẻ phân cách cho dễ nhìn

    # Khởi tạo danh sách chứa các từ bị lỗi
    failed_words = []

    # Sử dụng enumerate để lấy số thứ tự (index)
    for index, audio_name in enumerate(audio_files, start=1):
        word = audio_name.replace(".mp3", "")
        audio_path = os.path.join(audio_folder, audio_name)

        # Hiển thị tiến độ kiểu [1/5], [2/5]...
        print(f"[{index}/{total_files}] Đang xử lý từ: '{word}' ...", end=" ")

        try:
            # TÌM DÒNG (Chữ thường)
            row_xpath = f"//tr[contains(@class, 'thing') and .//td[@data-key='1']//div[text()='{word}']]"
            row_element = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))

            # TÌM INPUT VÀ UPLOAD
            input_xpath = ".//input[@type='file' and contains(@class, 'add_thing_file')]"
            file_input = row_element.find_element(By.XPATH, input_xpath)
            file_input.send_keys(audio_path)

            time.sleep(1.5)  # Đợi tải lên
            print(f"✅ Thành công!")

        except Exception as e:
            print(f"❌ THẤT BẠI (Không tìm thấy từ trên Web)")
            failed_words.append(word)

    print("-" * 50)
    print("📝 [BƯỚC 5] Đang tổng hợp lỗi...")
    write_error_log(failed_words)


if __name__ == "__main__":
    print("🚀 BẮT ĐẦU KHỞI CHẠY CHƯƠNG TRÌNH...")

    try:
        os.system("taskkill /F /IM chrome.exe /T >nul 2>&1")
    except:
        pass

    driver = setup_driver()
    wait = WebDriverWait(driver, 15)

    try:
        login(driver, wait)
        upload_audios(driver, wait)
        print("🎉 HOÀN TẤT TOÀN BỘ QUÁ TRÌNH!")

    except Exception as e:
        print(f"\n❌ CHƯƠNG TRÌNH DỪNG VÌ LỖI: {e}")
        traceback.print_exc()

    finally:
        try:
            input("\nNhấn Enter để đóng trình duyệt và kết thúc...")
            driver.quit()
        except:
            print("Chương trình đã kết thúc.")