# API

All endpoints except `/health`, registration, and login require `Authorization: Bearer <token>`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/auth/register` | Register and return access token |
| POST | `/auth/login` | Sign in |
| POST/GET | `/conversations` | Create/list conversations |
| GET | `/conversations/{id}` | Read owned conversation |
| POST | `/agent/run` | Create plan and run supported local workflow |
| GET | `/agent/tasks/{id}` | Read owned task |
| POST | `/files/upload` | Upload supported private file |
| GET/DELETE | `/files` and `/files/{id}` | List/delete owned file |
| GET/POST | `/memory` | List/create user memory |
| DELETE | `/memory/{id}` | Delete user memory |

Interactive OpenAPI docs are available at `/docs` while the API is running.
