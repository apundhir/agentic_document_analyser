from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import numpy as np
import cv2
from preprocessing_service.processors import ImageProcessor
from common.config import settings
from common.logger import configure_logger

# Configure Structured Logging
logger = configure_logger("preprocessing_service")

app = FastAPI(title="Document Preprocessing Service", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info(f"Service started in {settings.ENV} mode", 
                extra={"config": settings.model_dump(mode='json')})

@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy", "service": "preprocessing"}

@app.post("/preprocess/normalize")
async def normalize_document(file: UploadFile = File(...)):
    """
    Main endpoint to ingest a raw document image and apply normalization.
    Steps:
    1. Validate Image
    2. Remove Noise (Denoise)
    3. Correct Orientation (Deskew) - Placeholder for now
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read image into numpy array
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
             raise HTTPException(status_code=400, detail="Invalid image file or corrupt data")
        
        if img is None:
             raise HTTPException(status_code=400, detail="Invalid image file or corrupt data")
        
        # Get original dims
        height, width, _ = img.shape

        # Apple Processing Steps
        logger.info("Starting Denoising...")
        denoised_img = ImageProcessor.denoise_image(img)
        
        logger.info("Starting Deskewing...")
        processed_img = ImageProcessor.deskew_image(denoised_img)
        
        # Encode back to memory to return or pass forward
        # For this endpoint, we might want to return the processed image bytes 
        # OR save it to shared storage and return the path. 
        # For now, let's return metadata + success status.
        
        final_h, final_w = processed_img.shape[:2]
        
        return {
            "filename": file.filename,
            "original_dims": {"width": width, "height": height},
            "processed_dims": {"width": final_w, "height": final_h},
            "steps_completed": ["denoise", "deskew"],
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/preprocess/pdf_to_images")
async def pdf_to_images(file: UploadFile = File(...)):
    """
    Convert PDF to a list of images (Base64 encoded).
    """
    if file.content_type != "application/pdf":
         raise HTTPException(status_code=400, detail="File must be a PDF")
    
    import io
    import base64
    from pdf2image import convert_from_bytes
    
    try:
        contents = await file.read()
        
        # Convert to list of PIL Images
        # poppler_path can be omitted if it's in PATH
        images = convert_from_bytes(contents)
        
        results = []
        for i, img in enumerate(images):
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            results.append({
                "page_number": i + 1,
                "base64_image": img_str,
                "width": img.width,
                "height": img.height
            })
            
        return {"pages": results, "total_pages": len(results)}
        
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        # Hint about poppler if it's missing
        if "poppler" in str(e).lower():
            raise HTTPException(status_code=500, detail="PDF engine (poppler) missing. Please install poppler-utils.")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
