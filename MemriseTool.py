import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from datetime import datetime

# --- THƯ VIỆN LOGIC ---
from gtts import gTTS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import sys
import re


class MemriseToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memrise All-In-One Tool v1.0")
        self.root.geometry("700x750")

        # Biến hệ thống
        self.is_running = False
        self.driver = None

        # --- TẠO GIAO DIỆN TAB ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Tab 1: Tạo Audio
        self.tab_gen = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gen, text='🔊 1. Tạo Audio')
        self.setup_tab_generate()

        # Tab 2: Upload Audio
        self.tab_upload = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_upload, text='☁️ 2. Upload Auto')
        self.setup_tab_upload()

        # Khu vực Log chung (Nằm dưới cùng)
        frame_log = ttk.LabelFrame(root, text="Nhật ký hoạt động (Log)")
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_area = scrolledtext.ScrolledText(frame_log, height=10, state='disabled')
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message):
        """Hàm ghi log ra màn hình"""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    # =========================================================================
    # TAB 1: LOGIC TẠO AUDIO
    # =========================================================================
    def setup_tab_generate(self):
        frame = ttk.Frame(self.tab_gen)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Chọn file words.txt
        ttk.Label(frame, text="Bước 1: Chọn file chứa từ vựng (.txt):").pack(anchor="w")
        f1 = ttk.Frame(frame)
        f1.pack(fill="x", pady=5)
        self.txt_file_path = tk.StringVar()
        ttk.Entry(f1, textvariable=self.txt_file_path).pack(side="left", fill="x", expand=True)
        ttk.Button(f1, text="Chọn File", command=self.browse_txt_file).pack(side="right", padx=5)

        # Chọn folder lưu audio
        ttk.Label(frame, text="Bước 2: Chọn thư mục lưu file Audio:").pack(anchor="w", pady=(10, 0))
        f2 = ttk.Frame(frame)
        f2.pack(fill="x", pady=5)
        self.save_folder_path = tk.StringVar(value=os.path.join(os.getcwd(), "audios"))  # Mặc định
        ttk.Entry(f2, textvariable=self.save_folder_path).pack(side="left", fill="x", expand=True)
        ttk.Button(f2, text="Chọn Folder", command=self.browse_save_folder).pack(side="right", padx=5)

        # Nút chạy
        ttk.Button(frame, text="▶️ BẮT ĐẦU TẠO AUDIO", command=self.run_generate_thread).pack(pady=20, ipadx=10,
                                                                                              ipady=5)

        # Hướng dẫn
        lbl_guide = ttk.Label(frame, text="Lưu ý: File .txt mỗi từ 1 dòng. Tool sẽ tự tạo file mp3 tương ứng.",
                              foreground="gray")
        lbl_guide.pack(side="bottom", pady=10)

    def browse_txt_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if f: self.txt_file_path.set(f)

    def browse_save_folder(self):
        f = filedialog.askdirectory()
        if f: self.save_folder_path.set(f)

    def run_generate_thread(self):
        threading.Thread(target=self.logic_generate_audio).start()

    def logic_generate_audio(self):
        input_file = self.txt_file_path.get()
        output_folder = self.save_folder_path.get()

        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Lỗi", "File từ vựng không tồn tại!")
            return

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            self.log(f"📁 Đã tạo mới thư mục: {output_folder}")

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]

            if not words:
                self.log("⚠️ File text trống!")
                return

            self.log(f"⏳ Bắt đầu tạo audio cho {len(words)} từ...")
            count = 0

            for word in words:
                # --- 1. XỬ LÝ NỘI DUNG ĐỂ ĐỌC (Text-to-Speech) ---
                # Thay thế từ viết tắt để Google đọc hay hơn
                # \b là ranh giới từ, giúp chỉ thay chữ "sb" đứng riêng lẻ
                text_to_speak = word
                text_to_speak = re.sub(r'\bsth\b', 'something', text_to_speak, flags=re.IGNORECASE)
                text_to_speak = re.sub(r'\bsb\b', 'somebody', text_to_speak, flags=re.IGNORECASE)
                # Thay dấu / bằng chữ "or" khi đọc (Ví dụ: earn/make -> earn or make)
                text_to_speak = text_to_speak.replace("/", " or ")

                # --- 2. XỬ LÝ TÊN FILE (Filename Sanitization) ---
                # Thay các ký tự cấm của Windows (/ \ : * ? " < > |) bằng dấu gạch dưới _
                safe_name = word.lower()
                for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                    safe_name = safe_name.replace(char, "_")

                # Đường dẫn lưu file
                file_path = os.path.join(output_folder, f"{safe_name}.mp3")

                try:
                    # Truyền text đã chỉnh sửa vào để đọc
                    tts = gTTS(text=text_to_speak, lang='en', slow=False)
                    tts.save(file_path)

                    # Log ra thì vẫn hiện từ gốc cho dễ theo dõi
                    self.log(f"✅ Đã tạo: {safe_name}.mp3 (Đọc là: '{text_to_speak}')")
                    count += 1
                except Exception as e:
                    self.log(f"❌ Lỗi từ '{word}': {e}")

            messagebox.showinfo("Hoàn tất", f"Đã tạo xong {count}/{len(words)} file audio!")
            self.log("🎉 QUÁ TRÌNH TẠO AUDIO HOÀN TẤT!")

        except Exception as e:
            self.log(f"❌ Lỗi nghiêm trọng: {e}")

    # =========================================================================
    # TAB 2: LOGIC UPLOAD AUDIO
    # =========================================================================
    def setup_tab_upload(self):
        frame = ttk.Frame(self.tab_upload)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Login Info
        gr_login = ttk.LabelFrame(frame, text="Thông tin đăng nhập Memrise")
        gr_login.pack(fill="x", pady=5)

        ttk.Label(gr_login, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.user_var = tk.StringVar()
        ttk.Entry(gr_login, textvariable=self.user_var, width=35).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(gr_login, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pass_var = tk.StringVar()
        ttk.Entry(gr_login, textvariable=self.pass_var, width=35, show="*").grid(row=1, column=1, padx=5, pady=5)

        # 2. Config Data
        gr_data = ttk.LabelFrame(frame, text="Cấu hình Dữ liệu")
        gr_data.pack(fill="x", pady=5)

        # Link Database
        ttk.Label(gr_data, text="Link Database (hoặc Link khóa học):").pack(anchor="w", padx=5)
        self.db_url_var = tk.StringVar()
        ttk.Entry(gr_data, textvariable=self.db_url_var).pack(fill="x", padx=5, pady=5)

        # Folder Audio
        ttk.Label(gr_data, text="Folder chứa Audio cần Upload:").pack(anchor="w", padx=5, pady=(5, 0))
        f3 = ttk.Frame(gr_data)
        f3.pack(fill="x", padx=5, pady=5)
        self.upload_folder_var = self.save_folder_path
        ttk.Entry(f3, textvariable=self.upload_folder_var).pack(side="left", fill="x", expand=True)
        ttk.Button(f3, text="Chọn...", command=self.browse_save_folder).pack(side="right", padx=5)

        # 3. Control
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        self.btn_start = ttk.Button(btn_frame, text="🚀 ĐĂNG NHẬP & UPLOAD", command=self.run_upload_thread)
        self.btn_start.pack(side="left", padx=10)
        self.btn_stop = ttk.Button(btn_frame, text="🛑 DỪNG LẠI", command=self.stop_upload, state="disabled")
        self.btn_stop.pack(side="left", padx=10)

    def stop_upload(self):
        self.is_running = False
        self.log("⚠️ Đang yêu cầu dừng chương trình...")
        self.btn_stop.config(state="disabled")

    def run_upload_thread(self):
        # Validate
        if not self.user_var.get() or not self.pass_var.get():
            messagebox.showwarning("Thiếu thông tin", "Nhập Email và Password!")
            return
        if not self.db_url_var.get():
            messagebox.showwarning("Thiếu thông tin", "Nhập Link Database Memrise!")
            return

        self.is_running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        threading.Thread(target=self.logic_upload).start()

    def setup_driver(self):
        self.log("🌐 Đang khởi tạo trình duyệt Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def get_correct_database_url(self, input_url):
        """Hàm tự động xử lý link Level/Course thành link Database chuẩn"""
        self.log(f"🕵️ Đang phân tích URL: {input_url}")

        # 1. Nếu link đã là Database chuẩn (có chứa /edit/database/) -> Dùng luôn
        if "/edit/database/" in input_url:
            self.log("✅ Link chuẩn. Tiếp tục...")
            return input_url

        # 2. Xử lý "lùi bước" về trang chủ khóa học
        # Cắt bỏ phần #l_... ở cuối nếu có
        clean_url = input_url.split("#")[0]

        # Nếu URL chưa có đuôi /edit/, thêm vào cho chắc
        if not clean_url.endswith("/edit/") and "/edit" not in clean_url:
            clean_url = clean_url.rstrip("/") + "/edit/"

        self.log(f"🔄 Đang chuyển hướng về trang chủ khóa học: {clean_url}")
        self.driver.get(clean_url)
        time.sleep(3)  # Đợi load trang

        try:
            # 3. Tìm nút "Databases" (Cơ sở dữ liệu) bằng HREF (Bất chấp tiếng Việt/Anh)
            # Nút này luôn có link chứa chữ '/edit/databases/'
            self.log("🔎 Đang tìm nút 'Cơ sở dữ liệu'...")

            try:
                # Cách 1: Tìm theo HREF đặc trưng trong menu
                db_tab = self.driver.find_element(By.XPATH, "//a[contains(@href, '/edit/databases/')]")
                db_tab.click()
                self.log("   -> Đã click vào tab Database (Cách 1).")
            except:
                # Cách 2: Tìm mọi thẻ a chứa link databases
                self.log("⚠️ Cách 1 thất bại, thử tìm mọi link chứa '/edit/databases/'...")
                db_tabs = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/edit/databases/')]")
                if len(db_tabs) > 0:
                    db_tabs[0].click()
                    self.log("   -> Đã click vào tab Database (Cách 2).")
                else:
                    raise Exception("Không tìm thấy link nào chứa '/edit/databases/'")

            time.sleep(2)

            # 4. Chọn Database đầu tiên trong danh sách
            # Link database chuẩn sẽ nằm ở cột Tên (Name), thẻ <a> đầu tiên
            first_db_link = self.driver.find_element(By.XPATH, "//td[contains(@class,'name')]//a")
            real_db_url = first_db_link.get_attribute("href")

            self.log(f"✅ Đã tìm thấy Database gốc: {real_db_url}")
            return real_db_url

        except Exception as e:
            self.log(f"❌ Không tìm được Database. Lỗi: {str(e)}")
            # Trường hợp xấu nhất: Trả về URL cũ
            return input_url

    def logic_upload(self):
        try:
            self.driver = self.setup_driver()
            wait = WebDriverWait(self.driver, 20)

            # --- LOGIN ---
            self.log("🔑 Đang đăng nhập...")
            self.driver.get("https://community-courses.memrise.com/signin")

            wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.user_var.get())
            self.driver.find_element(By.NAME, "password").send_keys(self.pass_var.get())
            try:
                self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            except:
                self.driver.find_element(By.NAME, "password").send_keys(Keys.ENTER)

            # Check Login
            try:
                wait.until(lambda d: "dashboard" in d.current_url or "home" in d.current_url)
                self.log("✅ Đăng nhập thành công!")
            except:
                self.log("❌ Không thể đăng nhập. Kiểm tra lại mật khẩu.")
                return

            # --- PREPARE ---
            audio_folder = self.upload_folder_var.get()
            self.log("🔄 Quét file audio...")
            if not os.path.exists(audio_folder):
                self.log("❌ Thư mục audio không tồn tại!")
                return

            # Tạo dictionary {word: filename} để tra cứu nhanh
            all_files = {}

            for f in os.listdir(audio_folder):
                if f.endswith(".mp3"):
                    real_filename = f
                    # Tên dùng để so khớp (giả lập lại từ gốc): earn_make money
                    key_name = f.replace(".mp3", "").lower()
                    # Lưu vào từ điển
                    all_files[key_name] = real_filename

            self.log(f"🎯 Tìm thấy {len(all_files)} file cần upload.")
            self.log(f"🎯 Danh sách các từ nhận diện được: {', '.join(all_files.keys())}")

            if len(all_files) == 0:
                self.log("⚠️ Không có file mp3 nào. Dừng lại.")
                return

            # --- UPLOAD LOOP ---

            # 1. Lấy URL chuẩn (Tự động tìm nếu user nhập sai)
            raw_url = self.db_url_var.get()
            final_url = self.get_correct_database_url(raw_url)
            base_url = final_url.split("?")[0]
            current_page = 1

            # Vòng lặp chính: Chạy khi còn file và user chưa bấm Stop
            while self.is_running and all_files:
                self.log(f"📄 Đang xử lý trang {current_page}...")

                separator = "&" if "?" in base_url else "?"
                self.driver.get(f"{base_url}{separator}page={current_page}")

                # Check rows
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'thing')]")))
                    time.sleep(2)
                    rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'thing')]")
                except:
                    self.log("🛑 Hết trang hoặc data trống.")
                    break

                if not rows:
                    self.log("🛑 Trang trống. Dừng lại.")
                    break

                # Duyệt từng dòng
                for row in rows:
                    if not self.is_running: break
                    try:
                        word_el = row.find_element(By.XPATH, ".//td[@data-key='1']//div[@class='text']")
                        word_raw = word_el.text.strip().lower()
                        word_safe = word_raw

                        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                            word_safe = word_safe.replace(char, "_")

                        if word_safe in all_files:
                            try:
                                audio_cell = row.find_element(By.XPATH, ".//td[@data-key='3']")
                                if audio_cell.find_elements(By.XPATH, ".//*[contains(@class, 'audio-player')]") or \
                                    audio_cell.find_elements(By.TAG_NAME, "audio"):

                                    self.log(f"⏩ Bỏ qua '{word_safe}' (Đã có audio trên web).")
                                    # Xóa khỏi danh sách để không tìm lại ở các trang sau
                                    del all_files[word_safe]

                                    if not all_files:
                                        self.log("\n🏁 Đã xử lý xong toàn bộ danh sách. Dừng sớm!")
                                        messagebox.showinfo("Thành công", "Đã hoàn tất!")
                                        return
                                    continue
                            except:
                                pass

                            fname = all_files[word_safe]
                            inp = row.find_element(By.XPATH,
                                                   ".//input[@type='file' and contains(@class, 'add_thing_file')]")
                            inp.send_keys(os.path.join(audio_folder, fname))

                            self.log(f"✅ Upload MỚI: '{word_safe}'")

                            # Xóa file đã làm xong khỏi danh sách
                            del all_files[word_safe]
                            time.sleep(0.5)

                            # [QUAN TRỌNG] Kiểm tra ngay lập tức xem hết file chưa
                            if not all_files:
                                self.log("\n🏁 Đã upload hết toàn bộ file trong thư mục. Dừng chương trình sớm!")
                                messagebox.showinfo("Thành công", "Đã upload xong toàn bộ file!")
                                return  # THOÁT HÀM NGAY LẬP TỨC
                    except:
                        continue

                # Logic Next Page
                if len(rows) < 20:
                    self.log("🏁 Đã đến trang cuối cùng của Database.")
                    break
                current_page += 1

            # Nếu chạy hết vòng lặp mà vẫn còn file
            if all_files:
                self.log(f"⚠️ Đã quét hết Database nhưng vẫn còn dư {len(all_files)} file chưa tìm thấy từ tương ứng.")

            self.log("🎉 XONG! Chương trình đã hoàn tất.")
            messagebox.showinfo("Thành công", "Quy trình kết thúc!")

        except Exception as e:
            self.log(f"❌ LỖI: {e}")
        finally:
            self.is_running = False
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = MemriseToolApp(root)
    root.mainloop()