from typing import Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from duckduckgo_search import DDGS

from app.rag.embedder import embedder
from app.rag.generator import generator, prompt_builder
from app.repositories.document import ChunkRepository
from app.models.document import Chunk


class AgentState(TypedDict):
    question: str
    document_id: Optional[str]
    chunks: list[tuple[Chunk, float]]
    web_results: list[dict]
    answer: str
    sources: list[dict]
    source_type: str  # "document" | "web" | "none"


def retrieve_node(state: AgentState) -> AgentState:
    """Cherche dans les documents via pgvector."""
    # chunk_repo est injecté via le state — voir build_agent()
    repo: ChunkRepository = state["_chunk_repo"]
    query_vec = embedder.embed_query(state["question"])
    chunks = repo.similarity_search(query_vec, limit=5, max_distance=0.5)

    if state.get("document_id"):
        chunks = [(c, d) for c, d in chunks if str(c.document_id) == state["document_id"]]

    return {**state, "chunks": chunks}


def should_search_web(state: AgentState) -> str:
    """Décide si on a besoin du web."""
    if state["chunks"]:
        return "generate"
    return "web_search"


def web_search_node(state: AgentState) -> AgentState:
    """Cherche sur le web avec DuckDuckGo si les docs ne suffisent pas."""
    results = []
    try:
        with DDGS() as ddgs:
            hits = list(ddgs.text(state["question"], max_results=3))
            for h in hits:
                results.append({
                    "title": h.get("title", ""),
                    "body": h.get("body", ""),
                    "href": h.get("href", ""),
                })
    except Exception:
        pass
    return {**state, "web_results": results}


def generate_node(state: AgentState) -> AgentState:
    """Génère la réponse depuis les chunks docs ou les résultats web."""
    if state["chunks"]:
        prompt = prompt_builder.build(state["question"], state["chunks"])
        answer = generator.generate(prompt)
        sources = [
            {"page_number": c.page_number, "preview": c.content[:150], "origin": "document"}
            for c, _ in state["chunks"]
        ]
        source_type = "document"
    elif state["web_results"]:
        context = "\n\n".join(
            f"[{r['title']}] {r['body']}" for r in state["web_results"]
        )
        prompt = (
            f"Tu es un assistant. Réponds à la question en te basant sur les résultats web suivants.\n\n"
            f"RÉSULTATS WEB :\n{context}\n\n"
            f"QUESTION : {state['question']}\n\nRÉPONSE :"
        )
        answer = generator.generate(prompt)
        sources = [
            {"page_number": None, "preview": r["body"][:150], "url": r["href"], "origin": "web"}
            for r in state["web_results"]
        ]
        source_type = "web"
    else:
        answer = "Je n'ai pas trouvé de réponse dans les documents ni sur le web."
        sources = []
        source_type = "none"

    return {**state, "answer": answer, "sources": sources, "source_type": source_type}


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("retrieve")
    graph.add_conditional_edges("retrieve", should_search_web, {
        "generate": "generate",
        "web_search": "web_search",
    })
    graph.add_edge("web_search", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


agent = build_agent()
