import os
import random
import subprocess
import cv2
import numpy as np 
# ข้อมูลสระเสียงสั้นและยาว
vowels = [
    "ะ", "า", "ิ", "ี", "ึ", "ื", "ุ", "ู", "เ", "แ", "โ", "อ", "ำ", "ใ", "ไ"
]

# ข้อมูลพยัญชนะไทย
consonants = [
    "ก", "ข", "ค", "ฆ", "ง", "จ", "ฉ", "ช", "ซ", "ฌ", "ญ", "ฎ", "ฏ", "ฐ", "ฑ", "ฒ", "ณ",
    "ด", "ต", "ถ", "ท", "ธ", "น", "บ", "ป", "ผ", "ฝ", "พ", "ฟ", "ภ", "ม", "ย", "ร", "ล", 
    "ว", "ศ", "ษ", "ส", "ห", "ฬ", "อ", "ฮ"
]

# ข้อมูลวรรณยุกต์
tone_marks = [
    "่", "้", "๊", "๋"
]

# ฟังก์ชันสุ่มคำไทย
def generate_random_thai_word():
    consonant = random.choice(consonants)
    vowel = random.choice(vowels)  # เลือกสระทั้งเสียงสั้นและยาว
    tone = random.choice(tone_marks) if random.random() < 0.5 else ''  # เลือกวรรณยุกต์
    return consonant + vowel + tone

# ตั้งค่าตำแหน่งที่เก็บไฟล์ที่สร้างขึ้น
output_directory = 'tesstrain/data/DilleniaUPC-ground-truth'

# สร้างโฟลเดอร์ถ้ายังไม่มี
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# กำหนดจำนวนครั้งที่ต้องการสร้างภาพ
num_images = 1000  # จำนวนภาพที่ต้องการสร้าง
line_count = 5000

for i in range(num_images):
    # สุ่มคำไทย 100 คำ
    num_lines = 200
    lines = []
    
    # สุ่มคำไทยจำนวน num_lines
    for _ in range(num_lines):
        random_thai_word = generate_random_thai_word()
        lines.append(random_thai_word)

    # รวมคำทั้งหมดเป็นข้อความเดียว โดยมีช่องว่างระหว่างคำ
    full_text = ' '.join(lines)

    # สร้างไฟล์ข้อความ
    line_training_text = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
    with open(line_training_text, 'w', encoding='utf-8') as output_file:
        output_file.write(full_text)

    file_base_name = f'tha_{line_count}'
    random_size_font = random.randint(12, 25)
    random_exposure = random.randint(1, 2)
    subprocess.run([
        'text2image',
        '--font=DilleniaUPC',
        f'--ptsize={random_size_font}',  
        f'--text={line_training_text}',
        f'--outputbase={output_directory}/{file_base_name}',
        '--max_pages=1',
        '--strip_unrenderable_words',
        '--leading=28',
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

        width_size = random.randint(0,4)
        height_size = random.randint(0,3)
        kernel = np.ones((width_size,height_size), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)

        cv2.imwrite(image_path, image)


    line_count += 1
