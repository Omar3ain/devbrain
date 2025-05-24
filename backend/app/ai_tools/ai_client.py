from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        api_key = os.getenv("OPEN_ROUTER_KEY")
        if not api_key:
            raise ValueError("OPEN_ROUTER_KEY environment variable is not set")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "X-Title": "DevBrain AI Tools"
            }
        )

    def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        """
        Generate a response using the AI model.
        
        Args:
            prompt (str): The user prompt
            system_prompt (str): The system prompt that sets the context
            max_tokens (int): Maximum number of tokens in the response
            temperature (float): Controls randomness (0.0 to 1.0)
            
        Returns:
            str: The generated response
        """
        try:
            response = self.client.chat.completions.create(
                model="mistralai/mistral-7b-instruct",  # Cost-effective model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            raise 