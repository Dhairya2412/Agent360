"use client";

import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui/toaster";
import type { Document } from "@/lib/types";

interface DocumentTableProps {
  documents: Document[];
  onDelete: () => void;
}

export function DocumentTable({ documents, onDelete }: DocumentTableProps) {
  const { toast } = useToast();

  const handleDelete = async (id: string) => {
    try {
      await api.deleteDocument(id);
      toast({ title: "Deleted", description: "Document removed from knowledge base" });
      onDelete();
    } catch (err) {
      toast({ title: "Error", description: String(err), variant: "destructive" });
    }
  };

  if (documents.length === 0) {
    return (
      <div className="rounded-xl border border-border p-12 text-center text-muted-foreground">
        <p>No documents uploaded yet</p>
        <p className="mt-1 text-sm">Upload SOPs, policies, or catalogs to enhance RAG retrieval</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-secondary/50">
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Filename</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Type</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Chunks</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Size</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Uploaded</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} className="border-b border-border/50 hover:bg-secondary/30">
              <td className="px-4 py-3 font-medium">{doc.filename}</td>
              <td className="px-4 py-3 uppercase text-xs">{doc.file_type}</td>
              <td className="px-4 py-3">{doc.chunk_count}</td>
              <td className="px-4 py-3">{(doc.size_bytes / 1024).toFixed(1)} KB</td>
              <td className="px-4 py-3">
                <Badge variant="success">{doc.status}</Badge>
              </td>
              <td className="px-4 py-3 text-xs text-muted-foreground">{formatDate(doc.created_at)}</td>
              <td className="px-4 py-3">
                <Button size="sm" variant="ghost" onClick={() => handleDelete(doc.id)}>
                  <Trash2 className="h-4 w-4 text-red-400" />
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
