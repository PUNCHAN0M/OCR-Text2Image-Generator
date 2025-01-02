import os
import random
import pathlib
import subprocess
import re  # นำเข้าโมดูล re สำหรับ Regular Expression
import cv2
import numpy as np
import pandas as pd  # ใช้ pandas สำหรับอ่านไฟล์ Excel

# File paths
"""============================= File Path ============================="""
# input train data
training_text_file = 'langdata/langdata_lstm/tha/tha.training_text'     # input train data
output_directory = 'tesstrain/data/DilleniaUPC3-ground-truth'            # output file .tif .txt .box

def data_from_tesseract_dataset():
    global training_text_file

    # ตัวกรองตัวอักษรไทย + สัญลักษณ์ทั่วไปที่ใช้บ่อย
    allowed_chars = set(
        "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ"
        "ะาำิีึืุูเแโใไๅๆ่้๊๋์ฯฺๆ0123456789"
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        " ./-()"  # อักขระเพิ่มเติม
    )

    # อ่านไฟล์ข้อมูล
    with open(training_text_file, 'r', encoding='utf-8') as input_file:
        lines = [line.strip() for line in input_file.readlines()]
    
    # กรองบรรทัดด้วย allowed_chars
    filtered_lines = []
    for line in lines:
        filtered_line = ''.join(c for c in line if c in allowed_chars)
        if filtered_line.strip():  # ตรวจสอบว่ามีข้อความเหลือหลังจากกรอง
            filtered_lines.append(filtered_line)

    random.shuffle(filtered_lines)
    
    return filtered_lines

# กำหนดเส้นทางไฟล์ Excel
excel_file = 'E:/Project/Tesseract-FineTuning/tesstrain/Address2col_prepared.xlsx'  # เปลี่ยนเป็นชื่อไฟล์ Excel ของคุณ
sheet_name = 'Sheet1'  # ชื่อแผ่นงาน (ถ้ามีหลายแผ่น)


"""============================= CHECK PATH ============================="""
# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

"""============================= Utility ============================="""
def check_box_file(file_base_name):
    box_file_path = os.path.join(output_directory, f'{file_base_name}.box')
    return os.path.exists(box_file_path)

def create_salt_pepper(file_base_name): 
    global output_directory

    image_path = f'{output_directory}/{file_base_name}.tif'
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # ตรวจสอบว่าโหลดภาพได้
    if image is not None:
        # เพิ่ม Salt-and-Pepper Noise
        """"set parameter"""
        noise_amount = 0.00001  # เปอร์เซ็นต์ของ noise
        random_number = random.randint(0, 8)
        
        total_pixels = image.size
        num_salt = int(noise_amount * total_pixels)
        num_pepper = int(noise_amount * total_pixels)
        
        # เพิ่ม salt (จุดสีขาว)
        for _ in range(num_salt):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord:y_coord + random_number, x_coord:x_coord + random_number] = 255

        # เพิ่ม pepper (จุดสีดำ)
        for _ in range(num_pepper):
            y_coord = random.randint(0, image.shape[0] - 5)
            x_coord = random.randint(0, image.shape[1] - 5)
            image[y_coord:y_coord + random_number, x_coord:x_coord + random_number] = 0

        # บันทึกภาพที่แก้ไขแล้วกลับไปแทนที่เดิม
        # image = cv2.GaussianBlur(image, (15, 15), sigmaX=1)
        # image = cv2.GaussianBlur(image, (5, 5), 0)  # Kernel size 5x5
        # image = cv2.medianBlur(image, 3)  # Kernel size 5
        width_size = random.randint(0,4)
        height_size = random.randint(0,3)
        kernel = np.ones((width_size,height_size), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        
        angle = random_angle = random.uniform(-1, 1)  # องศาที่ต้องการหมุน
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (w, h))

        cv2.imwrite(image_path, image)

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
def generate_multiple_dates(num_dates=25):
    random_date_size = random.randint(20, 25)
    return [generate_random_date() for _ in range(num_dates)]

def text2image(file_base_name,line_training_text):
    """import global"""

    random_size_font = random.randint(12, 25)
    random_exposure = random.randint(0, 2)
    random_leading = random.randint(15, 18)
    random_char_spacing = random.uniform(0.01, 0.1) 
    print(f"size: {random_size_font}\nexposure:{random_exposure}")

    subprocess.run([
        'text2image',                                                           # output type .Tif
        f'--outputbase={os.path.join(output_directory, file_base_name)}',       # output path
        '--font=DilleniaUPC',                                                   # font_style
        f'--text={line_training_text}',                                         # sentence_text
        '--max_pages=1',                                                        # anomber_of_pages
        '--xsize=3600',                                                         # width_image
        '--ysize=480',                                                          # hight_image
        f'--ptsize={random_size_font}',                                         # font_size
        f'--leading={random_leading}',                                          # space_under_text
        f'--char_spacing={random_char_spacing}',                                # space_between_text
        f'--exposure={random_exposure}',                                        # font_weight
        '--strip_unrenderable_words',                                           # remove word cant become to picture                               
        '--unicharset_file=langdata/tha.unicharset',                            # anumber of unchar 
    ])
   


"""============================= Generate Function ============================="""

def generate_image_from_tesseract_dataset(define_count=None):
    """import global"""
    global output_directory     # path output
    global line_count           # current image                        
    global count                # a number of images need

    # ใช้ define_count ถ้ามีค่า ถ้าไม่มีก็ใช้ count
    final_count = define_count if define_count is not None else count

    """get dataset"""
    lines = data_from_tesseract_dataset()
    lines = lines[:final_count]
        

    """ process text2image"""
    for line in lines:
        #export to .gt.txt
        line_training_text = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
        with open(line_training_text, 'w', encoding='utf-8') as output_file:
            output_file.writelines([line])

        file_base_name = f'tha_{line_count}'
        text2image(file_base_name,line_training_text)

         # เช็คว่าไฟล์ .box ถูกสร้างขึ้นหรือไม่
        if not check_box_file(file_base_name):
            print(f"ทำการสร้างไฟล์ .box ใหม่สำหรับ {file_base_name}")
            text2image(file_base_name, line_training_text)

        
        create_salt_pepper(file_base_name)
        
        line_count += 1



def generate_image_from_date(amount_group_date= 30,define_count=None) :
    """import global"""
    global line_count
    global count
    amount_group_date=random.randint(20,30)
    # ใช้ define_count ถ้ามีค่า ถ้าไม่มีก็ใช้ count
    final_count = define_count if define_count is not None else count

    for line in range(final_count):
        random_dates = generate_multiple_dates(amount_group_date)
        date_str = ' '.join(random_dates)
        
        # export .gt.txt
        line_training_text = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
        with open(line_training_text, 'w', encoding='utf-8') as output_file:
            output_file.write(f"{date_str}\n")  # เพิ่มข้อความวันที่เข้าไปในไฟล์

        # สร้างชื่อไฟล์ base สำหรับภาพ
        file_base_name = f'tha_{line_count}'
        text2image(file_base_name,line_training_text)

         # เช็คว่าไฟล์ .box ถูกสร้างขึ้นหรือไม่
        if not check_box_file(file_base_name):
            print(f"ทำการสร้างไฟล์ .box ใหม่สำหรับ {file_base_name}")
            text2image(file_base_name, line_training_text)

        create_salt_pepper(file_base_name)

        line_count += 1


def generate_image_from_excel(group_size=1, define_count=None):
    """import global"""
    global line_count
    global output_directory
    global count

    # group_size = random.randint(6,8)
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์ Excel: {e}")
        return

    # รวมคอลัมน์ที่ต้องการเป็น 1 บรรทัด
    df['combined_text'] =   'ซ.' + df['DistrictThaiShort']+' ' +'ถ.' + df['TambonThaiShort'] +  " "+df['TambonThai'] + " " + df['DistrictThai'] + ' ' + df['ProvinceThai'] + ' ' 
    
    # ลบค่าที่ว่างและแปลงเป็น list
    lines = df['combined_text'].dropna().tolist()

    # ใช้ define_count ถ้ามีค่า ถ้าไม่มีก็ใช้ count
    final_count = define_count if define_count is not None else count

    if not os.path.exists(excel_file):
        print(f"ไฟล์ {excel_file} ไม่พบ")
        return

    

    # เพิ่มข้อความสุ่มในแต่ละบรรทัด
    enhanced_lines = []
    for line in lines:
        random_part1 = f"ที่อยู่ {random.randint(1, 99)}/{random.randint(1, 99)}"
        random_part2 = f"หมู่ {random.randint(1, 100)}"
        # additional_parts = f"ถ. ซ."
        enhanced_line = f"{random_part1} {random_part2} {line}"
        enhanced_lines.append(enhanced_line)
    # สุ่มข้อมูล
    random.shuffle(enhanced_lines)

    # รวม 5 บรรทัดใน 1 ภาพ
    grouped_lines = []

    # ใช้ for-loop สำหรับแยกกลุ่ม
    for i in range(0, len(enhanced_lines), group_size):
        group = enhanced_lines[i:i + group_size]
        grouped_line = '/'.join(group)
        grouped_lines.append(grouped_line)

    # จำกัดจำนวนกลุ่มให้เหลือ 1000 กลุ่ม
    grouped_lines = grouped_lines[:final_count]
    
    for grouped_text in grouped_lines:
        if not grouped_text:  # ถ้า grouped_text ว่าง
            print("excel : หมดแล้ว")
            continue  # ข้ามบรรทัดนี้ไป

        # สร้างไฟล์ข้อความฝึก
        line_training_text = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
        with open(line_training_text, 'w', encoding='utf-8') as output_file:
            output_file.writelines([grouped_text])

        # สร้างชื่อไฟล์ base สำหรับภาพ
        file_base_name = f'tha_{line_count}'
        text2image(file_base_name, line_training_text)
         # เช็คว่าไฟล์ .box ถูกสร้างขึ้นหรือไม่
        if not check_box_file(file_base_name):
            print(f"ทำการสร้างไฟล์ .box ใหม่สำหรับ {file_base_name}")
            text2image(file_base_name, line_training_text)

        create_salt_pepper(file_base_name)

        line_count += 1

def generate_image_from_sara(amount_group=100,define_count=None):
    """import global"""
    global line_count
    global output_directory
    global count
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

    # กำหนดจำนวนครั้งที่ต้องการสร้างภาพ

    for i in range(count):
        # สุ่มคำไทย 100 คำ
        lines = []
        
        # สุ่มคำไทยจำนวน num_lines
        for _ in range(amount_group):
            random_thai_word = generate_random_thai_word()
            lines.append(random_thai_word)

        # รวมคำทั้งหมดเป็นข้อความเดียว โดยมีช่องว่างระหว่างคำ
        full_text = ' '.join(lines)

        # สร้างไฟล์ข้อความ
        line_training_text = os.path.join(output_directory, f'tha_{line_count}.gt.txt')
        with open(line_training_text, 'w', encoding='utf-8') as output_file:
            output_file.write(full_text)
        # สร้างชื่อไฟล์ base สำหรับภาพ
        file_base_name = f'tha_{line_count}'
        text2image(file_base_name, line_training_text)
         # เช็คว่าไฟล์ .box ถูกสร้างขึ้นหรือไม่
        if not check_box_file(file_base_name):
            print(f"ทำการสร้างไฟล์ .box ใหม่สำหรับ {file_base_name}")
            text2image(file_base_name, line_training_text)

        create_salt_pepper(file_base_name)

        line_count += 1


def main():
    # generate_image_from_tesseract_dataset()

    # generate_image_from_date()

    # generate_image_from_excel() 

    generate_image_from_sara()

if __name__ == '__main__':
    count = 1000
    line_count = 6000
    main()
