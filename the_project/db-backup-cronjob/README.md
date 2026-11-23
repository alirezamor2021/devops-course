# db-backup-cronjob

A Kubernetes CronJob that backs up the todo database to Google Cloud Storage once every 24 hours (03:00 UTC).

Each run:

1. An init container (`postgres:16`) runs `pg_dump` against `todo-postgres-svc` and writes a gzipped SQL dump to a shared `emptyDir`.
2. The main container (`google-cloud-cli`) authenticates with a service-account key and uploads the dump to
   `gs://devops-513709-todo-backups/<namespace>/todos-<UTC timestamp>.sql.gz`.

Connection settings come from the existing `todo-db-config` ConfigMap and `todo-postgres-secret` Secret. No custom image is needed.

## One-time setup

Run these on your machine. Never commit `key.json` (it is in `.gitignore`).

Set the project:

```bash
gcloud config set project devops-513709
```

Create the bucket:

```bash
gcloud storage buckets create gs://devops-513709-todo-backups --location=europe-north1 --uniform-bucket-level-access
```

Create the service account:

```bash
gcloud iam service-accounts create "todo-backup-sa" --display-name="Todo DB backup SA"
```

Allow it to create and read objects in the backup bucket only:

```bash
gcloud storage buckets add-iam-policy-binding gs://devops-513709-todo-backups \
  --member="serviceAccount:todo-backup-sa@devops-513709.iam.gserviceaccount.com" \
  --role="roles/storage.objectCreator"
```

```bash
gcloud storage buckets add-iam-policy-binding gs://devops-513709-todo-backups \
  --member="serviceAccount:todo-backup-sa@devops-513709.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

Create a key and store it as a Secret in the `project` namespace:

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=todo-backup-sa@devops-513709.iam.gserviceaccount.com
```

```bash
kubectl -n project create secret generic storage-sa-key --from-file=key.json=key.json
```

```bash
rm key.json
```

The GitHub workflow copies this Secret into branch environments, so their backups land under `gs://devops-513709-todo-backups/<branch>/`.

## Testing

Trigger a run without waiting for the schedule:

```bash
kubectl -n project create job --from=cronjob/todo-db-backup todo-db-backup-manual
```

```bash
kubectl -n project logs job/todo-db-backup-manual -c pg-dump
```

```bash
kubectl -n project logs job/todo-db-backup-manual -c upload
```

```bash
gcloud storage ls gs://devops-513709-todo-backups/project/
```

The backups can also be downloaded from the Google Cloud Console under Cloud Storage → Buckets → `devops-513709-todo-backups`.

## Restoring

```bash
gcloud storage cat gs://devops-513709-todo-backups/project/todos-<timestamp>.sql.gz | gunzip | kubectl -n project exec -i todo-postgres-ss-0 -- psql -U todos -d todos
```
