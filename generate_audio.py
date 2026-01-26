import os
from gtts import gTTS


def generate_test_audios():
    # 1. Danh sách 5 từ tiếng Anh bất kỳ (bạn có thể thay đổi tùy ý)
    words = ["apple", "communicate", "software", "engineer", "success"]

    # 2. Tạo thư mục 'audios' nếu chưa tồn tại
    output_folder = "audios"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Đã tạo thư mục: {output_folder}")

    print("⏳ Đang bắt đầu tạo file audio...")

    # 3. Vòng lặp tạo file mp3 cho từng từ
    count = 0
    for word in words:
        # Đường dẫn lưu file (ví dụ: audios/apple.mp3)
        file_path = os.path.join(output_folder, f"{word}.mp3")

        try:
            # Tạo giọng đọc: lang='en' (Tiếng Anh), slow=False (Tốc độ đọc bình thường)
            tts = gTTS(text=word, lang='en', slow=False)

            # Lưu thành file mp3
            tts.save(file_path)
            print(f"✅ Đã tạo thành công: {word}.mp3")
            count += 1
        except Exception as e:
            print(f"❌ Lỗi khi tạo audio cho từ '{word}': {e}")

    print(f"🎉 Hoàn tất! Đã tạo {count} file trong thư mục '{output_folder}'.")


if __name__ == "__main__":
    generate_test_audios()