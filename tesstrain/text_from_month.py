import os
import random
import pathlib
import subprocess
import cv2
import numpy as np

# ฟังก์ชันสุ่มวันที่ในช่วงที่กำหนด
def generate_random_date():
    months = [
        "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
        "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
    ]
    year = random.randint(2450, 2567)
    month = random.choice(months)
    
    days_in_month = {
        "ม.ค.": 31, "ก.พ.": 28, "มี.ค.": 31, "เม.ย.": 30, "พ.ค.": 31, "มิ.ย.": 30,
        "ก.ค.": 31, "ส.ค.": 31, "ก.ย.": 30, "ต.ค.": 31, "พ.ย.": 30, "ธ.ค.": 31
    }
    
    # กรณีปีอธิกสุรทิน
    if month == "ก.พ." and ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
        days_in_month["ก.พ."] = 29

    day = random.randint(1, days_in_month[month])
    return f"{day} {month} {year}"

# สุ่มวันที่ 20 ครั้งแล้วรวมเป็นข้อความ
def generate_multiple_dates(num_dates=20):
    return [generate_random_date() for _ in range(num_dates)]

# กำหนดที่เก็บไฟล์ข้อความและภาพ
training_text_file = 'langdata/langdata_lstm/tha/tha.training_text'
output_directory = 'tesstrain/data/DilleniaUPC-ground-truth'

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# อ่านไฟล์ข้อความ
lines = []
with open(training_text_file, 'r', encoding='utf-8') as input_file:
    for line in input_file.readlines():
        lines.append(line.strip())

# สุ่มลำดับบรรทัด
random.shuffle(lines)
lines = lines[:1000]

line_count = 2000
for line in lines:

    # สุ่มวันที่ 20 ครั้งแล้วเพิ่มไปในข้อความ
    random_dates = generate_multiple_dates(20)
    date_str = ' '.join(random_dates)
    random_size_font = random.randint(12, 25)
    random_exposure = random.randint(1, 2)
    # สร้างไฟล์ข้อความฝึก
    line_training_text = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
    with open(line_training_text, 'w', encoding='utf-8') as output_file:
        output_file.write(f"{date_str}\n")  # เพิ่มข้อความวันที่เข้าไปในไฟล์

    # สร้างชื่อไฟล์ base สำหรับภาพ
    file_base_name = f'tha_{line_count}'

    # สร้างภาพฝึกด้วย text2image
    subprocess.run([
        'text2image',
        '--font=DilleniaUPC',
        f'--ptsize={random_size_font}',                     # ปรับขนาดฟอนต์
        f'--text={line_training_text}',
        f'--outputbase={output_directory}/{file_base_name}',
        '--max_pages=1',
        '--strip_unrenderable_words',
        '--leading=15',
        '--xsize=4500',
        '--ysize=560',
        '--char_spacing=0.03',
        f'--exposure={random_exposure}',
        '--unicharset_file=langdata/tha.unicharset'
    ])

    # เพิ่ม Salt-and-Pepper Noise
    image_path = f'{output_directory}/{file_base_name}.tif'
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is not None:
        # จำนวนของ noise
        noise_amount = 0.0005
        total_pixels = image.size
        num_salt = int(noise_amount * total_pixels)
        num_pepper = int(noise_amount * total_pixels)
        random_number = random.randint(0, 5)
        # เพิ่ม Salt (จุดสีขาว)
        for _ in range(num_salt):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord, x_coord] = 255
            # เพิ่ม 5px ของ salt
            image[y_coord:y_coord+random_number, x_coord:x_coord+random_number] = 255

        # เพิ่ม Pepper (จุดสีดำ)
        for _ in range(num_pepper):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord, x_coord] = 0
            # เพิ่ม 5px ของ pepper
            image[y_coord:y_coord+random_number, x_coord:x_coord+random_number] = 0

        # บันทึกภาพที่มีการเพิ่ม Salt-and-Pepper Noise
        cv2.imwrite(image_path, image)

    line_count += 1
