export interface BoundingBox {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export interface Attributes {
    text?: string;
    vlm_description?: string;
    html?: string;
    page_number?: number;
}

export interface Block {
    block_type: string;
    text: string;
    bounding_box: BoundingBox;
}

export interface VisualElement {
    type: string;
    confidence: number;
    bounding_box: BoundingBox;
    attributes: Attributes;
}

export interface Table {
    confidence: number;
    bounding_box: BoundingBox;
    header_rows: unknown[];
    body_rows: unknown[];
}

export interface Page {
    page_number: number;
    dimension: {
        width: number;
        height: number;
        unit: string;
    };
    blocks: Block[];
    base64_image?: string;
}

export interface DocumentContent {
    text: string;
    pages: Page[];
    entities: unknown[];
    visual_elements: VisualElement[];
    tables: Table[];
}

export interface AnalysisResponse {
    job_id: string;
    status: string;
    timestamp: string;
    document: DocumentContent;
}
