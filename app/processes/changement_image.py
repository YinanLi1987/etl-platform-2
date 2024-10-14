import cv2
import numpy as np
from pdf2image import convert_from_path
from google.cloud import storage
import os



def convert_pdf_to_images(pdf_path):
    """
    Convert each page of the PDF into a list of images.
    """
    return convert_from_path(pdf_path)
def combine_overlapping_lines(lines):
    """
    Combine overlapping or close bounding boxes into a single box.
    """
    combined_lines = []
    for (x1, y1, x2, y2) in lines:
        found = False
        for (cx1, cy1, cx2, cy2) in combined_lines:
            if (y1 < cy2 + 5) and (y2 > cy1 - 5):  # Check for overlap in y-axis
                combined_lines.remove((cx1, cy1, cx2, cy2))
                combined_lines.append((min(cx1, x1), min(cy1, y1), max(cx2, x2), max(cy2, y2)))
                found = True
                break
        if not found:
            combined_lines.append((x1, y1, x2, y2))
    return combined_lines

def crop_and_save_images(image, combined_lines, page_num, output_dir,color_name):
    """
    Crop and save images based on the bounding boxes.
    
    Parameters:
    - image: The original image.
    - combined_lines: List of bounding box coordinates.
    - page_num: The page number in the PDF.
    - output_dir: Directory to save cropped images.
    """
    # Initialize a GCS client
    storage_client = storage.Client()
    bucket_name = os.getenv('BUCKET_NAME')
    bucket=storage_client.bucket(bucket_name)
     # Initialize a list to hold URLs of uploaded images
   
    for i, (x1, y1, x2, y2) in enumerate(combined_lines):
        cropped_image = image[y1 - 10:y2 + 10, x1 - 1500:x2 + 1500]
        # Generate a unique name for the image
        cropped_image_name = f'page_{page_num + 1}_{color_name}_crop_{i + 1}.png'

       # Save locally if desired
        cropped_image_path = os.path.join(output_dir, cropped_image_name)
        cv2.imwrite(cropped_image_path, cropped_image)
        print(f'Saved locally: {cropped_image_path}')
        
        # Upload to GCS
        blob = bucket.blob(cropped_image_name)
        blob.upload_from_filename(cropped_image_path)  # Upload the file from local path
        print(f'Uploaded to GCS: {blob.public_url}') 


def detect_and_crop_regions_from_pdf(pdf_path, output_dir):
    """
    Detect red regions in a PDF and save cropped images.
    
    Parameters:
    - pdf_path: The path to the PDF file.
    - output_dir: Directory to save cropped images.
    """
    # Convert PDF pages to images
    pages = convert_pdf_to_images(pdf_path)
    
    # Create output directory if it doesn't exist
    # os.makedirs(output_dir, exist_ok=True)

   # Define lower and upper bounds for red, gold, blue, and green in HSV
    color_ranges = {
        
        'gold': [
            (np.array([15, 100, 100]), np.array([30, 255, 255]))  # Gold: yellow-orange
        ],
        'blue': [
            (np.array([100, 150, 0]), np.array([140, 255, 255]))  # Blue
        ],
        'green': [
            (np.array([40, 100, 100]), np.array([80, 255, 255]))  # Green
        ],
        'purple': [
            (np.array([130, 100, 100]), np.array([160, 255, 255]))  # Purple
        ]
    }


    # Process each page
    for page_num, page in enumerate(pages):
        # Convert PIL image to OpenCV format
        open_cv_image = np.array(page)
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

        # Convert to HSV color space
        hsv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)
        # Detect regions for each color
        for color_name, ranges in color_ranges.items():
            combined_mask = None
            for lower, upper in ranges:
                mask = cv2.inRange(hsv_image, lower, upper)
                if combined_mask is None:
                    combined_mask = mask
                else:
                    combined_mask = combined_mask | mask  # Combine all masks for the same color
            # Find contours in the combined mask for the color
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

       
            # Store bounding rectangles for red-detected lines
            lines = []
            for contour in contours:
                if cv2.contourArea(contour) > 10:  # Filter by contour area
                    (x, y, w, h) = cv2.boundingRect(contour)
                    lines.append((x - 1500, y - 30, x + w + 1500, y + h + 30))

            # Combine overlapping bounding boxes
            combined_lines = combine_overlapping_lines(lines)
            # Crop and save the regions, getting URLs
            crop_and_save_images(open_cv_image, combined_lines, page_num, output_dir, color_name)
         

