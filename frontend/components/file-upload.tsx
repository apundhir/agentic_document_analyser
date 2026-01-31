'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';

interface FileUploadProps {
    onUpload: (file: File) => void;
    isUploading: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUpload, isUploading }) => {
    const [uploadError, setUploadError] = useState<string | null>(null);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        setUploadError(null);
        if (acceptedFiles?.length > 0) {
            const file = acceptedFiles[0];
            // Basic client-side check
            if (file.type.startsWith('image/') || file.type === 'application/pdf') {
                onUpload(file);
            } else {
                setUploadError('Only text, image, or PDF files are currently supported.');
            }
        }
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
            'application/pdf': ['.pdf']
        },
        maxFiles: 1,
        disabled: isUploading
    });

    return (
        <div className="w-full max-w-2xl mx-auto">
            {/* @ts-expect-error - Framer Motion and Dropzone type mismatch for event handlers */}
            <motion.div
                {...getRootProps()}
                initial={{ scale: 0.98, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                whileHover={{ scale: 1.01 }}
                className={cn(
                    "relative border-2 border-dashed rounded-2xl p-10 transition-all duration-300 ease-out flex flex-col items-center justify-center gap-6 cursor-pointer overflow-hidden group",
                    isDragActive
                        ? "border-blue-500 bg-blue-50/50 shadow-xl shadow-blue-100"
                        : "border-slate-200 hover:border-blue-400 hover:bg-slate-50 hover:shadow-lg hover:shadow-slate-100",
                    isUploading && "opacity-80 cursor-wait pointer-events-none border-slate-200"
                )}
            >
                <input {...getInputProps()} />

                {/* Animated Background Gradient */}
                <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />

                <AnimatePresence mode="wait">
                    {!isUploading ? (
                        <motion.div
                            key="idle"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex flex-col items-center gap-4 relative z-10"
                        >
                            <div className={cn(
                                "p-5 rounded-full shadow-sm transition-colors duration-300",
                                isDragActive ? "bg-blue-100 text-blue-600" : "bg-white text-slate-400 group-hover:text-blue-500 group-hover:scale-110"
                            )}>
                                <Upload className="w-8 h-8" />
                            </div>

                            <div className="text-center space-y-1">
                                <p className="text-lg font-semibold text-slate-700">
                                    {isDragActive ? "Drop your file anywhere" : "Click to upload or drag & drop"}
                                </p>
                                <p className="text-sm text-slate-500">
                                    Detect layouts, extract text, and analyze structure instantly.
                                </p>
                            </div>

                            <div className="flex gap-2 mt-2">
                                {['PDF', 'PNG', 'JPG', 'WEBP'].map(ext => (
                                    <span key={ext} className="text-[10px] font-bold px-2 py-1 bg-slate-100 text-slate-500 rounded-md border border-slate-200 uppercase tracking-widest">{ext}</span>
                                ))}
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="uploading"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="w-full max-w-sm flex flex-col items-center gap-6 relative z-10"
                        >
                            <div className="relative">
                                <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 animate-pulse rounded-full" />
                                <Loader2 className="w-12 h-12 text-blue-600 animate-spin relative z-10" />
                            </div>

                            <div className="w-full space-y-2 text-center">
                                <h3 className="text-lg font-semibold text-slate-800 animate-pulse">Deep Analysis in Progress</h3>
                                <p className="text-xs text-slate-500">Running LayoutLMv3 & Qwen-VL... (~15s)</p>
                                <Progress value={undefined} className="h-2 w-full bg-slate-100" />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>

            <AnimatePresence>
                {uploadError && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, height: 0 }}
                        animate={{ opacity: 1, y: 0, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4"
                    >
                        <div className="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 shadow-sm">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            <p className="text-sm font-medium">{uploadError}</p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
