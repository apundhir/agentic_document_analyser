from fastapi import FastAPI, UploadFile, File
import uvicorn
import io
import base64
import json
from common.config import settings
from common.logger import configure_logger
from common.fireworks_client import FireworksClient
from PIL import Image

# Setup Logging
logger = configure_logger("visual_service")

app = FastAPI()

# Initialize Client
client = FireworksClient()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "visual_service", "model": settings.FIREWORKS_MODEL}

@app.post("/detect/layout")
async def detect_objects(file: UploadFile = File(...)):
    logger.info(f"Received detection request for {file.filename}")
    
    contents = await file.read()
    
    # Get Dimensions for de-normalization
    try:
        image = Image.open(io.BytesIO(contents))
        width, height = image.size
    except Exception as e:
        logger.error(f"Failed to load image: {e}")
        return {"error": "Invalid image file"}

    # Encode to base64
    base64_img = base64.b64encode(contents).decode('utf-8')
    
    # Prompt for Qwen-VL (Unified Extraction)
    prompt = """
    Analyze the document image, including complex layouts like DIAGRAMS, CHARTS, and FLOWCHARTS.
    Identify ALL layout elements (Title, Text, Header, Footer, Table, Image, Diagram).
    
    CRITICAL: Perform OCR on ALL text content, even text inside charts, diagrams, or shapes.
    
    Return a valid JSON list of objects.
    Each object must have:
    - "type": One of [title, text, header, footer, table, image, diagram]
    - "bbox": [xmin, ymin, xmax, ymax] (0-1000 scale)
    - "text": The extracted text content. If it's a diagram, extract the labels within it.
    
    Example:
    [
      {"type": "title", "bbox": [10, 10, 500, 50], "text": "System Architecture"},
      {"type": "diagram", "bbox": [10, 100, 900, 900], "text": "Flowchart logic..."},
      {"type": "text", "bbox": [50, 150, 200, 200], "text": "Input Node"}
    ]
    
    IMPORTANT: Return ONLY the JSON list. Do not include markdown formatting like ```json.
    """
    
    import re
    
    try:
        response_text = await client.analyze_image(prompt=prompt, base64_image=base64_img)
        logger.info(f"Raw Fireworks Response: {response_text}")
        
        # Robust Parsing: Find the first '[' and last ']'
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            regions = json.loads(json_str)
        else:
             # Fallback: try cleaning markdown
             clean_text = response_text.replace("```json", "").replace("```", "").strip()
             regions = json.loads(clean_text)
        
        results = []
        for r in regions:
            # Validate format
            if "bbox" not in r: continue
            
            box = r["bbox"]
            if len(box) != 4: continue
            
            # Normalize: Model returns [xmin, ymin, xmax, ymax] (0-1000)
            xmin, ymin, xmax, ymax = box
            
            x1 = (xmin / 1000) * width
            y1 = (ymin / 1000) * height
            x2 = (xmax / 1000) * width
            y2 = (ymax / 1000) * height
            
            results.append({
                "label": r.get("type", "text"),
                "confidence": 1.0, 
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "attributes": {
                    "text": r.get("text", "")
                }
            })
            
        logger.info(f"Parsed {len(results)} regions.")
        return {"detections": results}
        
    except Exception as e:
        logger.error(f"Detection failed: {e}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Visual Intelligence Service Failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.VISUAL_HOST, port=settings.VISUAL_PORT)
