import sys
import os
# Add root to python path
sys.path.append(os.getcwd())

from common.fireworks_client import FireworksClient
from common.logger import configure_logger

logger = configure_logger("test_fireworks")

def main():
    try:
        client = FireworksClient()
        image_path = "test2.png"
        
        if not os.path.exists(image_path):
            logger.error(f"Image {image_path} not found!")
            return

        logger.info(f"Sending {image_path} to Fireworks (Qwen2-VL)...")
        prompt = "Describe this image in detail and list any visible text."
        
        response = client.analyze_image(image_path, prompt)
        
        logger.info("Response received:")
        print(response)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    main()
