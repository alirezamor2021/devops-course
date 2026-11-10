# todo-backend

A small REST service that stores todo items for the project. It is part of the DevOps with Kubernetes course project and is used by `todo-app`, which serves the HTML/JS single page application and the random image.

Todos are kept **in memory**, so they are lost when the process or pod restarts. A database replaces this in a later exercise.

## Endpoints

| Method | Path     | Description                | Success response |
|--------|----------|----------------------------|------------------|
| GET    | `/todos` | List all todos             | `200` with a JSON array |
| POST   | `/todos` | Create a new todo          | `201` with the created todo |

### GET /todos

```bash
curl http://localhost:3000/todos
```

```json
[
  {"id": 1, "text": "Learn Kubernetes basics"},
  {"id": 2, "text": "Deploy application to cluster"},
  {"id": 3, "text": "Configure persistent volumes"}
]
```

### POST /todos

Request body:

```json
{"text": "Buy milk"}
```

```bash
curl -X POST http://localhost:3000/todos \
  -H 'Content-Type: application/json' \
  -d '{"text": "Buy milk"}'
```

Response (`201`):

```json
{"id": 4, "text": "Buy milk"}
```

Validation: `text` is required and must be 1 to 140 characters. Otherwise the service responds with `422 Unprocessable Entity`.

## Tech stack

- Python 3.12
- [FastAPI](https://fastapi.tiangolo.com/) and [Uvicorn](https://www.uvicorn.org/)
- [uv](https://docs.astral.sh/uv/) for dependency management

## Running locally

```bash
cd the_project/todo-backend
uv sync
uv run main.py
```

The service listens on port `3000`. Interactive API docs are available at <http://localhost:3000/docs>.

## Docker

```bash
docker build -t <your-registry>/todo-backend:latest .
docker run --rm -p 3000:3000 <your-registry>/todo-backend:latest
```

## Kubernetes

The service is exposed inside the cluster by `todo-backend-svc` (port `2345` forwarding to container port `3000`), and the ingress routes `/todos` to it. All other paths, including `/image`, go to `todo-app`.

```bash
kubectl apply -f manifests/
kubectl get pods,svc,ingress
```

Keep `replicas: 1` for now. Because data is stored in memory, each replica would hold its own separate list.

## Project layout

```
todo-backend/
├── main.py
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── manifests/
└── README.md
```