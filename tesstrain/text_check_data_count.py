# import os
# from collections import Counter

# def count_and_sort_characters(file_path):
#     if not os.path.exists(file_path):
#         print(f"File not found: {file_path}")
#         return None
    
#     # อ่านไฟล์และเก็บตัวอักษรทั้งหมด
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()
    
#     # ใช้ Counter เพื่อนับจำนวนตัวอักษร
#     char_count = Counter(content)
    
#     # เรียงลำดับตามจำนวนจากน้อยไปมาก
#     sorted_char_count = sorted(char_count.items(), key=lambda x: x[1])
    
#     # แสดงผลการเรียงลำดับ
#     for char, count in sorted_char_count:
#         print(f"'{char}': {count} times")
    
#     return sorted_char_count

# # ระบุพาธไฟล์
# file_path = "tesstrain/data/DilleniaUPC/all-gt"
# sorted_char_count = count_and_sort_characters(file_path)

# if sorted_char_count:
#     print("\nTotal unique characters:", len(sorted_char_count))

import os

def check_empty_box_files(folder_path):
    # สร้างรายการสำหรับเก็บชื่อไฟล์ที่ว่าง
    empty_files = []
    
    # วนลูปอ่านไฟล์ทั้งหมดในโฟลเดอร์
    for file_name in os.listdir(folder_path):
        # ตรวจสอบว่าไฟล์ตรงกับรูปแบบ tha_{ตัวเลข}.box
        if file_name.startswith("tha_") and file_name.endswith(".box"):
            # ตรวจสอบว่าเป็นไฟล์ (ไม่ใช่โฟลเดอร์)
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                # เปิดไฟล์และตรวจสอบว่ามีข้อมูลหรือไม่
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read().strip()
                    if not content:  # ถ้าเนื้อหาไฟล์ว่าง
                        empty_files.append(file_name)
    
    return empty_files

# ตัวอย่างการใช้งาน
folder_path = "E:/Project/Tesseract-FineTuning/tesstrain/data/DilleniaUPC-ground-truth"  # แทนที่ด้วย path ของโฟลเดอร์ที่ต้องการตรวจสอบ
empty_files = check_empty_box_files(folder_path)

if empty_files:
    print("ไฟล์ที่ว่างมีดังนี้:")
    print("\n".join(empty_files))
else:
    print("ไม่มีไฟล์ที่ว่าง")
