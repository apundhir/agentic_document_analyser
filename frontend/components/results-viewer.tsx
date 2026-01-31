'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText, Code, Table } from 'lucide-react';

import { AnalysisResponse, Table as TableData } from '@/lib/types';

interface ResultsViewerProps {
    data: AnalysisResponse | null;
}

export const ResultsViewer: React.FC<ResultsViewerProps> = ({ data }) => {
    if (!data) return null;

    const fullText = data.document?.text || "No text extracted.";
    const tables = data.document?.tables || [];

    return (
        <Card className="h-full flex flex-col border-slate-200 shadow-lg">
            <CardHeader className="bg-slate-50 border-b border-slate-100 py-4">
                <CardTitle className="text-sm font-medium text-slate-700">Analysis Results</CardTitle>
            </CardHeader>
            <CardContent className="p-0 flex-1 overflow-hidden">
                <Tabs defaultValue="text" className="h-full flex flex-col">
                    <div className="px-4 pt-4 border-b border-slate-100 bg-white">
                        <TabsList className="grid w-full grid-cols-3 mb-4">
                            <TabsTrigger value="text" className="flex items-center gap-2">
                                <FileText className="w-4 h-4" /> Text
                            </TabsTrigger>
                            <TabsTrigger value="json" className="flex items-center gap-2">
                                <Code className="w-4 h-4" /> JSON
                            </TabsTrigger>
                            <TabsTrigger value="tables" className="flex items-center gap-2" disabled={tables.length === 0}>
                                <Table className="w-4 h-4" /> Tables ({tables.length})
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    <div className="flex-1 overflow-auto bg-slate-50/50 p-4">
                        <TabsContent value="text" className="m-0 h-full">
                            <ScrollArea className="h-full rounded-md border bg-white p-6 shadow-sm">
                                <div className="prose prose-sm max-w-none text-slate-700 whitespace-pre-wrap font-mono text-xs leading-relaxed">
                                    {fullText}
                                </div>
                            </ScrollArea>
                        </TabsContent>

                        <TabsContent value="json" className="m-0 h-full">
                            <ScrollArea className="h-full rounded-md border bg-slate-900 p-6 shadow-sm">
                                <pre className="text-xs text-blue-300 font-mono">
                                    {JSON.stringify(data, null, 2)}
                                </pre>
                            </ScrollArea>
                        </TabsContent>

                        <TabsContent value="tables" className="m-0 h-full space-y-4">
                            {tables.map((table: TableData, idx: number) => (
                                <Card key={idx} className="border border-slate-200 overflow-hidden">
                                    <CardHeader className="bg-slate-100 py-2 px-4">
                                        <CardTitle className="text-xs font-semibold text-slate-600">Table {idx + 1}</CardTitle>
                                    </CardHeader>
                                    <CardContent className="p-0 overflow-auto">
                                        {/* Simple Table Rendering logic could go here, for now raw dump */}
                                        <pre className="text-xs p-4 bg-white text-slate-600">
                                            {JSON.stringify(table, null, 2)}
                                        </pre>
                                    </CardContent>
                                </Card>
                            ))}
                        </TabsContent>
                    </div>
                </Tabs>
            </CardContent>
        </Card>
    );
};
