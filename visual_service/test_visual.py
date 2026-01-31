import pytest
import numpy as np
import cv2
from detector import ObjectDetector

def test_detector_loading():
    # Use yolov8n.pt as it is small and standard
    detector = ObjectDetector("yolov8n.pt")
    assert detector.model is not None

def test_inference():
    detector = ObjectDetector("yolov8n.pt")
    # Create a dummy image
    img = np.zeros((640, 640, 3), dtype=np.uint8)
    # Draw a rectangle to potentially confuse it or just pass blank
    cv2.rectangle(img, (100, 100), (200, 200), (255, 255, 255), -1)
    
    detections = detector.detect(img)
    # It might detect nothing on a blank/dummy image, but it shouldn't crash
    assert isinstance(detections, list)
    
if __name__ == "__main__":
    try:
        test_detector_loading()
        print("Model Loading Test Passed")
        test_inference()
        print("Inference Test Passed")
    except Exception as e:
        print(f"Test Failed: {e}")
