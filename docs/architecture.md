# Architecture Schema

Production-ready REST API with layered architecture: **Routes → Services → UoW → Repositories → MongoDB**

---

## System Architecture

```mermaid
graph TB
    subgraph Client["🌐 Client"]
        WebApp["Web/Mobile/CLI"]
    end

    subgraph API["📡 API Layer"]
        Routes["Routes<br/>/api/v1/*"]
        Auth["JWT + Rate Limiting"]
        Validation["Pydantic Schemas"]
    end

    subgraph Services["💼 Service Layer"]
        AuthSvc["AuthService"]
        SongsSvc["SongsService"]
        RatingsSvc["RatingsService"]
    end

    subgraph DataAccess["🗄️ Data Access"]
        UoW["UnitOfWork"]
        SongsRepo["SongsRepository"]
        RatingsRepo["RatingsRepository"]
        UsersRepo["UsersRepository"]
    end

    subgraph Infrastructure["⚙️ Infrastructure"]
        MongoDB[("MongoDB")]
        Redis[("Redis")]
    end

    WebApp --> Routes
    Routes --> Auth
    Auth --> Validation
    Validation --> AuthSvc
    Validation --> SongsSvc
    Validation --> RatingsSvc

    AuthSvc --> UoW
    SongsSvc --> UoW
    RatingsSvc --> UoW

    UoW --> SongsRepo
    UoW --> RatingsRepo
    UoW --> UsersRepo

    SongsRepo --> MongoDB
    RatingsRepo --> MongoDB
    UsersRepo --> MongoDB

    SongsRepo -.cache.-> Redis
    RatingsRepo -.cache.-> Redis
    Auth -.rate limit.-> Redis
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as Auth Routes
    participant Service as AuthService
    participant UoW as UnitOfWork
    participant Repo as UsersRepository
    participant DB as MongoDB

    Client->>API: POST /auth/login<br/>{username, password}
    API->>Service: login(username, password)
    Service->>UoW: __enter__()
    UoW->>Repo: get_by_username()
    Repo->>DB: query user
    DB-->>Repo: user doc
    Repo-->>Service: user
    Service->>Service: verify password
    Service-->>API: JWT token
    API-->>Client: 200 {access_token}
```

---

## Add Rating Flow (with Cache Invalidation)

```mermaid
sequenceDiagram
    participant Client
    participant API as Ratings Routes
    participant Service as RatingsService
    participant UoW as UnitOfWork
    participant SRepo as SongsRepository
    participant RRepo as RatingsRepository
    participant DB as MongoDB
    participant Cache as Redis

    Client->>API: POST /songs/ratings<br/>{song_id, rating}
    API->>Service: add_rating(song_id, rating)
    Service->>UoW: __enter__(use_transactions=True)
    UoW->>SRepo: get_by_id(song_id)
    SRepo->>DB: find song
    DB-->>SRepo: song doc
    Service->>RRepo: add_rating(song_id, rating)
    RRepo->>DB: update aggregates
    DB-->>RRepo: stats
    Service->>UoW: __exit__() commit
    Service->>Cache: delete("ratings:stats:{song_id}")
    Service-->>API: RatingStatsResponse
    API-->>Client: 201 Created
```

---

## Unit of Work Pattern

```mermaid
graph TB
    Start([Service calls UoW]) --> Enter["__enter__()"]
    Enter --> CheckTx{Transactions<br/>enabled?}
    CheckTx -->|Yes| TryTx["Try begin transaction"]
    CheckTx -->|No| Work
    TryTx --> TxCheck{Success?}
    TxCheck -->|Yes| AttachSession["Attach session"]
    TxCheck -->|No| Work
    AttachSession --> Work["Business logic"]
    Work --> Exit["__exit__()"]
    Exit --> ExitCheck{Exception?}
    ExitCheck -->|No| Commit["Commit"]
    ExitCheck -->|Yes| Rollback["Rollback"]
    Commit --> Cleanup["Cleanup"]
    Rollback --> Cleanup
    Cleanup --> End([Return])
```

---

## Repository Cache Pattern

```mermaid
graph LR
    Service["Service"] --> CheckCache{Check Cache?}
    CheckCache -->|Read| CacheHit{Hit?}
    CheckCache -->|Write| QueryDB
    CacheHit -->|Yes| Return["Return"]
    CacheHit -->|No| QueryDB["Query MongoDB"]
    QueryDB --> StoreCache["Store in cache"]
    StoreCache --> Return
```

---

## Project Structure

```
songs_project/
├── songs_api/
│   ├── __init__.py              # Flask app factory
│   ├── settings.py              # Pydantic settings
│   ├── schemas.py               # Request/response models
│   ├── api/v1/                  # Routes (auth, songs, system)
│   ├── services/                # Business logic
│   ├── repositories/            # Data access
│   ├── infrastructure/          # UoW, cache, rate limiter, DB
│   ├── models/documents.py      # MongoEngine models
│   ├── security/jwt_auth.py     # JWT authentication
│   └── scripts/                 # Seed scripts
├── tests/                       # Test suite
├── wsgi.py                      # Gunicorn entry
├── docker-compose.yml           # MongoDB + Redis + API
└── env.sample                   # Environment template
```

---

## Design Patterns

- **Unit of Work**: Transaction management via context manager
- **Repository**: Data access abstraction with cache integration
- **Service Layer**: Business logic orchestration
- **Dependency Injection**: SystemResources container
- **Cache-Aside**: Check cache → miss → query DB → store cache

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | Flask 3.x |
| Database | MongoDB + MongoEngine |
| Cache | Redis |
| Auth | JWT + bcrypt |
| Validation | Pydantic 2.x |
| Server | Gunicorn |
| Testing | pytest + mongomock |
