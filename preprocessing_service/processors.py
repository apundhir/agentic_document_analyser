import cv2
import numpy as np
import logging

logger = logging.getLogger("preprocessing_service")

class ImageProcessor:
    @staticmethod
    def denoise_image(image: np.ndarray) -> np.ndarray:
        """
        Removes noise from the image using fastNlMeansDenoising.
        Good for 'salt and pepper' noise common in scans.
        """
        try:
            # Check if color or grayscale
            if len(image.shape) == 3:
                # h=10 is strength, 10, 7, 21 are window sizes
                denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            else:
                denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
            return denoised
        except Exception as e:
            logger.error(f"Denoising failed: {e}")
            return image # Return original on failure

    @staticmethod
    def deskew_image(image: np.ndarray) -> np.ndarray:
        """
        Corrects skew using Projection Profile method or MinAreaRect.
        Here we use minAreaRect on textual contours.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Invert colors (text should be white, bg black for contour detection)
            # Use adaptive thresholding to handle uneven lighting
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find all coordinates of non-zero pixels
            coords = np.column_stack(np.where(thresh > 0))
            
            if len(coords) == 0:
                logger.warning("No text found for deskewing.")
                return image

            # Get minimum area rectangle
            angle = cv2.minAreaRect(coords)[-1]
            
            # minAreaRect returns angle in range [-90, 0). 
            # We need to adjust it to represent the rotation needed.
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            logger.info(f"Detected skew angle: {angle}")

            # Rotate the image
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Add border to avoid cutting off corners during rotation
            # This is a simplification; for production, improved logic needed for padding
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return rotated

        except Exception as e:
            logger.error(f"Deskewing failed: {e}")
            return image
    
    @staticmethod
    def correct_orientation(image: np.ndarray) -> np.ndarray:
        """
        Traditional methods (tesseract OSD) are slow. 
        For now, we assume upright. 
        TODO: Implement deep-learning based orientation classifier (0, 90, 180, 270)
        """
        return image
