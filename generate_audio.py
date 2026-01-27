import os
from gtts import gTTS

def generate_audios_from_file(input_file="words.txt"):
    # 1. Kiểm tra xem file words.txt có tồn tại không
    if not os.path.exists(input_file):
        print(f"❌ Lỗi: Không tìm thấy file '{input_file}'!")
        return

    # 2. Tạo thư mục 'audios' nếu chưa tồn tại
    output_folder = "audios"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Đã tạo thư mục: {output_folder}")

    # 3. Đọc danh sách từ từ file
    with open(input_file, "r", encoding="utf-8") as f:
        # .strip() để loại bỏ khoảng trắng và ký tự xuống dòng dư thừa
        words = [line.strip() for line in f if line.strip()]

    if not words:
        print("⚠️ File 'words.txt' đang trống.")
        return

    print(f"⏳ Bắt đầu tạo audio cho {len(words)} từ...")

    # 4. Vòng lặp tạo file mp3
    count = 0
    for word in words:
        # Chuyển tên file về chữ thường để khớp với logic upload của tool
        file_path = os.path.join(output_folder, f"{word.lower()}.mp3")

        try:
            tts = gTTS(text=word, lang='en', slow=False)
            tts.save(file_path)
            print(f"✅ Đã tạo: {word.lower()}.mp3")
            count += 1
        except Exception as e:
            print(f"❌ Lỗi cho từ '{word}': {e}")

    print(f"🎉 Hoàn tất! Đã tạo {count}/{len(words)} file trong thư mục '{output_folder}'.")

if __name__ == "__main__":
    generate_audios_from_file()