import time
import logging
import requests
import os

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

# Service URLs (Localhost for now)
PREPROCESSING_URL = "http://localhost:8001/preprocess/normalize"
VISUAL_URL = "http://localhost:8002/detect/layout"

class DocumentWorkflow:
    def __init__(self, file_path: str):
        # Resolve to absolute path
        self.file_path = os.path.abspath(file_path)
        self.filename = os.path.basename(file_path)

    def run(self):
        """
        Executes the basic pipeline:
        1. Preprocess (Denoise/Deskew)
        2. Visual Analysis (Layout Detection)
        3. Extraction (TODO)
        """
        logger.info(f"Starting workflow for {self.filename}")
        
        if not os.path.exists(self.file_path):
            logger.error(f"File not found: {self.file_path}")
            return

        # Step 1: Preprocessing
        try:
            logger.info("Step 1: Sending to Preprocessing Service...")
            with open(self.file_path, "rb") as f:
                files = {"file": (self.filename, f, "image/jpeg")} # Assuming JPEG/PNG for prototype
                resp = requests.post(PREPROCESSING_URL, files=files)
            
            if resp.status_code != 200:
                logger.error(f"Preprocessing failed: {resp.text}")
                return
            
            data = resp.json()
            logger.info(f"Preprocessing complete. Metadata: {data}")
            # In a real system, we'd get a URL/Path to the processed image back.
            # For this MVP, we assume the file on disk is what we use, 
            # or the service returns bytes (which we aren't handling here for simplicity).
            # Let's verify the visual service can see the file.
            
        except Exception as e:
            logger.error(f"Preprocessing Step Exception: {e}")
            return

        # Step 2: Visual Intelligence
        try:
            logger.info("Step 2: Sending to Visual Intelligence Service...")
            # Ideally we send the *processed* image. 
            # Here we send the original again just to test the integration flow.
            with open(self.file_path, "rb") as f:
                files = {"file": (self.filename, f, "image/jpeg")} 
                resp = requests.post(VISUAL_URL, files=files)
            
            if resp.status_code != 200:
                logger.error(f"Visual Analysis failed: {resp.text}")
                return
            
            layout_data = resp.json()
            detections = layout_data.get("detections", [])
            logger.info(f"Visual Analysis complete. Found {len(detections)} elements.")
            for d in detections:
                logger.info(f" - Detected {d['label']} at {d['confidence']:.2f}")

        except Exception as e:
            logger.error(f"Visual Step Exception: {e}")
            return

        logger.info("Workflow completed successfully.")

if __name__ == "__main__":
    workflow = DocumentWorkflow("sample_invoice.jpg")
    workflow.run()
