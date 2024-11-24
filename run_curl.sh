#!/bin/bash

IMAGE_PATH="C:\\Users\\aleja\\OneDrive\\Escritorio\\flypi\\circuit.png"

# Check if file exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: File $IMAGE_PATH does not exist"
    exit 1
fi

# Convert image to base64
BASE64_IMAGE=$(base64 -i "$IMAGE_PATH")

# Create JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
    "image_data": "$BASE64_IMAGE",
    "content_type": "image/png"
}
EOF
)

# Send request to API
curl -X POST \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    http://localhost:8000/api/v1/retrieve-circuit-schema-test
