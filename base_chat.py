from groq import Groq
from dotenv import load_dotenv
import base64 

load_dotenv()
client = Groq()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

image_data = encode_image("circuit.png")

completion = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        # {"role": "user", "content": "What components are this simple circuit made of (dont count cables)", "image": image_data}
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "What components are this simple circuit made of (dont count cables)"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
          ]
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)

print(completion.choices[0].message)