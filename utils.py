from pdf2image import convert_from_path
import numpy as np
from PIL import Image
import cv2
import os
import img2pdf
import shutil
def book_into_images(path, output_path, poppler_path = None):
    if poppler_path is None:
        images = convert_from_path(path, dpi=200)
    else:
        images = convert_from_path(path, poppler_path=poppler_path, dpi=200)
    for i in range(len(images)):
        images[i].save(output_path+'/page'+ str(i) +'.png', 'PNG')

def read_image(image_path):
    image = cv2.imread(image_path)
    return image

def crop_page(image):
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold_value = 128
    _, binary = cv2.threshold(grayscale, threshold_value, 255, cv2.THRESH_BINARY)
    rows_with_content = np.any(binary == 0, axis=1)
    cols_with_content = np.any(binary == 0, axis=0)
    top = np.argmax(rows_with_content)  
    bottom = len(rows_with_content) - np.argmax(np.flipud(rows_with_content)) 
    left = np.argmax(cols_with_content)  
    right = len(cols_with_content) - np.argmax(np.flip(cols_with_content)) 
    cropped_image = image[top:bottom, left:right]
    return cropped_image

def stretch_image(cropped_image, desired_dimensions, top, bottom, left, right, added_line_width):
    width = int(desired_dimensions[1]/2 - (left + right + added_line_width))
    height = int(desired_dimensions[0] - (top + bottom))
    stretched_image = cv2.resize(cropped_image, (width, height))
    return stretched_image

def add_margins(stretched_image, top, bottom, left, right):
    image_with_margins = cv2.copyMakeBorder(
        stretched_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(255, 255, 255)  # White margins
    )
    return image_with_margins

def concat_image(left_page, right_page, line):
    side_by_side_image = np.hstack((left_page, line, right_page))
    return side_by_side_image

def produce_landscape_page(left_page_path, right_page_path, desired_dimensions, top, bottom, right, left, added_line_width, line):
    left_page, right_page = read_image(left_page_path), read_image(right_page_path)
    left_cropped_page = crop_page(left_page)
    left_stretched_page = stretch_image(left_cropped_page, desired_dimensions, top, bottom, left, right, added_line_width)
    left_margined_page = add_margins(left_stretched_page, top, bottom, left, right)
                                     
    right_cropped_page = crop_page(right_page)
    right_stretched_page = stretch_image(right_cropped_page, desired_dimensions, top, bottom, left, right, added_line_width)
    right_margined_page = add_margins(right_stretched_page, top, bottom, right, left)

    landscape_page = concat_image(left_margined_page, right_margined_page, line)
    return landscape_page