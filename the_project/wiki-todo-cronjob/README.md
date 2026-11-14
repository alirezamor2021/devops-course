# wiki-todo-cronjob

A Kubernetes CronJob that creates a new todo every hour, reminding you to read a random Wikipedia article. It is part of the DevOps with Kubernetes course project and talks to `todo-backend`.

Each run:

1. Requests `https://en.wikipedia.org/wiki/Special:Random` without following the redirect.
2. Reads the article URL from the `Location` header.
3. Sends `POST /todos` to `todo-backend` with the text `Read <URL>`.

The URL is plain text, not a hyperlink, so you can copy and paste it from the todo list.

If the resulting text is longer than `MAX_TODO_LENGTH` (the backend's limit), the script picks another random article, up to `MAX_ATTEMPTS` times. If none fits, the Job fails and Kubernetes retries it.

## Configuration

All settings come from environment variables. The script exits with an error if one is missing.

| Variable | Description | Example |
|----------|-------------|---------|
| `WIKI_RANDOM_URL` | URL that redirects to a random article | `https://en.wikipedia.org/wiki/Special:Random` |
| `TODO_BACKEND_URL` | Full URL of the backend's `POST /todos` endpoint | `http://todo-backend-svc:2345/todos` |
| `MAX_TODO_LENGTH` | Maximum todo length, from the shared `todo-config` ConfigMap | `140` |
| `MAX_ATTEMPTS` | Number of random articles to try before giving up | `10` |
| `REQUEST_TIMEOUT_SECONDS` | Timeout for each HTTP request | `10` |
| `USER_AGENT` | Descriptive User-Agent sent to Wikipedia, which may block the default Python one | `kube-todo-reminder/1.0 (course exercise)` |

## Running locally

The script uses only the Python standard library.

```bash
cd the_project/wiki-todo-cronjob

WIKI_RANDOM_URL=https://en.wikipedia.org/wiki/Special:Random \
TODO_BACKEND_URL=http://localhost:3000/todos \
MAX_TODO_LENGTH=140 \
MAX_ATTEMPTS=10 \
REQUEST_TIMEOUT_SECONDS=10 \
USER_AGENT="kube-todo-reminder/1.0 (local test)" \
python main.py
```

This needs a running todo-backend at the given URL.

## Docker

```bash
docker build -t alirezamor2021/wiki-todo-cronjob:v1.0.0 .
docker push alirezamor2021/wiki-todo-cronjob:v1.0.0
```

## Kubernetes

The manifest is in `manifests/wiki-todo-cronjob.yaml` and deploys to the `project` namespace.

```bash
kubectl apply -f manifests/wiki-todo-cronjob.yaml
kubectl get cronjob -n project
```

Key settings:

- **Schedule:** `0 * * * *` (minute 0 of every hour, in the cluster's timezone, normally UTC).
- **`concurrencyPolicy: Forbid`:** a run is skipped if the previous one is still going.
- **`backoffLimit: 3`:** a failed Job is retried up to three times.
- **History:** the last 3 successful and 3 failed Jobs are kept, so their logs stay available.

The `todo-config` ConfigMap and the `todo-backend-svc` Service must already exist in the `project` namespace.

### Trigger a run manually

You don't have to wait an hour:

```bash
kubectl create job --from=cronjob/wiki-todo wiki-todo-manual -n project
kubectl logs job/wiki-todo-manual -n project
kubectl delete job wiki-todo-manual -n project
```

A successful run logs `Created todo 'Read https://en.wikipedia.org/wiki/...' (HTTP 201)`. The new todo then appears in the todo list.

### Troubleshooting

- **Connection error:** check that the Service is named `todo-backend-svc` and that the pod can reach the internet.
- **HTTP 403 from Wikipedia:** make `USER_AGENT` more specific.
- **`Missing required environment variable`:** an entry is missing from the manifest's `env:` section.
- **Past runs:** `kubectl get jobs -n project` lists them, and `kubectl logs job/<name> -n project` shows each one's output.

## Project layout

```
wiki-todo-cronjob/
├── main.py
├── Dockerfile
├── manifests/
│   └── wiki-todo-cronjob.yaml
└── README.md
```