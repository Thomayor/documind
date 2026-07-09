"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api, AskResponse, Document } from "@/lib/api";

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources?: AskResponse["sources"];
  sourceType?: string;
};

export default function ChatInterface() {
  const searchParams = useSearchParams();
  const docId = searchParams.get("doc") ?? undefined;

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [doc, setDoc] = useState<Document | null>(null);
  const [agentMode, setAgentMode] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const counter = useRef(0);

  useEffect(() => {
    if (!docId) return;
    api.listDocuments().then((docs) => {
      const found = docs.find((d) => d.id === docId);
      if (found) setDoc(found);
    });
  }, [docId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const q = input.trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { id: ++counter.current, role: "user", content: q }]);
    setInput("");
    setLoading(true);

    try {
      const res = agentMode
        ? await api.agentAsk(q, docId)
        : await api.ask(q, docId);

      setMessages((prev) => [
        ...prev,
        {
          id: ++counter.current,
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          sourceType: (res as any).source_type,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: ++counter.current, role: "assistant", content: "Erreur : impossible de contacter l'API." },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="shrink-0 px-6 py-4 border-b border-border flex items-center gap-3">
        <div className="flex-1 min-w-0">
          {doc ? (
            <>
              <p className="text-sm font-medium truncate">{doc.filename}</p>
              <p className="text-xs text-muted-foreground">Questions limitées à ce document</p>
            </>
          ) : (
            <>
              <p className="text-sm font-medium">Chat</p>
              <p className="text-xs text-muted-foreground">Questions sur tous les documents</p>
            </>
          )}
        </div>

        {/* Toggle agent mode */}
        <button
          onClick={() => setAgentMode((v) => !v)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
            agentMode
              ? "bg-primary/10 text-primary border-primary/20"
              : "bg-transparent text-muted-foreground border-border hover:text-foreground"
          }`}
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.2"/>
            <path d="M4 6h4M6 4v4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
          </svg>
          {agentMode ? "Agent (web fallback)" : "RAG seul"}
        </button>

        {doc && (
          <a href="/chat" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
            Tous les docs
          </a>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-accent flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M3 3h14v10H11L7.5 17V13H3V3Z" stroke="currentColor" strokeWidth="1.3" fill="none"/>
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Posez une question</p>
              <p className="text-xs text-muted-foreground mt-1">
                {agentMode
                  ? "L'agent cherche dans vos docs, puis sur le web si nécessaire"
                  : "Recherche uniquement dans vos documents"}
              </p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="w-7 h-7 rounded-lg bg-primary/20 flex items-center justify-center shrink-0 mt-0.5">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                  <path d="M2 2h9v7H7L4.5 12V9H2V2Z" stroke="currentColor" strokeWidth="1.2" fill="none" className="text-primary"/>
                </svg>
              </div>
            )}

            <div className={`max-w-[75%] space-y-2 flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div className={`px-4 py-3 rounded-xl text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground rounded-br-sm"
                  : "bg-card border border-border rounded-bl-sm"
              }`}>
                {msg.content}
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="space-y-1.5 w-full">
                  <div className="flex items-center gap-2 px-1">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Sources</p>
                    {msg.sourceType === "web" && (
                      <span className="text-[10px] font-medium text-amber-400 bg-amber-400/10 px-1.5 py-0.5 rounded">
                        Web
                      </span>
                    )}
                  </div>
                  {msg.sources.map((src, i) => (
                    <div key={i} className="flex gap-2 px-3 py-2 bg-accent/40 border border-border/50 rounded-lg">
                      {src.page_number && (
                        <span className="shrink-0 text-[10px] font-bold text-primary bg-primary/10 px-1.5 py-0.5 rounded self-start">
                          p.{src.page_number}
                        </span>
                      )}
                      {(src as any).url && (
                        <a
                          href={(src as any).url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="shrink-0 text-[10px] font-medium text-amber-400 hover:underline self-start truncate max-w-[120px]"
                        >
                          {new URL((src as any).url).hostname}
                        </a>
                      )}
                      <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                        {src.preview}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M2 2h9v7H7L4.5 12V9H2V2Z" stroke="currentColor" strokeWidth="1.2" fill="none"/>
              </svg>
            </div>
            <div className="px-4 py-3 bg-card border border-border rounded-xl rounded-bl-sm flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:0ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="shrink-0 px-6 py-4 border-t border-border">
        <div className="flex items-end gap-3 bg-card border border-border rounded-xl px-4 py-3 focus-within:border-primary/50 transition-colors">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder={agentMode ? "Question… l'agent cherche dans vos docs puis sur le web" : "Question sur vos documents…"}
            rows={1}
            className="flex-1 bg-transparent text-sm resize-none outline-none placeholder:text-muted-foreground max-h-32 leading-relaxed"
            style={{ fieldSizing: "content" } as React.CSSProperties}
          />
          <button
            onClick={send}
            disabled={!input.trim() || loading}
            className="shrink-0 w-8 h-8 rounded-lg bg-primary flex items-center justify-center disabled:opacity-40 hover:bg-primary/90 transition-all"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 11V3M7 3L4 6M7 3l3 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        <p className="text-[10px] text-muted-foreground mt-2 text-center">Shift+Entrée pour un saut de ligne</p>
      </div>
    </div>
  );
}
