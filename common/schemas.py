from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class Dimension(BaseModel):
    width: int
    height: int
    unit: str = "pixel"

class TextAnchor(BaseModel):
    start_offset: int
    end_offset: int

class Entity(BaseModel):
    type: str
    mention_text: str
    normalized_value: Optional[str] = None
    confidence: float
    text_anchor: Optional[TextAnchor] = None
    bounding_box: Optional[BoundingBox] = None
    properties: List['Entity'] = []

class VisualElement(BaseModel):
    type: str # seal, signature, logo, table, figure
    confidence: float
    bounding_box: BoundingBox
    attributes: Dict[str, Any] = {}

class TableCell(BaseModel):
    text: str
    row_span: int = 1
    col_span: int = 1
    bounding_box: Optional[BoundingBox] = None

class TableRow(BaseModel):
    cells: List[TableCell]

class Table(BaseModel):
    confidence: float
    header_rows: List[TableRow] = []
    body_rows: List[TableRow] = []
    bounding_box: Optional[BoundingBox] = None

class Block(BaseModel):
    block_type: str # paragraph, title, etc
    text: str
    bounding_box: Optional[BoundingBox] = None

class Page(BaseModel):
    page_number: int
    dimension: Dimension
    orientation: int = 0
    blocks: List[Block] = []
    base64_image: Optional[str] = None # Added for PDF rendering on Frontend

class DocumentContent(BaseModel):
    text: str # Full raw text
    pages: List[Page] = []
    entities: List[Entity] = []
    visual_elements: List[VisualElement] = []
    tables: List[Table] = []

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    timestamp: str
    document: DocumentContent
