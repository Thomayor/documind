# DocuMind — Questions & Réponses de révision

---

## Étape 1 — Setup projet

**Q : Quelle est la différence entre `dependencies` et `dev-dependencies` dans `pyproject.toml` ?**

R : Les `dependencies` sont installées en production (elles tournent dans l'image Docker de prod). Les `dev-dependencies` (pytest, ruff, black...) ne sont jamais installées en prod — l'image est plus légère et on n'expose pas des outils de debug en production.

---

## Étape 2 — Docker

**Q : Qu'est-ce qu'un build multi-stage Docker, et quel problème ça résout ?**

R : C'est une seule image finale construite en plusieurs étapes dans le même Dockerfile. Chaque `FROM` démarre un nouveau stage. On peut copier uniquement certains fichiers d'un stage vers le suivant — tout le reste est jeté. Résultat : l'image de prod ne contient pas les outils de build (gcc, uv, headers de compilation), elle est donc plus légère et moins exposée aux attaques.

---

## Étape 3 — Pydantic Settings

**Q : Pourquoi utiliser `BaseSettings` de Pydantic plutôt que `os.environ.get("DATABASE_URL")` ?**

R : Trois raisons :
1. **Fail-fast** : si une variable obligatoire manque, l'app refuse de démarrer immédiatement avec un message clair. Avec `os.environ`, on obtient `None` qui se propage silencieusement jusqu'à un crash incompréhensible.
2. **Typage automatique** : on déclare `DEBUG: bool` et Pydantic convertit la string `"true"` en `True` automatiquement.
3. **Ordre de priorité** : `BaseSettings` cherche d'abord dans les variables d'environnement, ensuite dans le fichier `.env`. Un seul endroit pour tout configurer.

Le vrai gain c'est le **fail-fast** — le typage est le bonus.

---

## Étape 4 — Base de données + Alembic

**Q : Quelle est la différence entre SQLAlchemy ORM et SQLAlchemy Core ?**

R : SQLAlchemy Core est le bas niveau — on écrit du SQL sous forme Python (`select(table).where(...)`), on manipule des tables et des colonnes. SQLAlchemy ORM est au-dessus du Core — on définit des classes Python qui représentent les tables (`class Document(Base)`), et SQLAlchemy fait la traduction SQL. On manipule des objets Python, pas du SQL brut.

**Q : Pourquoi Alembic plutôt que `Base.metadata.create_all()` ?**

R : `create_all()` crée les tables si elles n'existent pas, mais ne fait rien si elles existent déjà. Si on modifie un modèle (ajouter une colonne), il faut dropper et recréer la base manuellement. Alembic génère des scripts de migration versionnés avec un `upgrade()` et un `downgrade()` — on peut faire évoluer la base en production sans perdre les données, et revenir en arrière si besoin.

**Q : Quelle est la différence entre les index HNSW et IVFFlat dans pgvector ?**

R :
- **IVFFlat** : divise les vecteurs en clusters avec des centroïdes. Simple, léger en mémoire, rapide à construire. Moins précis si les données changent souvent (les clusters deviennent périmés).
- **HNSW** : construit un graphe multi-niveaux où chaque vecteur est connecté à ses voisins proches. Plus rapide à la recherche, plus précis, mais consomme plus de mémoire et plus long à construire.

Pour DocuMind on utilise **HNSW** : les données sont dynamiques (insertions fréquentes) et la précision impacte directement la qualité des réponses RAG.

---

## Étape 5 — Modèles SQLAlchemy

**Concepts clés :**

- **UUID comme clé primaire** : généré côté application (pas côté base), donc on connaît l'ID avant l'insertion. Utile pour orchestrer plusieurs opérations.
- **Colonne `Vector(768)`** : type pgvector — PostgreSQL stocke le vecteur nativement et peut faire des recherches de similarité avec l'opérateur `<=>`. 768 = taille de sortie du modèle `intfloat/multilingual-e5-base`.
- **`cascade="all, delete-orphan"`** : si on supprime un `Document`, tous ses `Chunk` sont supprimés automatiquement (cohérent avec `ondelete="CASCADE"` en base).
- **`ondelete="SET NULL"` sur QueryHistory** : si on supprime un document, l'historique des questions posées dessus est conservé mais sans référence au document — on ne perd pas l'historique.
- **Séparation ORM / base** : les relations SQLAlchemy (`relationship`) sont des abstractions Python. Le `CASCADE` en base et le `cascade` ORM sont deux choses distinctes — l'un agit au niveau SQL, l'autre au niveau session Python.

---

## Étape 6 — Schémas Pydantic

**Q : Pourquoi créer des schémas Pydantic séparés des modèles SQLAlchemy ?**

R : Le modèle SQLAlchemy représente une ligne en base de données — il contient tout, y compris des choses à ne jamais exposer (mots de passe, clés internes, relations qui déclenchent des requêtes SQL supplémentaires à la sérialisation). Le schéma Pydantic représente ce que l'API accepte ou retourne — on choisit exactement quels champs exposer. Un même modèle ORM peut avoir plusieurs schémas : `DocumentCreate` (ce que le client envoie), `DocumentOut` (ce que l'API retourne).

Sans cette séparation : une modification de la table casse l'interface de l'API. Avec : les deux évoluent indépendamment. C'est le **DTO pattern** (Data Transfer Object).

---

## Étape 9 — Chunker

**Q : Qu'est-ce que l'overlap dans le chunking et pourquoi c'est important pour le RAG ?**

R : Sans overlap, un texte est découpé en blocs disjoints. Une phrase qui chevauche la frontière entre deux chunks est coupée en deux — aucun chunk ne la contient entière. Si la réponse à une question est dans cette phrase, le RAG la rate.

Avec overlap, chaque chunk reprend N caractères du chunk précédent. Les phrases en bordure apparaissent dans deux chunks — le contexte n'est jamais perdu à la frontière.

Trade-off : plus d'overlap = meilleure couverture, mais plus de chunks stockés et plus de tokens envoyés au LLM.

```
Sans overlap :  [0-500] [500-1000] [1000-1500]
Avec overlap :  [0-500] [450-950]  [900-1400]
```

---

## Étape 8 — Parsers

**Q : Qu'est-ce qu'une classe abstraite (ABC) et pourquoi l'utiliser pour `BaseParser` ?**

R : Une ABC force les sous-classes à implémenter certaines méthodes. Si `PDFParser` n'implémente pas `parse()`, Python lève une erreur à l'instanciation — pas au moment de l'appel. C'est un contrat garanti à la construction. Avec une classe normale, on pourrait instancier `BaseParser` directement par erreur, ou oublier `parse()` et le découvrir seulement au runtime.

**Q : Le Repository est-il un singleton ?**

R : Non. Il est instancié à chaque requête HTTP avec la session de base de données de cette requête. Une session SQLAlchemy n'est pas thread-safe — elle ne doit pas être partagée entre requêtes. Quand la requête se termine, la session est fermée et le Repository est garbage collecté.

---

## Étape 7 — Repository pattern

**Q : Pourquoi une couche Repository plutôt que des requêtes SQLAlchemy directement dans les routes ?**

R : Sans Repository, une route fait 3 choses à la fois : valider la requête HTTP, requêter la base, formater la réponse. C'est illisible et impossible à tester sans base de données.

Le Repository est une abstraction entre la logique métier et la base. Les routes ne savent pas comment les données sont stockées — elles appellent juste `repository.get(id)`. Pour tester la logique métier, on remplace le Repository par un mock : zéro base de données, tests rapides.

```
Route FastAPI → Service (logique métier) → Repository (accès DB) → PostgreSQL
```

Si on change de base de données, on ne réécrit que les Repositories — pas les routes, pas les services.

---

## Étape 11-12 — Embedder + Similarity Search

**Q : Quelle est la différence entre MiniLM et Qwen2.5 dans le pipeline RAG ?**

R : Ce sont deux modèles avec des rôles opposés.

**MiniLM** (`paraphrase-multilingual-MiniLM-L12-v2`) est un **encodeur** — il transforme du texte en vecteur de 384 nombres. Il ne génère aucun texte. Son seul rôle est de produire des représentations numériques pour comparer des textes sémantiquement.

**Qwen2.5-1.5B-Instruct** est un **LLM génératif** — il prend un prompt en entrée et génère du texte token par token. C'est lui qui rédige la réponse à la question.

Le pipeline RAG complet utilise les deux :

```
Question utilisateur
       │
       ▼
   [MiniLM]   ← encode la question en vecteur
       │
       ▼
  [pgvector]  ← trouve les 5 chunks les plus proches (similarity search)
       │
       ▼
  [Qwen2.5]   ← reçoit "question + chunks" et génère une réponse en langage naturel
       │
       ▼
  Réponse + sources (numéros de page)
```

MiniLM = **trouver** les bons passages dans la base vectorielle.
Qwen2.5 = **répondre** en lisant ces passages.

---

**Q : Pourquoi trier les résultats de similarity search par ASC et non DESC ?**

R : La distance cosinus mesure une **différence** entre deux vecteurs :
- `0` → vecteurs identiques → très similaire
- `1` → vecteurs orthogonaux → sans relation
- `2` → vecteurs opposés

On veut les chunks les **plus similaires**, donc les distances les **plus petites**. `ORDER BY distance ASC` met les plus proches en premier. En DESC, on obtiendrait les chunks les moins pertinents.

---

## Étape 13-14 — Générateur LLM + Service Q&A

**Q : Quelle est la différence entre un modèle `base` et un modèle `Instruct` sur HuggingFace ?**

R : Un modèle **base** est entraîné uniquement à prédire le prochain token — il complète du texte. Si on lui donne "La capitale de la France est", il continue avec "Paris, une ville...". Il ne répond pas à des questions, il complète.

Un modèle **Instruct** est le même modèle base, affiné avec du RLHF et du fine-tuning sur des instructions. On lui a montré des milliers d'exemples du format `[USER] question / [ASSISTANT] réponse`. Résultat : il suit les instructions, reste dans le sujet, arrête de générer au bon moment.

Pour DocuMind on a besoin que le modèle suive l'instruction "réponds uniquement à partir du contexte fourni" — un modèle base ignorerait cette instruction.

**Q : Pourquoi le pipeline RAG est-il synchrone et bloquant sur CPU ?**

R : Qwen2.5 tourne sur CPU (pas de GPU disponible en Docker). La génération de 200 tokens prend ~60-90 secondes car le CPU doit calculer les matrices de chaque couche du réseau séquentiellement. Uvicorn est bloqué pendant ce temps — aucune autre requête ne passe. En production, on utiliserait un GPU (x100 plus rapide) ou un service d'inférence dédié (vLLM, Ollama) dans un processus séparé.

---

## Étape 16 — Historique avec pagination

**Q : Quelle est la différence entre la pagination `limit/offset` et la pagination par curseur ?**

R :
- **`limit/offset`** : "saute N entrées, donne-moi les M suivantes". Simple, mais si une nouvelle entrée est insérée pendant la pagination, les pages se décalent — doublons ou entrées manquées possibles.
- **Cursor-based** : on passe l'ID de la dernière entrée vue. Le serveur retourne "tout ce qui vient après cet ID". Stable car l'ID ne change pas, même avec des insertions concurrentes. Utilisé par Twitter, Instagram pour le scroll infini.

Pour DocuMind, `limit/offset` suffit — l'historique n'est pas modifié pendant la consultation.

---

## Étapes 17-18 — Tests unitaires et intégration

**Q : Pourquoi mocker les repositories dans les tests unitaires ?**

R : Un test unitaire teste une seule chose en isolation. Si le test de `QAService.ask()` fait une vraie requête PostgreSQL, on teste en fait QAService + ChunkRepository + la connexion DB + les migrations. Quand ça casse, on ne sait pas où. Le mock remplace le Repository par un objet qui retourne des données prédéfinies — le test ne teste que la logique de `QAService`, rien d'autre.

```python
# Le mock dit : "quand on appelle similarity_search, renvoie ces chunks"
mock_chunk_repo.similarity_search.return_value = [(fake_chunk, 0.2)]
```

**Q : Pourquoi a-t-on une base de données séparée pour les tests ?**

R : Les tests d'intégration insèrent et suppriment des données réelles. Si on utilisait la base de dev, les tests pourraient corrompre des données en cours d'utilisation, et les données de dev parasiteraient les assertions des tests. La base de test est créée vide avant chaque session, peuplée par les fixtures, puis nettoyée — chaque run repart d'un état propre.

**Q : Qu'est-ce que `app.dependency_overrides` dans FastAPI ?**

R : C'est le mécanisme de FastAPI pour remplacer une dépendance (comme `get_db`) par une autre dans les tests. Sans ça, chaque test ferait des requêtes sur la base de prod. Avec `dependency_overrides`, on dit "pour ce test, quand FastAPI demande `get_db`, donne-lui `get_test_db` à la place". Ça s'active/désactive sans modifier le code de production.

---

## Étape 19 — Logging, Middleware, Exceptions

**Q : Quelle est la différence entre un Middleware et un Exception Handler dans FastAPI ?**

R :
- **Middleware** : enveloppe toutes les requêtes, même celles qui réussissent. S'exécute avant et après chaque handler. Notre `LoggingMiddleware` mesure la durée et log `METHOD PATH STATUS DURATIONms` pour chaque requête.
- **Exception Handler** : s'active uniquement quand une exception non gérée remonte. Notre `unhandled_exception_handler` intercepte tout ce qui échappe aux routes et retourne `{"detail": "Erreur interne"}` proprement au lieu d'un crash 500 brut.

Analogie : le Middleware est un douanier qui contrôle tout le monde à l'entrée et à la sortie. L'Exception Handler est l'équipe d'urgence qui intervient seulement quand quelque chose explose.

---

## Étapes 23-24 — CI/CD GitHub Actions

### CI (Continuous Integration)

**Q : Qu'est-ce que la CI et pourquoi ça tourne sur chaque PR ?**

R : La CI est un pipeline automatisé qui vérifie qu'un changement de code ne casse rien. Elle s'exécute à chaque push ou PR sur un runner GitHub (une VM Ubuntu éphémère). Si elle échoue, le merge est bloqué. On ne merge jamais du code qui casse les tests.

**Q : Pourquoi séparer lint, test et build en 3 jobs distincts ?**

R : Deux raisons :
1. **Feedback rapide** : si le lint échoue (style, imports manquants), on le sait en 10 secondes sans attendre les tests qui prennent 3 minutes.
2. **Parallélisme** : des jobs indépendants tournent en parallèle sur des runners séparés. `build` dépend de `test` (`needs: test`), mais si on avait des jobs vraiment indépendants ils tourneraient simultanément.

**Q : Comment la CI fait-elle tourner PostgreSQL ?**

R : Via les `services` GitHub Actions. GitHub lance un conteneur `pgvector/pgvector:pg16` en parallèle du job, avec un healthcheck. Le job attend que le conteneur soit `healthy` avant de démarrer. C'est un vrai PostgreSQL, pas un mock — les tests d'intégration tournent sur une vraie base.

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    options: --health-cmd pg_isready  # attend que PG soit prêt
```

### CD (Continuous Deployment)

**Q : Pourquoi tagger l'image Docker avec le SHA Git et pas `latest` ?**

R : `latest` est écrasé à chaque push — impossible de savoir quelle version tourne en prod. Le SHA Git (`a3f9c12`) est unique et traçable : on peut faire `git show a3f9c12` pour voir exactement quel code est dans l'image. En cas de bug, on rollback vers le SHA précédent en une commande. ArgoCD utilise ce tag pour détecter qu'une nouvelle image est disponible et déclencher un redéploiement.

**Q : Qu'est-ce que GHCR et pourquoi l'utiliser ?**

R : GitHub Container Registry — le registry Docker intégré à GitHub. Avantages : pas de compte Docker Hub, `GITHUB_TOKEN` suffit pour l'authentification (pas de secret supplémentaire), les images sont liées au repo (accès, visibilité, suppression gérés avec le repo).

**Q : Qu'est-ce que le principe GitOps que le CD implémente ?**

R : Dans le GitOps, le repo Git est la **source de vérité unique** pour l'état de l'infrastructure. Au lieu de déployer directement sur le cluster (`kubectl apply`), le CD commit le nouveau tag d'image dans `k8s/documind/values.yaml`. ArgoCD surveille ce fichier et applique le changement automatiquement. Avantages : tout déploiement est auditable via `git log`, on peut rollback avec `git revert`, l'état du cluster est toujours en sync avec le repo.

```
Code merge → CI passe → CD build image → CD commit tag → ArgoCD détecte → Redéploiement auto
```
