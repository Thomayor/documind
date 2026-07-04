"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Document } from "@/lib/api";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "2-digit", month: "short", year: "numeric",
  });
}

function extLabel(type: string) {
  if (type.includes("pdf")) return "PDF";
  if (type.includes("word") || type.includes("docx")) return "DOCX";
  return "TXT";
}

export default function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(false);
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    window.addEventListener("documind:refresh", load);
    return () => window.removeEventListener("documind:refresh", load);
  }, []);

  async function remove(id: string) {
    setDeleting(id);
    try {
      await api.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } finally {
      setDeleting(null);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {loading ? "Documents" : error ? "Documents" : `${documents.length} document${documents.length !== 1 ? "s" : ""}`}
        </span>
        {!loading && !error && (
          <button onClick={load} className="text-xs text-muted-foreground hover:text-foreground transition-colors">
            Actualiser
          </button>
        )}
      </div>

      {loading && (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-[58px] rounded-lg border border-border bg-card animate-pulse" />
          ))}
        </div>
      )}

      {error && (
        <div className="flex flex-col items-center justify-center py-10 text-center rounded-lg border border-dashed border-border">
          <p className="text-sm text-muted-foreground">Impossible de contacter l'API</p>
          <button onClick={load} className="mt-2 text-xs text-primary hover:underline">
            Réessayer
          </button>
        </div>
      )}

      {!loading && !error && documents.length === 0 && (
        <div className="flex flex-col items-center justify-center py-10 text-center rounded-lg border border-dashed border-border">
          <p className="text-sm font-medium text-foreground">Aucun document</p>
          <p className="text-xs text-muted-foreground mt-1">Importez un fichier pour commencer</p>
        </div>
      )}

      {!loading && !error && documents.length > 0 && (
        <div className="space-y-1.5">
          {documents.map((doc) => {
            const ext = extLabel(doc.content_type);
            const extColor =
              ext === "PDF" ? "text-rose-400 bg-rose-400/10" :
              ext === "DOCX" ? "text-blue-400 bg-blue-400/10" :
              "text-slate-400 bg-slate-400/10";

            return (
              <div
                key={doc.id}
                className="group flex items-center gap-3 px-4 py-3 rounded-lg border border-border bg-card hover:bg-accent/30 transition-colors"
              >
                <span className={`shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded ${extColor}`}>
                  {ext}
                </span>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{doc.filename}</p>
                  <p className="text-xs text-muted-foreground">{formatDate(doc.created_at)}</p>
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                  <Link
                    href={`/chat?doc=${doc.id}`}
                    className="px-2.5 py-1.5 rounded-md text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
                  >
                    Interroger
                  </Link>
                  <button
                    onClick={() => remove(doc.id)}
                    disabled={deleting === doc.id}
                    className="p-1.5 rounded-md text-muted-foreground hover:text-rose-400 hover:bg-rose-400/10 transition-colors"
                  >
                    {deleting === doc.id ? (
                      <div className="w-3.5 h-3.5 border border-current border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                        <path d="M2 3h9M5 3V2h3v1M4 3l.5 7.5h4L9 3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
