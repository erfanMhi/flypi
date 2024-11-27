import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

def test_groq_connection() -> Optional[str]:
    """
    Test the Groq API connection using the provided API key.
    
    Returns:
        Optional[str]: The response text if successful, None if failed
    """
    try:
        # Initialize the Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        client = Groq(api_key=api_key)
        
        # Make a simple test request
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, API test successful!'"
                }
            ],
            model="mixtral-8x7b-32768",  # Using Mixtral model
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error testing Groq API: {str(e)}")
        return None

if __name__ == "__main__":
    print("Testing Groq API connection...")
    response = test_groq_connection()
    
    if response:
        print("✅ API test successful!")
        print(f"Response: {response}")
    else:
        print("❌ API test failed!")