import os
import random
import pathlib
import subprocess

# File paths
training_text_file = 'langdata/langdata_lstm/tha/tha.training_text'
output_directory = 'tesstrain/data/DilleniaUPC-ground-truth'

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# Read and shuffle the lines in the training text file
lines = []
with open(training_text_file, 'r', encoding='utf-8') as input_file:  # Added encoding='utf-8'
    lines = [line.strip() for line in input_file.readlines()]

random.shuffle(lines)

# Only keep a specific count of lines (for testing, setting count=1)
count = 1
lines = lines[:count]

# Process each line to create the necessary training files
line_count = 0
for line in lines:
    # Prepare the output file for ground truth text
    training_text_file_name = pathlib.Path(training_text_file).stem
    line_training_text = os.path.join(output_directory, f'{training_text_file_name}_{line_count}.gt.txt')

    # Use UTF-8 encoding for the output file
    with open(line_training_text, 'w', encoding='utf-8') as output_file:
        output_file.writelines([line])


    # Base name for the generated image
    file_base_name = f'tha_{line_count}'

    # Run text2image to generate the image
    subprocess.run([
        'text2image',
        '--font=DilleniaUPC',  # Ensure this font is available
        f'--text={line_training_text}',
        f'--outputbase={os.path.join(output_directory, file_base_name)}',
        '--max_pages=1',
        '--ptsize=12',
        '--strip_unrenderable_words',
        '--leading=20',
        '--xsize=3600',
        '--ysize=480',
        '--char_spacing=0.05',
        '--exposure=1',
        '--unicharset_file=langdata/tha.unicharset'
    ])

    line_count += 1
