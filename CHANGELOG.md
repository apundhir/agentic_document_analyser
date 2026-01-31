# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2024-01-31

### 🚀 Features
- **Visual Intelligence**: Integrated Qwen2-VL (via Fireworks AI) for unified layout analysis and OCR.
- **Frontend**:
    - Next.js 14 UI with Tailwind CSS and Shadcn/UI integration.
    - Interactive Document Visualizer with bounding box overlays.
    - Drag-and-drop file upload supporting PDF and Image formats.
- **Microservices Architecture**:
    - **Orchestrator**: Asyncio-based workflow engine managed by FastAPI.
    - **Preprocessing**: PDF-to-Image conversion and normalization pipeline.
    - **Visual Service**: Dedicated service for VLM inference and JSON parsing.

### 🐛 Bug Fixes
- Fixed "Image failed to load" race condition for multi-page PDF uploads.
- Resolved race conditions in concurrent page processing.
- Fixed TypeScript type errors in frontend components.

### 🛠 Improvements
- Establishing comprehensive CI pipeline (Linting + Build Checks).
- Standardized logging across all Python services.
- Consolidated repository structure (removed nested git).
- Added `ARCHITECTURE.md` with detailed Mermaid system diagrams.
