"use client";

import { useRef, useState } from "react";
import { Upload, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toaster";
import { api } from "@/lib/api";

interface FileUploaderProps {
  onUploaded: () => void;
}

export function FileUploader({ onUploaded }: FileUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      const result = await api.uploadDocument(file);
      toast({ title: "Uploaded", description: `${result.filename} — ${result.chunk_count} chunks indexed` });
      onUploaded();
    } catch (err) {
      toast({ title: "Upload failed", description: String(err), variant: "destructive" });
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div className="rounded-xl border border-dashed border-border p-8 text-center">
      <Upload className="mx-auto h-10 w-10 text-muted-foreground" />
      <p className="mt-4 font-medium">Upload Knowledge Documents</p>
      <p className="mt-1 text-sm text-muted-foreground">PDF, TXT, CSV, or Markdown — chunked and embedded into ChromaDB</p>
      <input ref={inputRef} type="file" className="hidden" accept=".pdf,.txt,.csv,.md" onChange={handleUpload} />
      <Button className="mt-4" onClick={() => inputRef.current?.click()} disabled={loading}>
        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
        Select File
      </Button>
    </div>
  );
}
