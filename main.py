import argparse
import os
import cv2
import numpy as np
import argparse
import shutil
import img2pdf
from utils import book_into_images, produce_landscape_page

def main():
    parser = argparse.ArgumentParser(description="Convert a PDF into a landscaped version.")
    
    parser.add_argument("path", type=str, help="Path to the input PDF.")
    parser.add_argument("output_pdf", type=str, help="Path for the output landscaped PDF.")
    
    # Optional arguments with defaults
    parser.add_argument("--poppler_path", type=str, help="Path to the Poppler library bin directory.")
    parser.add_argument("--output_path", type=str, default="temp_book", help="Temporary directory for intermediate images.")
    parser.add_argument("--landscape_images_path", type=str, default="processed_book", help="Directory for processed landscape images.")
    parser.add_argument("--desired_dimensions", type=int, nargs=2, default=(2480, 3508), help="Desired dimensions of the output images (width, height).")
    parser.add_argument("--top", type=int, default=25, help="Top margin for cropping.")
    parser.add_argument("--bottom", type=int, default=10, help="Bottom margin for cropping.")
    parser.add_argument("--left", type=int, default=10, help="Left margin for cropping.")
    parser.add_argument("--right", type=int, default=20, help="Right margin for cropping.")
    parser.add_argument("--added_line_width", type=int, default=1, help="Width of the line added between pages in pixels.")
    
    args = parser.parse_args()

    # Prepare paths
    os.makedirs(args.output_path, exist_ok=True)
    os.makedirs(args.landscape_images_path, exist_ok=True)

    # Convert book into images
    book_into_images(args.path,  args.output_path, args.poppler_path)

    # Prepare images for landscape
    all_image_paths = os.listdir(args.output_path)
    all_image_paths.sort(key=lambda x: int(x[4:-4]))
    full_image_paths = [os.path.join(args.output_path, i) for i in all_image_paths]

    line = np.ones((args.desired_dimensions[0], args.added_line_width * 2, 3), dtype=np.uint8) * np.array((0, 0, 0), dtype=np.uint8)

    count = 0
    for left_page_path, right_page_path in zip(full_image_paths[::2], full_image_paths[1::2]):
        landscape_page = produce_landscape_page(
            left_page_path, right_page_path,
            args.desired_dimensions, args.top, args.bottom,
            args.right, args.left, args.added_line_width, line
        )
        output_image_path = os.path.join(args.landscape_images_path, f"page{count}.png")
        cv2.imwrite(output_image_path, landscape_page)
        count += 1

    # Create PDF from processed images
    all_image_paths = os.listdir(args.landscape_images_path)
    all_image_paths.sort(key=lambda x: int(x[4:-4]))
    full_image_paths = [os.path.join(args.landscape_images_path, i) for i in all_image_paths]

    with open(args.output_pdf, "wb") as f:
        f.write(img2pdf.convert(full_image_paths))

    # Clean up temporary directories
    shutil.rmtree(args.landscape_images_path)
    shutil.rmtree(args.output_path)

if __name__ == "__main__":
    main()