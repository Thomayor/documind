"use client";

import { useRef, useState } from "react";
import { api } from "@/lib/api";

type State = "idle" | "uploading" | "success" | "error";

export default function UploadZone() {
  const [state, setState] = useState<State>("idle");
  const [message, setMessage] = useState("");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function upload(file: File) {
    setState("uploading");
    setMessage(file.name);
    try {
      const doc = await api.uploadDocument(file);
      setState("success");
      setMessage(`"${doc.filename}" ingéré avec succès`);
      window.dispatchEvent(new Event("documind:refresh"));
      setTimeout(() => { setState("idle"); setMessage(""); }, 3000);
    } catch {
      setState("error");
      setMessage("Erreur — vérifiez le type de fichier (PDF, TXT, DOCX)");
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  }

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => state !== "uploading" && inputRef.current?.click()}
        className={`
          relative border border-dashed rounded-xl px-6 py-8 text-center cursor-pointer
          transition-all duration-150
          ${dragging
            ? "border-primary/70 bg-primary/5"
            : "border-border hover:border-primary/40 hover:bg-accent/30"
          }
          ${state === "uploading" ? "pointer-events-none" : ""}
        `}
      >
        {state === "uploading" ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
            <div>
              <p className="text-sm font-medium text-foreground">Ingestion en cours…</p>
              <p className="text-xs text-muted-foreground mt-0.5 truncate max-w-xs mx-auto">{message}</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 12V4M9 4L6 7M9 4l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 13v1a1 1 0 001 1h10a1 1 0 001-1v-1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </div>
            <div>
              <p className="text-sm text-foreground">
                Glissez un fichier ou{" "}
                <span className="text-primary font-medium">parcourez</span>
              </p>
              <p className="text-xs text-muted-foreground mt-1">PDF · TXT · DOCX</p>
            </div>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt,.docx"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) upload(f); }}
        />
      </div>

      {message && state !== "uploading" && (
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs ${
          state === "error"
            ? "bg-destructive/10 text-destructive"
            : "bg-green-500/10 text-green-400"
        }`}>
          {state === "success" ? (
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" strokeWidth="1.2"/>
              <path d="M4 6.5l2 2 3-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          ) : (
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" strokeWidth="1.2"/>
              <path d="M6.5 4v3M6.5 9v.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
          )}
          {message}
        </div>
      )}
    </div>
  );
}
