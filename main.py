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
DATABASE_URL = ""
BASE_DIR = os.getcwd()


def setup_driver():
    print("🌐 [BƯỚC 1] Đang khởi tạo trình duyệt Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def login(driver, wait):
    print("🔑 [BƯỚC 2] Đang truy cập trang đăng nhập Memrise...")
    driver.get("https://community-courses.memrise.com/signin")

    print("⏳ Đang điền thông tin đăng nhập...")
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Chờ sau khi login xong
    wait.until(EC.url_contains("dashboard"))
    print("✅ Đăng nhập thành công! Đã vào Dashboard.")


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
    driver = setup_driver()
    wait = WebDriverWait(driver, 15) # Thời gian chờ tối đa 15 giây

    try:
        login(driver, wait)
        upload_audios(driver, wait)
        print("🎉 HOÀN TẤT TOÀN BỘ QUÁ TRÌNH!")
    except Exception as e:
        print(f"❌ CHƯƠNG TRÌNH DỪNG ĐỘT NGỘT VÌ LỖI: {str(e)}")
        print("🔍 Chi tiết lỗi (Traceback):")
        traceback.print_exc()
    finally:
        input("Nhấn Enter để đóng trình duyệt...")
        driver.quit()