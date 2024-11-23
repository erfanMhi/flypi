from groq import Groq
from dotenv import load_dotenv
import base64 

load_dotenv()
client = Groq()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Encode all required images
battery_data = encode_image("battery.png")
resistor_data = encode_image("resistor.png")
circuit_data = encode_image("circuit.png")

# First call - Teaching about battery
completion_battery = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "This is what a battery looks like in circuit diagrams. It's represented by a long and short parallel lines."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{battery_data}"}}
            ]
        }
    ],
    temperature=1,
    max_tokens=1024,
)
battery_knowledge = completion_battery.choices[0].message.content

# Second call - Teaching about resistor
completion_resistor = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "This is what a resistor looks like in circuit diagrams. It's shown as a zigzag line or rectangular block."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{resistor_data}"}}
            ]
        }
    ],
    temperature=1,
    max_tokens=1024,
)
resistor_knowledge = completion_resistor.choices[0].message.content

# Final call - Analyzing the circuit with context
completion_circuit = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"""Let me explain what we've learned:
                1. Battery: {battery_knowledge}
                2. Resistor: {resistor_knowledge}
                
                Now, looking at this circuit, what components are present in it? (don't count cables)"""},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{circuit_data}"}}
            ]
        }
    ],
    temperature=1,
    max_tokens=1024,
)

print(completion_circuit.choices[0].message.content)