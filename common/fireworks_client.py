from openai import AsyncOpenAI
from common.config import settings
from common.logger import configure_logger

logger = configure_logger("fireworks_client")

class FireworksClient:
    def __init__(self):
        if not settings.FIREWORKS_API_KEY:
            logger.warning("FIREWORKS_API_KEY is not set. Cloud features will fail.")
        
        self.client = AsyncOpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=settings.FIREWORKS_API_KEY,
            timeout=120.0, # Explicit 2 minute timeout
            max_retries=5
        )
        self.model = settings.FIREWORKS_MODEL

    def encode_image(self, image_path: str) -> str:
        """Encodes a local image file to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def analyze_image(self, image_path: str = None, prompt: str = "", base64_image: str = None) -> str:
        """
        Sends an image to the VLM and returns the test response.
        Accepts either image_path or base64_image.
        """
        try:
            if base64_image is None:
                if image_path:
                    # distinct from async logic, but file I/O is fast enough or could be asyncified too if needed
                    base64_image = self.encode_image(image_path)
                else:
                    raise ValueError("Either image_path or base64_image must be provided")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
                temperature=0.0,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Fireworks API call failed: {str(e)}", exc_info=True)
            raise e
