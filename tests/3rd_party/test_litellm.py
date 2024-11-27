import os
from typing import Optional

import asyncio
from dotenv import load_dotenv
import litellm

# Load environment variables from .env file
load_dotenv()

async def test_litellm_groq() -> Optional[str]:
    """
    Test the Groq API connection using LiteLLM.
    
    Returns:
        Optional[str]: The response text if successful, None if failed
    """
    try:
        # Retrieve the API key for Groq from environment variables
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        os.environ["GROQ_API_KEY"] = api_key
        
        # Make a simple test request
        response = await litellm.acompletion(
            model="groq/mixtral-8x7b-32768",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, API test successful!'"
                }
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        import traceback
        print(f"Error testing Groq API via LiteLLM: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    print("Testing Groq API connection via LiteLLM...")
    response = asyncio.run(test_litellm_groq())
    
    if response:
        print("✅ API test successful!")
        print(f"Response: {response}")
    else:
        print("❌ API test failed!")