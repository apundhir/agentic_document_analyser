from paddleocr import LayoutDetection
import logging
import numpy as np
import cv2

logger = logging.getLogger("visual_service")

class ObjectDetector:
    def __init__(self, model_name: str = "PP-DocLayout_plus-L"):
        """
        Initialize PaddleOCR LayoutDetection.
        Current implementation ignores model_name as LayoutDetection 
        uses its own internal config/weights management (usually PP-Structure).
        """
        try:
            logger.info("Loading PaddleOCR LayoutDetection model...")
            # Initialize the model as per L6.ipynb
            self.model = LayoutDetection()
            logger.info("PaddleOCR LayoutDetection loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load PaddleOCR LayoutDetection: {e}")
            self.model = None

    def detect(self, image: np.ndarray, conf_threshold: float = 0.4):
        """
        Run layout analysis on an image using PaddleOCR LayoutDetection.
        Returns a list of detections with label, confidence, and bbox (x1, y1, x2, y2).
        """
        if self.model is None:
            return {"error": "Model not loaded"}

        try:
            # LayoutDetection.predict accepts image path or numpy array
            # We pass numpy array directly
            results = self.model.predict(image)
            
            # Parsing results based on L6.ipynb output structure
            # The result is typically a list of dicts or objects depending on version.
            # L6.ipynb snippet:
            # layout_result = layout_engine.predict(image_path)
            # regions = []
            # for box in layout_result[0]['boxes']: ... Or results IS the list if simpler
            
            detections = []
            
            # Handle potential nested list return
            # It seems from L6.ipynb logs: "layout_result" might be the list of boxes directly or wrapped.
            # We'll check the structure.
            
            target_list = results
            
            # Defensively check types
            if isinstance(results, list) and len(results) > 0 and 'boxes' in results[0]:
                 # PP-Structure v2 style often returns list of {boxes: [...]}
                 target_list = results[0]['boxes']
            elif isinstance(results, list):
                 # Sometimes it's a direct list of elements
                 target_list = results

            for item in target_list:
                # Structure from notebook: {'label': 'text', 'score': 0.98, 'bbox': [x1, y1, x2, y2]}
                # Note: notebook says 'bbox' is [x1, y1, x2, y2], but logs showed 'coordinate' in one version.
                # We'll check both.
                
                label = str(item.get('label', 'unknown'))
                score = float(item.get('score', 0.0))
                
                # Check for bbox or coordinate
                raw_bbox = item.get('bbox') or item.get('coordinate')
                
                if not raw_bbox or len(raw_bbox) != 4:
                     continue
                
                # Convert bbox to list of floats
                bbox = [float(x) for x in raw_bbox]
                
                if score < conf_threshold:
                    continue
                    
                detections.append({
                    "label": label,
                    "confidence": score,
                    "bbox": {
                        "x1": bbox[0], "y1": bbox[1], 
                        "x2": bbox[2], "y2": bbox[3]
                    }
                })

            return detections

        except Exception as e:
            logger.error(f"Inference layout failed: {e}")
            return []
