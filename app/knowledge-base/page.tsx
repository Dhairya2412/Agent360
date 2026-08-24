"use client";

import { useEffect, useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { FileUploader } from "@/components/knowledge/FileUploader";
import { DocumentTable } from "@/components/knowledge/DocumentTable";
import { ErrorState } from "@/components/ui/error-state";
import { api } from "@/lib/api";
import type { Document } from "@/lib/types";

export default function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    api.listDocuments()
      .then(setDocuments)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load documents"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <>
      <Topbar title="Knowledge Base" subtitle="Upload and manage RAG documents for agent retrieval" />
      <div className="space-y-6 p-8">
        <FileUploader onUploaded={load} />
        {loading ? (
          <p className="text-muted-foreground">Loading documents...</p>
        ) : error ? (
          <ErrorState message={error} onRetry={load} />
        ) : (
          <DocumentTable documents={documents} onDelete={load} />
        )}
      </div>
    </>
  );
}
