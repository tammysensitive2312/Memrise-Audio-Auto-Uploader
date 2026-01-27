import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def manual_login_setup():
    print("🛠️ CHẾ ĐỘ THIẾT LẬP ĐĂNG NHẬP THỦ CÔNG")
    print("---------------------------------------")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # --- CẤU HÌNH ĐÚNG PROFILE BẠN ĐANG DÙNG TRONG MAIN.PY ---
    # Hãy đảm bảo đường dẫn này GIỐNG HỆT trong file main.py của bạn
    user_data_dir = r"E:\SeleniumProfile"
    options.add_argument(f"user-data-dir={user_data_dir}")

    # Tắt các cảnh báo để không bị Google chặn
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🌐 Đang mở Memrise...")
        driver.get("https://community-courses.memrise.com/signin")

        print("\n⚠️  HƯỚNG DẪN:")
        print("1. Trình duyệt đã mở lên.")
        print("2. Hãy tự tay đăng nhập bằng Google/Facebook/Email thoải mái.")
        print("3. Đợi đến khi nào vào hẳn được màn hình Dashboard (Danh sách khóa học).")
        print("4. SAU KHI XONG, quay lại đây nhấn phím ENTER để lưu và thoát.")

        input("\n👉 Đã đăng nhập xong? Nhấn Enter tại đây để đóng trình duyệt...")

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        driver.quit()
        print("✅ Đã lưu trạng thái đăng nhập! Giờ bạn có thể chạy main.py")


if __name__ == "__main__":
    manual_login_setup()