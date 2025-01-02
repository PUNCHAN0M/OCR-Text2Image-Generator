import os
import random
import re
import subprocess
import cv2
import pandas as pd  # ใช้ pandas สำหรับอ่านไฟล์ Excel

# ===================== Utility Functions =====================

def setup_output_directory(output_directory):
    """ตรวจสอบและสร้างโฟลเดอร์สำหรับเก็บผลลัพธ์"""
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

def add_salt_pepper_noise(image_path, noise_amount=0.0005):
    """เพิ่ม Salt-and-Pepper Noise ลงในภาพ"""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return

    total_pixels = image.size
    num_salt = int(noise_amount * total_pixels)
    num_pepper = int(noise_amount * total_pixels)

    # เพิ่ม salt (จุดสีขาว)
    for _ in range(num_salt):
        y_coord = random.randint(0, image.shape[0] - 1)
        x_coord = random.randint(0, image.shape[1] - 1)
        image[y_coord, x_coord] = 255

    # เพิ่ม pepper (จุดสีดำ)
    for _ in range(num_pepper):
        y_coord = random.randint(0, image.shape[0] - 1)
        x_coord = random.randint(0, image.shape[1] - 1)
        image[y_coord, x_coord] = 0

    cv2.imwrite(image_path, image)

def get_random_font_and_exposure():
    """สุ่มขนาดฟอนต์และค่า exposure"""
    random_size_font = random.randint(12, 25)
    random_exposure = random.randint(1, 2)
    return random_size_font, random_exposure

# ===================== Text File Processing =====================

def clean_training_lines(training_text_file, allowed_chars):
    """อ่านและลบตัวอักษรที่ไม่ต้องการออกจากไฟล์ข้อความ"""
    lines = []
    with open(training_text_file, 'r', encoding='utf-8') as input_file:
        for line in input_file.readlines():
            cleaned_line = ''.join(re.findall(allowed_chars, line))
            if cleaned_line.strip():
                lines.append(cleaned_line)
    return lines

def read_excel_and_prepare_lines(excel_file, sheet_name):
    """อ่านข้อมูลจาก Excel และสร้างข้อความที่ใช้ฝึก"""
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df['combined_text'] = df['TambonThai'] + ' ' + df['TambonThaiShort'] + ' ' + df['DistrictThai'] + ' ' + df['DistrictThaiShort'] + ' ' + df['ProvinceThai'] + ' ' + df['PostCodeMain'].astype(str) + ' ' + df['PostCodeAll'].astype(str)
    lines = df['combined_text'].dropna().tolist()
    return lines

def enhance_lines_with_random_text(lines):
    """เพิ่มข้อความสุ่มในแต่ละบรรทัด"""
    enhanced_lines = []
    for line in lines:
        random_part1 = f"ที่อยู่ {random.randint(1, 99)}/{random.randint(1, 99)}"
        random_part2 = f"หมู่ {random.randint(1, 100)}"
        additional_parts = "ถ. ซ."
        enhanced_line = f"{line} {random_part1} {random_part2} {additional_parts}"
        enhanced_lines.append(enhanced_line)
    return enhanced_lines

def group_lines_for_training(enhanced_lines, group_size=5, max_groups=1000):
    """จัดกลุ่มบรรทัดข้อความสำหรับสร้างภาพ"""
    random.shuffle(enhanced_lines)
    grouped_lines = []
    for i in range(0, len(enhanced_lines), group_size):
        group = enhanced_lines[i:i + group_size]
        grouped_line = '/'.join(group)
        grouped_lines.append(grouped_line)
    return grouped_lines[:max_groups]

# ===================== Image Generation =====================

def generate_training_text_file(output_directory, line_count, text):
    """สร้างไฟล์ข้อความสำหรับการฝึก"""
    file_path = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
    with open(file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text)
    return file_path

def generate_image_with_text2image(text_file, output_directory, line_count, font_name="DilleniaUPC"):
    """สร้างภาพข้อความด้วย text2image"""
    random_size_font, random_exposure = get_random_font_and_exposure()
    file_base_name = f'tha_{line_count}'
    subprocess.run([
        'text2image',
        f'--font={font_name}',
        f'--ptsize={random_size_font}',
        f'--text={text_file}',
        f'--outputbase={output_directory}/{file_base_name}',
        '--max_pages=1',
        '--strip_unrenderable_words',
        '--leading=25',
        '--xsize=4500',
        '--ysize=560',
        '--char_spacing=0.01',
        f'--exposure={random_exposure}',
        '--unicharset_file=langdata/tha.unicharset',
    ])
    return f'{output_directory}/{file_base_name}.tif'

# ===================== Main Processes =====================

def generate_image_custom_month(output_directory, num_images=5):
    """สร้างภาพข้อความพร้อมข้อมูลวันที่แบบกำหนดเอง"""
    months = [
        "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
        "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
    ]

    def generate_random_date():
        year = random.randint(2450, 2567)
        month = random.choice(months)
        days_in_month = {
            "ม.ค.": 31, "ก.พ.": 28, "มี.ค.": 31, "เม.ย.": 30, "พ.ค.": 31, "มิ.ย.": 30,
            "ก.ค.": 31, "ส.ค.": 31, "ก.ย.": 30, "ต.ค.": 31, "พ.ย.": 30, "ธ.ค.": 31
        }
        if month == "ก.พ." and ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
            days_in_month["ก.พ."] = 29

        day = random.randint(1, days_in_month[month])
        return f"{day} {month} {year}"

    for i in range(num_images):
        date_str = generate_random_date()
        random_size_font, random_exposure = get_random_font_and_exposure()
        print(f"Generating custom month image {i + 1}/{num_images} with date {date_str}")
        text_file = generate_training_text_file(output_directory, i, date_str)
        image_path = generate_image_with_text2image(text_file, output_directory, i)
        add_salt_pepper_noise(image_path)

def process_excel_and_generate_images(excel_file, output_directory, sheet_name='Sheet1', group_size=5, max_groups=1000):
    """กระบวนการสร้างภาพจากข้อมูลในไฟล์ Excel"""
    lines = read_excel_and_prepare_lines(excel_file, sheet_name)
    enhanced_lines = enhance_lines_with_random_text(lines)
    grouped_lines = group_lines_for_training(enhanced_lines, group_size, max_groups)

    for line_count, text in enumerate(grouped_lines):
        text_file = generate_training_text_file(output_directory, line_count, text)
        image_path = generate_image_with_text2image(text_file, output_directory, line_count)
        add_salt_pepper_noise(image_path)

def main():
    """ฟังก์ชันหลักสำหรับการสร้างภาพข้อความ"""
    output_directory = 'tesstrain/data/DilleniaUPC-ground-truth'
    excel_file = 'E:/Project/Tesseract-FineTuning/tesstrain/Address2col_prepared.xlsx'
    setup_output_directory(output_directory)

    # กำหนดหมายเลขเริ่มต้น
    current_index = 0

    # สร้างภาพจาก custom month
    num_custom_month_images = 2
    generate_image_custom_month(output_directory, num_images=num_custom_month_images)
    current_index += num_custom_month_images

    # สร้างภาพจาก Excel
    num_excel_groups = 2  # จำนวนกลุ่มที่จะสร้างจาก Excel
    process_excel_and_generate_images(
        excel_file, output_directory, sheet_name='Sheet1', group_size=5, max_groups=num_excel_groups
    )
    current_index += num_excel_groups

    # ระบุจุดสุดท้าย
    print(f"กระบวนการเสร็จสิ้นที่ tha_{current_index - 1}")

if __name__ == '__main__':
    main()
