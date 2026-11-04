# Todo App 

A lightweight Python 3.14 web server managed by `uv` that listens on a configurable `PORT` environment variable, outputs `"Server started in port NNNN"` upon startup, and is deployed declaratively in Kubernetes.

---

## Directory Structure

```text
the_project/todo-app/
├── manifests/
│   └── deployment.yaml
├── Dockerfile
├── main.py
├── pyproject.toml
└── README.md
```

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed locally
- [Docker](https://www.docker.com/) installed
- A Kubernetes cluster (`minikube`, `k3d`, `kind`, or a cloud cluster) with `kubectl` configured

---

## Local Development (with `uv`)

1. **Initialize and Install Dependencies:**
   ```bash
   uv sync
   ```

2. **Run locally using default PORT (5000):**
   ```bash
   uv run python main.py
   ```

3. **Run with a custom PORT environment variable:**
   ```bash
   PORT=8080 uv run python main.py
   ```

---

## Docker Instructions

1. **Build the Docker Image:**
   ```bash
   docker build -t todo-app:latest .
   ```

2. **Run the Docker Container:**
   ```bash
   docker run --rm -e PORT=5000 -p 5000:5000 todo-app:latest
   ```

---

## Running in Kubernetes Declaratively

### Step 1: Make Image Available to Your Cluster

- **If using a local cluster (minikube / kind):**
  - **Minikube:** `minikube image load todo-app:latest`
  - **Kind:** `kind load docker-image todo-app:latest`
- **If using a remote registry (e.g., Docker Hub):**
  ```bash
  docker tag todo-app:latest <your-username>/todo-app:v1.0.0
  docker push <your-username>/todo-app:v1.0.0
  ```
  *(Remember to update the `image` field in `manifests/deployment.yaml` if using a remote registry tag).*

### Step 2: Apply the Declarative Manifest

Deploy the web server using `kubectl apply`:
```bash
kubectl apply -f manifests/deployment.yaml
```

### Step 3: Check Status, Logs, and Testing

1. **Verify the Pod is running:**
   ```bash
   kubectl get pods -l app=todo-app
   ```

2. **View startup logs:**
   ```bash
   kubectl logs -f deployment/todo-app
   ```
   **Expected Output:**
   ```plaintext
   Server started in port 5000
   ```

3. **Port-Forward to Test Locally:**
   Route traffic from your local machine to the Kubernetes pod:
   ```bash
   kubectl port-forward deployment/todo-app 5000:5000
   ```

4. **Test the Endpoint via curl:**
   Open a separate terminal window and run:
   ```bash
   curl http://localhost:5000
   ```
   **Expected Response:**
   ```plaintext
   Todo app is running!
   ```

5. **Restart the Deployment (Rollout Restart):**
   ```bash
   kubectl rollout restart deployment/todo-app
   ```

6. **Clean Up:**
   To delete the deployment and clean up resources using the manifest:
   ```bash
   kubectl delete -f manifests/deployment.yaml
   ```