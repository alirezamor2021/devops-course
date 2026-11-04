# log_output

A lightweight Python 3.14 application managed by `uv` that generates a random string at startup and outputs it every 5 seconds along with an ISO timestamp, deployed declaratively in Kubernetes.

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

2. **Run Locally:**
   ```bash
   uv run python main.py
   ```

---

## Docker Instructions

1. **Build the Docker Image (using the image name `log-outout`):**
   ```bash
   docker build -t log-outout:latest .
   ```

2. **Run the Docker Container:**
   ```bash
   docker run --rm log-outout:latest
   ```

---

## Running in Kubernetes Declaratively

### Step 1: Make the Image Available to Your Cluster

- **If using a local cluster (minikube / kind):**
  - Minikube: `minikube image load log-outout:latest`
  - Kind: `kind load docker-image log-outout:latest`

- **If using a remote registry (e.g., Docker Hub):**
  ```bash
  docker tag log-outout:latest <your-username>/log-outout:v1.0.0
  docker push <your-username>/log-outout:v1.0.0
  ```
  *(Remember to update the `image` field in `manifests/deployment.yaml` if using a remote registry tag)*

### Step 2: Apply the Declarative Manifest

Deploy the application using `kubectl apply`:

```bash
kubectl apply -f manifests/deployment.yaml
```

### Step 3: Check Status, Restart, and View Logs

1. **Verify the Pod is running:**
   ```bash
   kubectl get pods -l app=log-output
   ```

2. **View live logs (outputs the stored random string every 5 seconds):**
   ```bash
   kubectl logs -f deployment/log-output
   ```
   **Example Output:**
   ```text
   [2026-11-04T22:15:00.000000Z]: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
   [2026-11-04T22:15:05.000000Z]: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
   ```

3. **Restart the Deployment (to test new startup string generation):**
   ```bash
   kubectl rollout restart deployment/log-output
   ```

4. **Clean Up:**
   To delete the deployment and clean up resources:
   ```bash
   kubectl delete -f manifests/deployment.yaml
   ```