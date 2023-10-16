# views.py
import os

import cv2
import pytesseract
import webcolors
from django.shortcuts import render
from django.http import JsonResponse
from .forms import ImageUploadForm
from .models import UploadedImage
from googletrans import Translator


# Calculate the contrast ratio between two colors
def calculate_contrast_ratio(color1, color2):
    # Calculate relative luminance for color1
    luminance1 = 0.2126 * color1[2] + 0.7152 * color1[1] + 0.0722 * color1[0]

    # Calculate relative luminance for color2
    luminance2 = 0.2126 * color2[2] + 0.7152 * color2[1] + 0.0722 * color2[0]

    # Ensure luminance1 is the lighter color
    if luminance1 < luminance2:
        luminance1, luminance2 = luminance2, luminance1

    # Calculate contrast ratio
    contrast_ratio = (luminance1 + 0.05) / (luminance2 + 0.05)

    return contrast_ratio

# Evaluate the contrast level based on the contrast ratio
def evaluate_contrast_level(contrast_ratio):
    if contrast_ratio >= 7.0:
        return "AAA (Large Text)"
    elif contrast_ratio >= 4.5:
        return "AA (Normal Text)"
    else:
        return "Fail"

# Find the closest color name using the Euclidean distance in RGB space
def closest_color(requested_color):
    min_distance = float('inf')
    closest_name = None
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        color_rgb = webcolors.hex_to_rgb(key)
        r_c, g_c, b_c = color_rgb
        r_d, g_d, b_d = requested_color
        distance = (r_c - r_d) ** 2 + (g_c - g_d) ** 2 + (b_c - b_d) ** 2
        if distance < min_distance:
            min_distance = distance
            closest_name = name
    return closest_name

# Analyze the image to get color and contrast information
def analyze_logo(image_path, target_language):
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Calculate the average color of the logo
    average_color = cv2.mean(image)[:3]

    # Convert the average color to CSS color code (e.g., "#RRGGBB")
    css_color = "#{:02X}{:02X}{:02X}".format(int(average_color[2]), int(average_color[1]), int(average_color[0]))

    # Find the closest color name to the average color
    closest_color_name = closest_color(average_color)

    # Calculate contrast ratio with a reference color (e.g., white)
    reference_color = [1.0, 1.0, 1.0]  # White color
    contrast_ratio = calculate_contrast_ratio(average_color, reference_color)

    # Perform OCR using pytesseract
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    detected_text = pytesseract.image_to_string(gray_image,lang='eng')

    # Translate the detected text to the target language
    try:
        # Translate the detected text to the target language
        translator = Translator()
        translated_text = translator.translate(detected_text, dest=target_language).text
    except Exception as e:
        # Handle the exception gracefully
        translated_text = "Translation failed: " + str(e)

    return {
        'average_color': css_color,
        'color_name': closest_color_name,
        'contrast_ratio': contrast_ratio,
        'contrast_level': evaluate_contrast_level(contrast_ratio),
        'detected_text': detected_text,
        'translated_text': translated_text,
    }

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_images = request.FILES.getlist('images')
            target_language = request.POST.get('target_language')  # Get the selected target language

            analysis_results = []

            for uploaded_image in uploaded_images:
                # Create an instance of UploadedImage
                uploaded_file = UploadedImage(file=uploaded_image)
                uploaded_file.save()

                # Analyze the logo using the analyze_logo function with the selected target language
                analysis_result = analyze_logo(uploaded_file.file.path, target_language)

                analysis_results.append(analysis_result)

                # Remove the uploaded image file after analysis
                os.remove(uploaded_file.file.path)

            return render(request, 'image_analysis/upload_image.html', {'results': analysis_results})
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        form = ImageUploadForm()

    return render(request, 'image_analysis/upload_image.html', {'form': form})


