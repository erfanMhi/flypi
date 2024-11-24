import base64
import requests
import os

# Path to image (using raw string to handle Windows paths)
IMAGE_PATH = r"circuit.png"

# Check if file exists
if not os.path.exists(IMAGE_PATH):
    print(f"Error: File {IMAGE_PATH} does not exist")
    exit(1)

# Read and convert image to base64
with open(IMAGE_PATH, 'rb') as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

# Prepare payload
payload = {
    "image_data": base64_image,
    "content_type": "image/png"
}

# Send request to API
response = requests.post(
    'http://localhost:8000/api/v1/retrieve-circuit-schema-test',
    json=payload
)

# Print response
print(f"Status Code: {response.status_code}")
print("Response:", response.text) 