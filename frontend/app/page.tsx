'use client';

import React, { useState } from "react";
import { FileUpload } from "@/components/file-upload";
import { DocumentVisualizer } from "@/components/document-visualizer";
import { ResultsViewer } from "@/components/results-viewer";
import { AnalysisResponse } from "@/lib/types";
import { api } from "@/lib/api";
import { AlertCircle, FileText, Layout, Zap } from "lucide-react";
import { Toaster, toast } from 'sonner';
import { motion } from 'framer-motion';

export default function Home() {
  const [isUploading, setIsUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileType, setFileType] = useState<string>("");

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setAnalysisResult(null);
    setFileType(file.type);

    // Create preview
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post<AnalysisResponse>("/analyze", formData);
      setAnalysisResult(response.data);
      toast.success("Analysis Complete!");
    } catch (error) {
      toast.error("Analysis Failed. Please try again.");
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      <Toaster position="top-center" richColors />

      {/* Background Decor */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-blue-50/50 to-transparent" />
        <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-indigo-50/50 blur-3xl opacity-60" />
        <div className="absolute top-[20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-blue-50/50 blur-3xl opacity-60" />
      </div>

      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white/70 backdrop-blur-md border-b border-white/20 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 group cursor-pointer">
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-2 rounded-xl shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-300">
              <Layout className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-600">
              DocIntel <span className="text-blue-600 opacity-80">Pro</span>
            </span>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50/50 border border-blue-100/50 text-xs font-medium text-blue-700">
              <Zap className="w-3.5 h-3.5 fill-blue-700" />
              Powered by Fireworks AI
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12 space-y-12">

        {/* Helper Hero */}
        {!analysisResult && !isUploading && !previewUrl && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center space-y-6 max-w-3xl mx-auto py-12"
          >
            <h1 className="text-5xl font-extrabold tracking-tight text-slate-900 leading-[1.15]">
              Transform Documents into <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600">Actionable Intelligence</span>
            </h1>
            <p className="text-lg text-slate-500 leading-relaxed max-w-2xl mx-auto">
              Advanced layout analysis, OCR, and semantic understanding driven by Qwen2-VL.
              Structure your unstructured data with pixel-perfect precision.
            </p>
          </motion.div>
        )}

        {/* Upload Section */}
        <section className="relative">
          <FileUpload onUpload={handleUpload} isUploading={isUploading} />
        </section>

        {/* Results Section */}
        {(previewUrl || analysisResult) && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[75vh] min-h-[600px]"
          >

            {/* Visualizer Panel */}
            <div className="h-full rounded-2xl overflow-hidden ring-1 ring-slate-200 shadow-xl shadow-slate-200/50 relative">
              {previewUrl && (fileType !== 'application/pdf' || analysisResult) ? (
                <DocumentVisualizer
                  imageUrl={previewUrl}
                  elements={analysisResult?.document.visual_elements || []}
                  pages={analysisResult?.document.pages}
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center bg-slate-50/50 text-slate-400 gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <FileText className="w-4 h-4 text-slate-400" />
                    </div>
                  </div>
                  <p className="font-medium animate-pulse">Processing Document...</p>
                </div>
              )}
            </div>

            {/* Data Panel */}
            <div className="h-full rounded-2xl overflow-hidden ring-1 ring-slate-200 shadow-xl shadow-slate-200/50">
              {analysisResult ? (
                <ResultsViewer data={analysisResult} />
              ) : (
                <div className="h-full bg-white flex items-center justify-center p-8">
                  <div className="text-center space-y-3 opacity-30">
                    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto">
                      <FileText className="w-8 h-8 text-slate-400" />
                    </div>
                    <p className="text-sm font-medium text-slate-500">Analysis results appearing soon...</p>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </main>

      {/* Footer */}
      {(analysisResult || previewUrl) && (
        <footer className="py-8 text-center text-sm text-slate-400 border-t border-slate-200/50 bg-white/30">
          <p>© 2026 DocIntel Pro. All rights reserved.</p>
        </footer>
      )}
    </div>
  );
}
