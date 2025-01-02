import os
import random
import pathlib
import subprocess
import pandas as pd  # ใช้ pandas สำหรับอ่านไฟล์ Excel
import cv2  # OpenCV สำหรับจัดการภาพ
import numpy as np

# กำหนดเส้นทางไฟล์ Excel
excel_file = 'E:/Project/Tesseract-FineTuning/tesstrain/Address2col_prepared.xlsx'  # เปลี่ยนเป็นชื่อไฟล์ Excel ของคุณ
sheet_name = 'Sheet1'  # ชื่อแผ่นงาน (ถ้ามีหลายแผ่น)

# อ่านข้อมูลจาก Excel
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# รวมคอลัมน์ที่ต้องการเป็น 1 บรรทัด
df['combined_text'] = df['TambonThai'] + ' ' + df['TambonThaiShort'] + ' ' + df['DistrictThai'] + ' ' + df['DistrictThaiShort'] + ' ' + df['ProvinceThai'] + ' ' + df['PostCodeMain'].astype(str) + ' ' + df['PostCodeAll'].astype(str)

# ลบค่าที่ว่างและแปลงเป็น list
lines = df['combined_text'].dropna().tolist()

# เพิ่มข้อความสุ่มในแต่ละบรรทัด
enhanced_lines = []
for line in lines:
    random_part1 = f"ที่อยู่ {random.randint(1, 99)}/{random.randint(1, 99)}"
    random_part2 = f"หมู่ {random.randint(1, 100)}"
    additional_parts = f"ถ. ซ."
    enhanced_line = f"{line}{random_part1}/{random_part2}{additional_parts}"
    enhanced_lines.append(enhanced_line)

# ตั้งค่าที่เก็บไฟล์ output
output_directory = 'tesstrain/data/DilleniaUPC-ground-truth'
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# สุ่มข้อมูล
random.shuffle(enhanced_lines)

# รวม 5 บรรทัดใน 1 ภาพ
# ตั้งค่ากลุ่มของบรรทัด
group_size = 8
grouped_lines = []

# ใช้ for-loop สำหรับแยกกลุ่ม
for i in range(0, len(enhanced_lines), group_size):
    group = enhanced_lines[i:i + group_size]
    grouped_line = '/'.join(group)
    grouped_lines.append(grouped_line)

# จำกัดจำนวนกลุ่มให้เหลือ 1000 กลุ่ม
grouped_lines = grouped_lines[:318]

# เริ่มสร้างไฟล์ข้อความและภาพฝึก
line_count = 1682
for grouped_text in grouped_lines:
    # สร้างไฟล์ข้อความฝึก
    random_size_font = random.randint(12, 25)
    random_exposure = random.randint(1, 2)
    training_text_file_name = pathlib.Path(excel_file).stem
    line_training_text = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
    with open(line_training_text, 'w', encoding='utf-8') as output_file:
        output_file.writelines([grouped_text])

    # สร้างชื่อไฟล์ base สำหรับภาพ
    file_base_name = f'tha_{line_count}'

    # สร้างภาพฝึกด้วย text2image
    subprocess.run([
        'text2image',
        '--font=DilleniaUPC',
        f'--ptsize={random_size_font}',
        f'--text={line_training_text}',
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

    # เพิ่ม Salt-and-Pepper Noise
    image_path = f'{output_directory}/{file_base_name}.tif'
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)


    # ตรวจสอบว่าโหลดภาพได้
    if image is not None:
        # เพิ่ม Salt-and-Pepper Noise
        noise_amount = 0.0005  # เปอร์เซ็นต์ของ noise
        total_pixels = image.size
        num_salt = int(noise_amount * total_pixels)
        num_pepper = int(noise_amount * total_pixels)
        random_number = random.randint(0, 5)
        # เพิ่ม salt (จุดสีขาว)
        for _ in range(num_salt):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord:y_coord + 5, x_coord:x_coord + 5] = 255

        # เพิ่ม pepper (จุดสีดำ)
        for _ in range(num_pepper):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord:y_coord + random_number, x_coord:x_coord + random_number] = 0

        # บันทึกภาพที่แก้ไขแล้วกลับไปแทนที่เดิม
        cv2.imwrite(image_path, image)

    line_count += 1
