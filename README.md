# DocuMind

Plateforme RAG (Retrieval-Augmented Generation) pour interroger vos documents avec un LLM tournant entièrement en local — sans envoyer vos données à un service tiers.

Importez un PDF, un DOCX ou un TXT. Posez une question en langage naturel. Le système retrouve les passages pertinents et génère une réponse ancrée dans votre document, avec les sources et numéros de page.

---

## Pourquoi ce projet ?

Les solutions SaaS (ChatGPT, Claude, etc.) nécessitent d'envoyer vos documents sur des serveurs externes. DocuMind fait tourner l'intégralité du pipeline en local :

- **Embeddings** : [intfloat/multilingual-e5-base](https://huggingface.co/intfloat/multilingual-e5-base) via `sentence-transformers`
- **Génération** : [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) via `transformers`
- **Recherche vectorielle** : PostgreSQL + pgvector (cosine distance, index HNSW)

Vos données ne quittent jamais votre machine.

---

## Stack technique

| Couche | Technologie | Pourquoi |
|--------|-------------|----------|
| **API** | FastAPI + Python 3.11 | Async natif, validation Pydantic, OpenAPI auto-généré |
| **Base de données** | PostgreSQL 16 + pgvector | Stockage relationnel + recherche vectorielle dans une seule DB |
| **Embeddings** | MiniLM / multilingual-e5 | Modèle léger (120M params), multilingue, rapide sur CPU |
| **LLM** | Qwen2.5-1.5B-Instruct | Modèle open-source instruction-tuned, tourne sur CPU |
| **ORM** | SQLAlchemy 2.0 + Alembic | Repository pattern, migrations versionnées |
| **Frontend** | Next.js 16 + Tailwind v4 | App Router, dark theme, composants React 19 |
| **Infra** | Docker Compose | Reproductibilité locale, isolation des services |
| **CI** | GitHub Actions | Lint + tests + build à chaque PR |
| **CD** | GitHub Actions + GHCR | Build & push image Docker sur merge vers main |
| **Orchestration** | Kubernetes (k3d) + Helm | Déploiement déclaratif, rollback, scaling |
| **GitOps** | ArgoCD | Sync automatique repo Git → cluster |
| **Observabilité** | Prometheus + Grafana | Métriques golden signals, alertes latence/error rate |

---

## Architecture

```
documind/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Routes FastAPI (documents, qa, history)
│   │   ├── core/            # Config, logging, middleware, exceptions
│   │   ├── models/          # SQLAlchemy ORM (Document, Chunk, QueryHistory)
│   │   ├── schemas/         # Pydantic I/O (DTO pattern)
│   │   ├── repositories/    # Accès DB — seul endroit qui touche SQLAlchemy
│   │   ├── services/        # Logique métier (DocumentService, QAService)
│   │   ├── rag/             # Embedder, Generator, Chunker, PromptBuilder
│   │   └── parsers/         # PDF (PyMuPDF), TXT, DOCX
│   ├── alembic/             # Migrations
│   ├── tests/               # 24 tests (17 unitaires + 7 intégration)
│   └── Dockerfile
├── frontend/
│   ├── app/                 # Next.js App Router
│   └── components/          # UploadZone, DocumentList, ChatInterface
├── k8s/                     # Helm chart (à venir)
├── .github/workflows/       # CI/CD GitHub Actions
└── docker-compose.yml
```

## Pipeline RAG

```
Document (PDF/DOCX/TXT)
        │
        ▼
    Parser → texte brut par page
        │
        ▼
    Chunker → morceaux de ~1000 tokens avec overlap
        │
        ▼
    Embedder (MiniLM) → vecteurs 768 dimensions
        │
        ▼
    pgvector → stockage + index HNSW

Question utilisateur
        │
        ▼
    Embedder → vecteur requête
        │
        ▼
    Similarity search (cosine distance <0.5) → top 5 chunks
        │
        ▼
    PromptBuilder → contexte + question
        │
        ▼
    Qwen2.5 → réponse + sources
```

---

## Lancer le projet

### Prérequis

- Docker + Docker Compose
- Node.js 20+
- Modèles HuggingFace téléchargés localement (voir ci-dessous)

### 1. Télécharger les modèles

```bash
# Dans le dossier backend/models/
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-1.5B-Instruct', local_dir='backend/models/Qwen2.5')"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"
```

### 2. Configuration

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

### 3. Démarrer le backend

```bash
docker compose up -d
```

### 4. Démarrer le frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est disponible sur `http://localhost:3000`.

---

## Tests

```bash
docker compose exec backend pytest tests/ -v
```

24 tests : parsers, chunker, prompt builder (unitaires avec mocks), endpoints REST (intégration avec DB de test).

---

## État du projet

- [x] Phase 1 — Fondations (Docker, config, DB)
- [x] Phase 2 — Modèles et persistance
- [x] Phase 3 — Parsing et ingestion
- [x] Phase 4 — Pipeline RAG complet
- [x] Phase 5 — Résumé + historique
- [x] Phase 6 — Tests (24 tests)
- [x] Phase 7 — Frontend Next.js
- [x] Phase 8 — CI GitHub Actions
- [ ] Phase 9 — Kubernetes + Helm
- [ ] Phase 10 — GitOps ArgoCD
- [ ] Phase 11 — Prometheus + Grafana
