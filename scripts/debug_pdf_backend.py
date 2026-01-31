import requests
import json
from PIL import Image, ImageDraw
import io
import base64
import sys

def create_dummy_pdf():
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,10), "Hello", fill=(255,255,0))
    b = io.BytesIO()
    img.save(b, format='PDF')
    return b.getvalue()

def test_analyze():
    print("Generating dummy PDF...")
    try:
        pdf_bytes = create_dummy_pdf()
        print(f"PDF Size: {len(pdf_bytes)} bytes")
        
        files = {'file': ('test.pdf', pdf_bytes, 'application/pdf')}
        
        print("Sending request to Orchestrator...")
        try:
            r = requests.post('http://localhost:8000/analyze', files=files, timeout=300)
            
            if r.status_code != 200:
                print(f"Error Status: {r.status_code}")
                print(f"Response: {r.text}")
                return
                
            data = r.json()
            doc = data.get('document', {})
            
            print("\n--- Response Layout ---")
            print(f"Document Keys: {list(doc.keys())}")
            
            if 'pages' not in doc:
                print("CRITICAL: 'pages' key MISSING in document!")
            else:
                pages = doc['pages']
                if pages is None:
                    print("CRITICAL: 'pages' is None!")
                else:
                    print(f"Pages count: {len(pages)}")
                    if len(pages) > 0:
                        p1 = pages[0]
                        print(f"Page 1 Keys: {list(p1.keys())}")
                        if 'base64_image' in p1:
                             b64 = p1['base64_image']
                             print(f"Page 1 base64_image: {str(b64)[:50]}...")
                        else:
                            print("CRITICAL: Page 1 missing 'base64_image'")
            
            if 'visual_elements' in doc:
                print(f"Visual Elements count: {len(doc['visual_elements'])}")
                
        except requests.exceptions.RequestException as re:
            print(f"Request failed: {re}")
            
    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    test_analyze()
