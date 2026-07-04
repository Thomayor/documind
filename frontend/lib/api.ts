const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function fetchWithTimeout(url: string, options: RequestInit = {}, ms = 4000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  return fetch(url, { ...options, signal: controller.signal }).finally(() => clearTimeout(id));
}

export type Document = {
  id: string;
  filename: string;
  content_type: string;
  created_at: string;
};

export type Source = {
  page_number: number | null;
  preview: string;
};

export type AskResponse = {
  answer: string;
  sources: Source[];
};

export type HistoryEntry = {
  id: string;
  question: string;
  answer: string;
  document_id: string | null;
  created_at: string;
};

export const api = {
  async listDocuments(): Promise<Document[]> {
    const r = await fetchWithTimeout(`${API_URL}/api/v1/documents/`);
    if (!r.ok) throw new Error("Erreur lors du chargement des documents");
    return r.json();
  },

  async uploadDocument(file: File): Promise<Document> {
    const form = new FormData();
    form.append("file", file);
    const r = await fetch(`${API_URL}/api/v1/documents/`, {
      method: "POST",
      body: form,
    });
    if (!r.ok) throw new Error("Erreur lors de l'upload");
    return r.json();
  },

  async deleteDocument(id: string): Promise<void> {
    const r = await fetch(`${API_URL}/api/v1/documents/${id}`, {
      method: "DELETE",
    });
    if (!r.ok) throw new Error("Erreur lors de la suppression");
  },

  async ask(question: string, document_id?: string): Promise<AskResponse> {
    const r = await fetch(`${API_URL}/api/v1/qa/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, document_id }),
    });
    if (!r.ok) throw new Error("Erreur lors de la question");
    return r.json();
  },

  async listHistory(skip = 0, limit = 20): Promise<HistoryEntry[]> {
    const r = await fetch(`${API_URL}/api/v1/history/?skip=${skip}&limit=${limit}`);
    if (!r.ok) throw new Error("Erreur lors du chargement de l'historique");
    return r.json();
  },
};
