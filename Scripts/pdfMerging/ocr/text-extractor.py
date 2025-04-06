
from PIL import Image
import pytesseract

def extract_text(image_path):
    """
    Extracts text from an image at the specified path using OCR.

    Parameters:
    image_path (str): The file path to the image from which to extract text.

    Returns:
    str: The extracted text.
    """
    try:
        # Open the image file
        with Image.open(image_path) as img:
            # Use pytesseract to do OCR on the image
            text = pytesseract.image_to_string(img)
            return text
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Path to the image file
    image_path = 'in.png'
    # Extract text from the image
    extracted_text = extract_text(image_path)
    print(extracted_text)
