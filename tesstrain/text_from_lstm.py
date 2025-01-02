import os
import random
import pathlib
import subprocess
import re  # นำเข้าโมดูล re สำหรับ Regular Expression
import cv2
# File paths
training_text_file = 'langdata/langdata_lstm/tha/tha.training_text'
output_directory = 'tesstrain/data/DilleniaUPC-ground-truth'

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# Read and clean lines from the training text file
lines = []
allowed_chars = r'[ก-ฮะ-์่-๋็า-ูฤ-์เ-์แ-์ไ-์โ-์ใ-์า-์ฯๆ\s\.\(\)\/\-]'  # Thai letters, vowels, tone marks, and allowed symbols
with open(training_text_file, 'r', encoding='utf-8') as input_file:
    for line in input_file.readlines():
        # Remove all unwanted characters
        cleaned_line = ''.join(re.findall(allowed_chars, line))
        # Append the cleaned line if it's not empty
        if cleaned_line.strip():
            lines.append(cleaned_line)

# Shuffle lines randomly
random.shuffle(lines)

# Only keep a specific count of lines (for testing, setting count=1)
count = 1000
lines = lines[:count]


# Process each line to create the necessary training files
line_count = 0
for line in lines:
    random_size_font = random.randint(12, 25)
    random_exposure = random.randint(1, 2)
    # Prepare the output file for ground truth text
    training_text_file_name = pathlib.Path(training_text_file).stem
    line_training_text = os.path.join(output_directory, f'{training_text_file_name}_{line_count}.gt.txt')

    # Use UTF-8 encoding for the output file
    with open(line_training_text, 'w', encoding='utf-8') as output_file:
        output_file.writelines([line])

    # Base name for the generated image
    file_base_name = f'tha_{line_count}'
    print(f"size: {random_size_font}\nexposure:{random_exposure}")
    # Run text2image to generate the image
    subprocess.run([
        'text2image',
        '--font=DilleniaUPC',  # Ensure this font is available
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
