'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { VisualElement, Page } from '@/lib/types';

const getBorderColor = (type: string) => {
    switch (type?.toLowerCase()) {
        case 'table': return '#3b82f6'; // blue-500
        case 'figure':
        case 'image':
        case 'diagram': return '#10b981'; // green-500
        case 'title':
        case 'header': return '#8b5cf6'; // violet-500
        case 'text': return '#64748b'; // slate-500
        case 'list': return '#f59e0b'; // amber-500
        case 'footer': return '#94a3b8'; // slate-400
        default: return '#ef4444'; // red-500
    }
};

interface DocumentVisualizerProps {
    imageUrl: string;
    elements: VisualElement[];
    pages?: Page[];
}

export const DocumentVisualizer: React.FC<DocumentVisualizerProps> = ({ imageUrl, elements, pages }) => {
    const [imageLoaded, setImageLoaded] = useState(false);
    const imageRef = useRef<HTMLImageElement>(null);
    const [imgDims, setImgDims] = useState<{ width: number, height: number } | null>(null);
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1);

    // Determine current display data
    const totalPages = pages?.length || 1;
    const isMultiPage = totalPages > 1;

    // Get current image source
    // If pages are present and have base64, use that. Otherwise fallback to the input URL.
    const currentImgSrc = (pages && pages[currentPage - 1]?.base64_image) || imageUrl;

    // Filter elements for current page
    // Note: VisualElements in root might not have page numbers in legacy logic, 
    // but the blocks in Page[] definitely do. 
    // For this implementation, let's map the Page[i].blocks to visual elements for display 
    // OR filter the global visual_elements list if they have page tags.
    // The backend update added 'page_number' to visual_elements attributes.
    const currentElements = React.useMemo(() => {
        // Start with global visual elements for this page
        const vlmElements = elements ? elements.filter(el => {
            const elPage = el.attributes?.page_number || 1;
            return elPage === currentPage;
        }) : [];

        // Map OCR blocks from the current page to VisualElements
        const pageBlocks = pages?.[currentPage - 1]?.blocks?.map(block => ({
            type: block.block_type || 'text',
            confidence: 1.0,
            bounding_box: block.bounding_box,
            attributes: {
                text: block.text,
                page_number: currentPage
            }
        })) || [];

        // Combine both sources
        return [...vlmElements, ...pageBlocks];
    }, [elements, pages, currentPage]);

    return (
        <Card className="h-full flex flex-col overflow-hidden border-slate-200 shadow-xl bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-white/50 border-b border-slate-100 py-3 px-6">
                <div className="flex justify-between items-center">
                    <CardTitle className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span>Visual Intelligence</span>
                    </CardTitle>

                    <div className="flex items-center gap-4">
                        {isMultiPage && (
                            <div className="flex items-center gap-2 bg-slate-100/50 rounded-lg p-1">
                                <Button
                                    variant="ghost" size="icon" className="h-6 w-6"
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                >
                                    <ChevronLeft className="w-4 h-4" />
                                </Button>
                                <span className="text-xs font-mono font-medium w-16 text-center">
                                    {currentPage} / {totalPages}
                                </span>
                                <Button
                                    variant="ghost" size="icon" className="h-6 w-6"
                                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                >
                                    <ChevronRight className="w-4 h-4" />
                                </Button>
                            </div>
                        )}
                        <Badge variant="secondary" className="text-xs font-mono bg-slate-100 text-slate-600 border-slate-200">
                            {currentElements.length} BLOCKS
                        </Badge>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="p-0 flex-1 bg-slate-50/50 overflow-auto relative min-h-[600px] scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent text-center">
                <div className="relative inline-block h-fit w-fit p-8 shadow-sm m-4 bg-white rounded-lg transition-all duration-300">
                    {/* The Document Image */}
                    <img
                        src={currentImgSrc}
                        alt={`Document Analysis Page ${currentPage}`}
                        ref={imageRef}
                        onLoad={() => {
                            // console.log(`[DocumentVisualizer] Image loaded successfully for page ${currentPage}`);
                            if (imageRef.current) {
                                setImgDims({
                                    width: imageRef.current.naturalWidth,
                                    height: imageRef.current.naturalHeight
                                });
                                setImageLoaded(true);
                            }
                        }}
                        onError={(e) => {
                            console.error(`[DocumentVisualizer] Image failed to load for page ${currentPage}`);
                            // console.error("Error Event:", e);
                            setImageLoaded(false);
                        }}
                        className="max-w-full h-auto block select-none rounded-[2px]"
                    />

                    {/* Overlay Layer */}
                    {imageLoaded && imgDims && currentElements.map((el, idx) => {
                        const { x1, y1, x2, y2 } = el.bounding_box;
                        const imgWidth = imgDims.width;
                        const imgHeight = imgDims.height;

                        // Calculate Percentages
                        const leftPct = (x1 / imgWidth) * 100;
                        const topPct = (y1 / imgHeight) * 100;
                        const widthPct = ((x2 - x1) / imgWidth) * 100;
                        const heightPct = ((y2 - y1) / imgHeight) * 100;

                        const isHovered = hoveredIndex === idx;
                        const borderColor = getBorderColor(el.type);

                        return (
                            <motion.div
                                key={`${currentPage}-${idx}`} // Force re-render on page change
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ duration: 0.3, delay: idx * 0.01 }}
                                onMouseEnter={() => setHoveredIndex(idx)}
                                onMouseLeave={() => setHoveredIndex(null)}
                                className={cn(
                                    "absolute cursor-pointer rounded-[2px]",
                                    isHovered ? "z-50 shadow-2xl ring-2 ring-offset-1 ring-offset-white" : "z-10"
                                )}
                                style={{
                                    left: `${leftPct}%`,
                                    top: `${topPct}%`,
                                    width: `${widthPct}%`,
                                    height: `${heightPct}%`,
                                    backgroundColor: isHovered ? borderColor + '1A' : 'transparent',
                                    border: `1px solid ${borderColor}`,
                                    boxShadow: isHovered ? `0 0 0 1px ${borderColor}` : 'none'
                                }}
                            >
                                {/* Floating Label Tooltip */}
                                <AnimatePresence>
                                    {isHovered && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 4, scale: 0.9 }}
                                            animate={{ opacity: 1, y: -4, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                            className="absolute -top-8 left-0 px-2.5 py-1 text-[10px] font-bold text-white rounded-md uppercase tracking-wider shadow-lg flex items-center gap-1 backdrop-blur-md whitespace-nowrap z-50"
                                            style={{ backgroundColor: borderColor }}
                                        >
                                            {el.type}
                                            <span className="opacity-75 font-mono text-[9px] border-l border-white/20 pl-1 ml-1">
                                                {(el.confidence * 100).toFixed(0)}%
                                            </span>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
};
