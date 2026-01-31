import cv2
import numpy as np
import pytest
from processors import ImageProcessor
import os

# Create a dummy noisy image for testing
def create_test_image():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.putText(img, "TEST", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # Add noise
    noise = np.random.randint(0, 50, (200, 200, 3))
    noisy_img = cv2.add(img, noise, dtype=cv2.CV_8U)
    return noisy_img

def create_skewed_image():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Create a rotated rectangle
    rect = ((100, 100), (100, 50), 30) # center, size, angle
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img, [box], 0, (255, 255, 255), 2)
    return img

def test_denoise():
    img = create_test_image()
    processed = ImageProcessor.denoise_image(img)
    assert processed is not None
    assert processed.shape == img.shape
    # Basic check: verify some processing happened (exact pixel comparison is hard for denoise)
    assert not np.array_equal(img, processed)

def test_deskew():
    img = create_skewed_image()
    processed = ImageProcessor.deskew_image(img)
    assert processed is not None
    # We expect the image to be rotated, dimensions might change slightly due to warpAffine 
    # but in our simple implementation we kept size same
    assert processed.shape == img.shape

if __name__ == "__main__":
    # Manually run if pytest not available in context
    try:
        test_denoise()
        print("Denoise Test Passed")
        test_deskew()
        print("Deskew Test Passed")
    except Exception as e:
        print(f"Test Failed: {e}")
