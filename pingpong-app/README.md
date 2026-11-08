# Ping-Pong Application

A lightweight FastAPI application that responds with an incrementing counter (`pong <count>`) on every GET request to `/pingpong`. Designed to run inside a Kubernetes cluster alongside a shared Ingress controller.

## Prerequisites

* [uv](https://github.com/astral-sh/uv) (for local dependency management)
* Docker
* A running Kubernetes cluster (e.g., Minikube, Kind) with an Ingress controller enabled

---

## Local Development with `uv`

1. **Initialize/Sync dependencies locally:**

   ```bash
   uv sync
   ```

2. **Run the application:**

   ```bash
   uv run python main.py
   ```

3. **Test locally:**

   ```bash
   curl http://localhost:3000/pingpong
   # Output: pong 0
   ```

---

## Building and Deployment

### 1. Build and Push the Docker Image

```bash
docker build -t <your-docker-hub-username>/pingpong:v1 .
docker push <your-docker-hub-username>/pingpong:v1
```

*(Make sure to update the image tag in `manifests/deployment.yaml` if you use a different name).*

### 2. Apply Kubernetes Manifests

Apply all resources stored in the `manifests/` directory:

```bash
kubectl apply -f manifests/
```

### 3. Verify Deployment

Check that your pods and services are running:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
```

### 4. Test the Ingress Route

Send a request through your cluster's ingress endpoint:

```bash
curl http://localhost/pingpong
# Output: pong 0

curl http://localhost/pingpong
# Output: pong 1
```