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
    print(f"📂 [BƯỚC 3.2] Đang chuẩn bị tải lên...")

    # 1. Chuẩn bị danh sách file
    audio_folder = os.path.join(BASE_DIR, "audios")
    normalize_audio_filenames(audio_folder)

    # Lấy danh sách tất cả file mp3 cần upload
    # Dùng set (tập hợp) để tìm kiếm nhanh hơn list
    all_audio_files = {f.replace(".mp3", ""): f for f in os.listdir(audio_folder) if f.endswith(".mp3")}
    total_files = len(all_audio_files)

    if total_files == 0:
        print("⚠️ Không tìm thấy file mp3 nào trong thư mục 'audios'. Kết thúc.")
        return

    print(f"🎯 Tìm thấy {total_files} file audio cần xử lý.")

    # 2. Bắt đầu vòng lặp duyệt từng trang
    current_page = 1
    files_uploaded_count = 0
    failed_words = []

    while True:
        print(f"\n📄 --- ĐANG XỬ LÝ TRANG {current_page} ---")

        # Xử lý URL phân trang
        # Nếu URL đã có tham số (dấu ?) thì dùng dấu &, ngược lại dùng dấu ?
        separator = "&" if "?" in DATABASE_URL else "?"
        page_url = f"{DATABASE_URL}{separator}page={current_page}"

        driver.get(page_url)
        time.sleep(3)  # Đợi trang tải

        # 3. Kỹ thuật "QUÉT MỘT LƯỢT" (Scraping map)
        # Thay vì tìm từng từ (rất chậm), ta lấy toàn bộ từ đang hiển thị trên trang này về
        try:
            # Lấy tất cả các dòng dữ liệu (class 'thing')
            rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'thing')]")

            if not rows:
                print("🛑 Trang này trống (không có từ vựng). Dừng quy trình phân trang.")
                break  # Thoát vòng lặp while

            print(f"   -> Tìm thấy {len(rows)} từ vựng trên trang này. Đang so khớp...")

            # Duyệt qua từng dòng trên web
            for row in rows:
                try:
                    # 1. Lấy từ trên web
                    word_element = row.find_element(By.XPATH, ".//td[@data-key='1']//div[@class='text']")
                    word_on_web = word_element.text.strip().lower()

                    # 2. KIỂM TRA NHANH (Không cần vòng lặp for con)
                    # Chúng ta đảo ngược dictionary thành {word: filename} ở đầu hàm để tra cứu O(1)
                    # (Xem phần Lưu ý bên dưới để sửa đoạn khai báo all_audio_files)

                    # Nếu danh sách từ điển có chứa từ này
                    if word_on_web in all_audio_files:
                        matched_filename = all_audio_files[word_on_web]

                        # Upload file
                        input_file = row.find_element(By.XPATH, ".//input[@type='file' and contains(@class, 'add_thing_file')]")
                        file_path = os.path.join(audio_folder, matched_filename)
                        input_file.send_keys(file_path)

                        print(f"   ✅ Upload thành công: '{word_on_web}'")
                        files_uploaded_count += 1
                        time.sleep(0.5)

                        # Xóa từ đã làm xong khỏi danh sách (Để tránh upload lại ở trang sau nếu lỡ trùng)
                        del all_audio_files[word_on_web]

                        # Nếu danh sách cần làm đã TRỐNG TRƠN -> Nghĩa là xong hết rồi
                        if not all_audio_files:
                            print("\n🏁 Đã upload hết toàn bộ file trong thư mục. Dừng chương trình sớm!")
                            return

                except Exception as e:
                    # Lỗi nhỏ ở dòng này thì bỏ qua, đi dòng tiếp
                    continue

        except Exception as e:
            print(f"⚠️ Có lỗi khi quét trang {current_page}: {e}")
            break

        # 4. Kiểm tra nút Next để quyết định có chạy tiếp không
        try:
            # Tìm xem có nút phân trang tiếp theo không, hoặc đơn giản là cứ tăng page
            # Nếu số lượng dòng < số lượng tối đa 1 trang (thường là 100) -> Hết trang
            if len(rows) < 20:
                print("🛑 Đã đến trang cuối cùng. Hoàn tất.")
                break

            current_page += 1

        except:
            break

    print("-" * 50)
    print(f"🎉 TỔNG KẾT: Đã upload thành công {files_uploaded_count}/{total_files} file audio.")


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