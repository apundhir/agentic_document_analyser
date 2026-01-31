from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import shutil
import os
import uuid
import time
from common.config import settings
from common.logger import configure_logger
from common.schemas import AnalysisResponse, DocumentContent, Page, Dimension

# Configure Logging
logger = configure_logger("orchestrator")

app = FastAPI(title="Orchestrator Service", version="2.0.0")

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "/tmp/doc_analysis_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "orchestrator", "mode": "cloud_native"}

async def call_service(client: httpx.AsyncClient, url: str, file_path: str, filename: str, content_type: str):
    """Helper to call a service with a file upload."""
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            
        files = {"file": (filename, file_content, content_type)}
        resp = await client.post(url, files=files, timeout=60.0) # Increased timeout for VLM
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Service call to {url} failed: {e}")
        return None

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    """
    Main entry point for the Frontend.
    Cloud Native Flow: Preprocess -> Visual Intelligence (Unified Layout+OCR+Ordering)
    """
    job_id = str(uuid.uuid4())
    logger.info(f"Received job {job_id} for file {file.filename}")
    
    # Save temp file
    file_path = os.path.join(TEMP_DIR, f"{job_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Preprocessing & Page Split
            pages_to_process = []
            
            if file.content_type == "application/pdf":
                logger.info(f"Job {job_id}: Detected PDF. converting to images...")
                pp_url = f"http://{settings.PREPROCESSING_HOST}:{settings.PREPROCESSING_PORT}/preprocess/pdf_to_images"
                pp_data = await call_service(client, pp_url, file_path, file.filename, file.content_type)
                
                if not pp_data or "pages" not in pp_data:
                     raise HTTPException(status_code=500, detail="PDF conversion failed")
                
                # Prepare pages for Visual Service
                # Visual Service expects 'file' upload. We need to convert base64 back to bytes.
                import base64
                import io
                
                for p in pp_data["pages"]:
                    img_bytes = base64.b64decode(p["base64_image"])
                    pages_to_process.append({
                        "page_number": p["page_number"],
                        "bytes": img_bytes,
                        "dims": {"width": p["width"], "height": p["height"]}
                    })
            else:
                 # Single Image Flow
                 # Preprocess (Denoise) - Optional but good for consistency
                 logger.info(f"Job {job_id}: Sending to Preprocessing (Normalize)...")
                 pp_url = f"http://{settings.PREPROCESSING_HOST}:{settings.PREPROCESSING_PORT}/preprocess/normalize"
                 pp_data = await call_service(client, pp_url, file_path, file.filename, file.content_type)
                 
                 if not pp_data: raise HTTPException(status_code=500, detail="Preprocessing failed")
                 
                 dims = pp_data.get("processed_dims", {"width": 0, "height": 0})
                 
                 # Read original file bytes for Visual Service 
                 # (Visual Service does its own normalization, so we can send raw file or processed. 
                 # For now sending raw file as Visual Service handles it well)
                 with open(file_path, "rb") as f:
                     raw_bytes = f.read()
                     
                 pages_to_process.append({
                     "page_number": 1,
                     "bytes": raw_bytes,
                     "dims": dims
                 })

            # Step 2: Visual Intelligence (Parallel)
            logger.info(f"Job {job_id}: Sending {len(pages_to_process)} pages to Visual Intelligence in parallel...")
            visual_url = f"http://{settings.VISUAL_HOST}:{settings.VISUAL_PORT}/detect/layout"

            async def process_page(page_data):
                """Helper task for single page processing"""
                files = {"file": ("page.png", page_data["bytes"], "image/png")}
                try:
                    resp = await client.post(visual_url, files=files, timeout=120.0) # 120s per page
                    resp.raise_for_status()
                    vis_data = resp.json()
                    
                    detections = vis_data.get("detections", [])
                    
                    # Transform Blocks
                    final_blocks = []
                    for d in detections:
                        attr = d.get("attributes", {})
                        final_blocks.append({
                            "type": d.get("label", "unknown"),
                            "content": attr.get("text", ""),
                            "bbox": d.get("bbox", {}),
                            "confidence": d.get("confidence", 1.0),
                            "vlm_description": attr.get("vlm_description", ""),
                            "html": attr.get("html", "")
                        })

                    # Sort Blocks
                    def sort_key(b):
                        bbox = b["bbox"]
                        if not bbox: return (0, 0)
                        y_rounded = round(bbox.get("y1", 0) / 20) * 20
                        return (y_rounded, bbox.get("x1", 0))

                    final_blocks.sort(key=sort_key)
                    
                    # Page Text
                    page_text = "\n\n".join([b.get('content', '') for b in final_blocks])
                    
                    # Map BBox Helper
                    def map_bbox(b_dict):
                        if not b_dict: return None
                        return {
                            "x1": b_dict.get("x1", 0),
                            "y1": b_dict.get("y1", 0),
                            "x2": b_dict.get("x2", 0),
                            "y2": b_dict.get("y2", 0)
                        }

                    # Pydantic Blocks
                    pydantic_blocks = [
                        {
                            "block_type": b.get("type", "unknown"),
                            "text": b.get("content", ""),
                            "bounding_box": map_bbox(b.get("bbox"))
                        } for b in final_blocks
                    ]
                    
                    # Visual Elements & Tables
                    page_visual_elements = []
                    page_tables = []
                    
                    for b in final_blocks:
                        b_type = b.get("type")
                        qt_block = {
                                "type": b_type,
                                "confidence": b.get("confidence", 0.0),
                                "bounding_box": map_bbox(b.get("bbox")),
                                "attributes": {
                                    "text": b.get("content", ""),
                                    "vlm_description": b.get("vlm_description"),
                                    "html": b.get("html"),
                                    "page_number": page_data["page_number"] # Track page
                                }
                        }
                        page_visual_elements.append(qt_block)
                        
                        if b_type == "table":
                            page_tables.append({
                                "confidence": b.get("confidence", 0.0),
                                "bounding_box": map_bbox(b.get("bbox")),
                                "header_rows": [], 
                                "body_rows": []
                            })
                    
                    # Prepare base64 image
                    import base64
                    page_b64 = base64.b64encode(page_data["bytes"]).decode('utf-8')
                    logger.info(f"Page {page_data['page_number']} base64 length: {len(page_b64)}")
                    
                    result_page = Page(
                        page_number=page_data["page_number"],
                        dimension=Dimension(width=page_data["dims"]["width"], height=page_data["dims"]["height"]),
                        blocks=pydantic_blocks,
                        base64_image=f"data:image/png;base64,{page_b64}"
                    )
                    
                    return {
                        "page": result_page,
                        "text": page_text,
                        "visual_elements": page_visual_elements,
                        "tables": page_tables
                    }

                except Exception as e:
                    import traceback
                    logger.error(f"Visual analysis failed for page {page_data['page_number']}: {repr(e)}")
                    logger.error(traceback.format_exc())
                    # Return empty/failed page structure to keep indexing or just skip? 
                    # Returning None allows filtering.
                    return None

            # Execute Parallel
            import asyncio
            results = await asyncio.gather(*(process_page(p) for p in pages_to_process))
            
            # Aggregate Results
            final_pages = []
            all_tables = []
            all_visual_elements = []
            full_text_buffer = []

            for res in results:
                if res:
                    final_pages.append(res["page"])
                    full_text_buffer.append(res["text"])
                    all_visual_elements.extend(res["visual_elements"])
                    all_tables.extend(res["tables"])
            
            # Sort pages by page number strictly
            final_pages.sort(key=lambda p: p.page_number)

            response = AnalysisResponse(
                job_id=job_id,
                status="completed",
                timestamp=str(time.time()),
                document=DocumentContent(
                    text="\n\n--- PAGE BREAK ---\n\n".join(full_text_buffer),
                    pages=final_pages,
                    entities=[],
                    visual_elements=all_visual_elements,
                    tables=all_tables
                )
            )
            return response
            
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
