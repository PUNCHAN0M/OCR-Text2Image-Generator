import os
import random
import pathlib
import subprocess
import re  # นำเข้าโมดูล re สำหรับ Regular Expression
import cv2

# ตั้งค่าพาธของไฟล์และโฟลเดอร์
training_text_file = 'langdata/langdata_lstm/tha/tha.training_text'
output_directory = 'tesstrain/data/DilleniaUPC-ground-truth'

# สร้างโฟลเดอร์ผลลัพธ์หากไม่มี
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# ฟังก์ชันสุ่มเพิ่ม Salt-and-Pepper Noise
def add_salt_pepper_noise(image_path, noise_amount=0.0005):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    salt_pepper_size = random.randint(0, 5)

    if image is not None:
        total_pixels = image.size
        num_salt = int(noise_amount * total_pixels)
        num_pepper = int(noise_amount * total_pixels)

        # เพิ่ม salt (จุดสีขาว)
        for _ in range(num_salt):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord:y_coord + salt_pepper_size, x_coord:x_coord + salt_pepper_size] = 255

        # เพิ่ม pepper (จุดสีดำ)
        for _ in range(num_pepper):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord:y_coord + salt_pepper_size, x_coord:x_coord + salt_pepper_size] = 0

        # บันทึกภาพที่แก้ไขแล้ว
        cv2.imwrite(image_path, image)

# ฟังก์ชันอ่านและทำความสะอาดข้อมูลจากไฟล์ training
def clean_training_lines(training_text_file, allowed_chars):
    lines = []
    with open(training_text_file, 'r', encoding='utf-8') as input_file:
        for line in input_file.readlines():
            # ลบตัวอักษรที่ไม่ต้องการ
            cleaned_line = ''.join(re.findall(allowed_chars, line))
            if cleaned_line.strip():
                lines.append(cleaned_line)
    return lines

# ฟังก์ชันสุ่มขนาดฟอนต์และ exposure
def get_random_font_and_exposure():
    random_size_font = random.randint(12, 25)
    random_exposure = random.randint(1, 2)
    return random_size_font, random_exposure

# ฟังก์ชันสร้างภาพจากข้อความ
def generate_image_from_text(line, line_count, random_size_font, random_exposure):
    training_text_file_name = pathlib.Path(training_text_file).stem
    line_training_text = os.path.join(output_directory, f'{training_text_file_name}_{line_count}.gt.txt')

    with open(line_training_text, 'w', encoding='utf-8') as output_file:
        output_file.writelines([line])

    file_base_name = f'tha_{line_count}'

    subprocess.run([
        'text2image',
        '--font=DilleniaUPC',
        f'--text={line_training_text}',
        f'--outputbase={os.path.join(output_directory, file_base_name)}',
        '--max_pages=1',
        f'--ptsize={random_size_font}',
        '--strip_unrenderable_words',
        '--leading=25',
        '--xsize=3600',
        '--ysize=480',
        '--char_spacing=0.05',
        f'--exposure={random_exposure}',
        '--unicharset_file=langdata/tha.unicharset'
    ])

    image_path = f'{output_directory}/{file_base_name}.tif'
    add_salt_pepper_noise(image_path)

# ฟังก์ชันหลักที่ทำงาน
def main():
    allowed_chars = r'[ก-ฮะ-์่-๋็า-ูฤ-์เ-์แ-์ไ-์โ-์ใ-์า-์ฯๆ\s\.\(\)\/\-]'  # Thai letters, vowels, tone marks, and allowed symbols

    # อ่านและทำความสะอาดข้อมูลจากไฟล์
    lines = clean_training_lines(training_text_file, allowed_chars)

    # สุ่มคำและเตรียมข้อมูล
    random.shuffle(lines)
    count = 5  # จำนวนภาพที่ต้องการ
    lines = lines[:count]

    # สร้างภาพและเพิ่ม Salt-and-Pepper Noise
    for line_count, line in enumerate(lines):
        random_size_font, random_exposure = get_random_font_and_exposure()
        print(f"size: {random_size_font}\nexposure: {random_exposure}")
        generate_image_from_text(line, line_count, random_size_font, random_exposure)

if __name__ == '__main__':
    main()
