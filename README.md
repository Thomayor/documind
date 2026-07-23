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
| **CI/CD** | GitHub Actions + GHCR | Lint + tests sur chaque PR, build & push image sur merge `main` |
| **Orchestration** | Kubernetes (k3d) + Helm | Déploiement déclaratif, rollback, scaling |
| **GitOps** | ArgoCD | Sync automatique repo Git → cluster, rollback déclaratif |
| **Observabilité** | Prometheus + Grafana | Métriques golden signals (latence p95, error rate), alertes |

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

## État du projet — 29 étapes

### Phase 1 — Fondations
- [x] Étape 1 — Setup projet · `pyproject.toml` · `uv` · structure des dossiers
- [x] Étape 2 — Docker · `docker-compose.yml` · PostgreSQL + pgvector · Dockerfile multi-stage
- [x] Étape 3 — Configuration · Pydantic `BaseSettings` · chargement `.env`
- [x] Étape 4 — Base de données · SQLAlchemy session · extension pgvector · migrations Alembic

### Phase 2 — Modèles et persistance
- [x] Étape 5 — Modèles SQLAlchemy · `Document`, `Chunk` (colonne vector), `QueryHistory`
- [x] Étape 6 — Schémas Pydantic · DTO pattern · séparation schemas API / models ORM
- [x] Étape 7 — Repository pattern · `BaseRepository` générique · `DocumentRepository` · `ChunkRepository`

### Phase 3 — Parsing et ingestion
- [x] Étape 8 — Parsers · `BaseParser` (ABC) · PDF (PyMuPDF) · TXT · DOCX
- [x] Étape 9 — Chunker · `RecursiveChunker` · overlap configurable
- [x] Étape 10 — Service ingestion · `DocumentService.ingest()` · route `POST /documents`

### Phase 4 — Pipeline RAG
- [x] Étape 11 — Embedder · Sentence Transformers · `multilingual-e5-base`
- [x] Étape 12 — Stockage vectoriel · `similarity_search()` · pgvector `<=>` · index HNSW
- [x] Étape 13 — Générateur LLM · HuggingFace · `Qwen2.5-1.5B-Instruct` · `PromptBuilder`
- [x] Étape 14 — Service Q&A · pipeline RAG complet · sources avec numéros de page

### Phase 5 — Features avancées
- [x] Étape 15 — Résumé automatique + extraction de concepts clés
- [x] Étape 16 — Historique des questions · pagination `limit/offset`

### Phase 6 — Qualité
- [x] Étape 17 — Tests unitaires · pytest · mocks · fixtures (17 tests)
- [x] Étape 18 — Tests d'intégration · `httpx.AsyncClient` · DB de test (7 tests)
- [x] Étape 19 — Logging structuré JSON · middleware FastAPI · gestion des erreurs

### Phase 7 — Frontend Next.js
- [x] Étape 20 — Setup Next.js 15 · Tailwind · shadcn/ui · connexion API
- [x] Étape 21 — UI Upload · drag & drop · liste des documents
- [x] Étape 22 — UI Chat RAG · interface conversationnelle · sources + numéros de page

### Phase 8 — CI/CD GitHub Actions
- [x] Étape 23 — Pipeline CI · lint (ruff/black) · pytest avec PostgreSQL service container · build Docker
- [ ] Étape 24 — Pipeline CD · push image GHCR · mise à jour automatique tag Helm

### Phase 9 — Kubernetes avec k3d
- [ ] Étape 25 — Cluster k3d local · manifestes K8s · Deployment · Service · Ingress · PVC
- [ ] Étape 26 — Helm chart · `values.yaml` · `helm install`

### Phase 10 — GitOps avec ArgoCD
- [ ] Étape 27 — Installation ArgoCD · `Application` CRD · sync policy
- [ ] Étape 28 — Workflow GitOps complet · CD → tag → ArgoCD sync → rollback

### Phase 11 — Observabilité
- [ ] Étape 29 — Prometheus · métriques FastAPI custom · dashboards Grafana · alertes
