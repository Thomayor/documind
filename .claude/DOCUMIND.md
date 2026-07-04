# DocuMind — Plateforme d'Intelligence Documentaire

Projet portfolio Python/IA/Data. Plateforme RAG permettant d'importer des documents hétérogènes et d'interagir avec eux via l'IA.

## Stack

**Backend** : Python 3.12, FastAPI, PostgreSQL, pgvector, SQLAlchemy, Alembic, Pydantic, HuggingFace, Sentence Transformers, PyMuPDF, Pytest  
**Frontend** : Next.js 15, TypeScript, Tailwind CSS, shadcn/ui  
**Infra** : Docker + docker-compose

## Agent disponible

- `/agents:mentor` → Guide étape par étape, questionne la compréhension, honnête

## Démarrage

```bash
# Lancer le projet complet
docker compose up -d

# Accéder à l'API
http://localhost:8000/docs

# Accéder au front
http://localhost:3000
```

## Plan — 29 étapes

| Phase | Étapes | Contenu |
|-------|--------|---------|
| 1 — Fondations | 1-4 | Setup, Docker, Config, Alembic |
| 2 — Persistance | 5-7 | Models, Schemas, Repositories |
| 3 — Ingestion | 8-10 | Parsers, Chunker, Upload API |
| 4 — RAG | 11-14 | Embedder, pgvector, LLM, Q&A |
| 5 — Features | 15-16 | Résumé, Historique |
| 6 — Qualité | 17-19 | Tests unitaires, intégration, Logging |
| 7 — Frontend | 20-22 | Next.js, Upload UI, Chat UI |
| 8 — CI/CD GitHub Actions | 23-24 | Pipeline CI (lint+test+build), CD (push image GHCR) |
| 9 — Kubernetes k3d | 25-26 | Manifestes K8s, Helm chart |
| 10 — GitOps ArgoCD | 27-28 | ArgoCD, workflow GitOps complet, rollback |
| 11 — Observabilité | 29 | Prometheus métriques, dashboards Grafana, alertes |
