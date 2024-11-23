from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()
completion = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)

print(completion.choices[0].message)