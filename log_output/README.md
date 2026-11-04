# log-output

A lightweight Python 3.14 application managed by `uv` that generates a random string at startup and outputs it every 5 seconds along with an ISO timestamp.

---

## Prerequisites

* [uv](https://docs.astral.sh/uv/) installed locally
* [Docker](https://www.docker.com/) installed
* A Kubernetes cluster (`minikube`, `k3d`, `kind`, or a cloud cluster) with `kubectl` configured

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

1. **Build the Docker Image:**
   ```bash
   docker build -t log-output:latest .
   ```

2. **Run the Docker Container:**
   ```bash
   docker run --rm log-output:latest
   ```

---

## Running in Kubernetes via `kubectl`

### Step 1: Make the Image Available to Your Cluster

* **If using a remote registry (e.g., Docker Hub):**
  Tag and push your image:
  ```bash
  docker tag log-output:latest <your-username>/log-output:v1.0.0
  docker push <your-username>/log-output:v1.0.0
  ```

* **If using a local cluster (`minikube` / `kind`):**
  Load the built image directly:
  * Minikube: `minikube image load log-output:latest`
  * Kind: `kind load docker-image log-output:latest`

---

### Step 2: Create the Deployment using Imperative Commands

Run the following command to deploy the application directly from the CLI:

```bash
kubectl create deployment log-output --image=log-output:latest --replicas=1
```

*(Note: If using a private registry or custom image tag, substitute `log-output:latest` with `<your-username>/log-output:v1.0.0`)*

---

### Step 3: Check Logs & Status

1. **Verify the Pod is running:**
   ```bash
   kubectl get pods -l app=log-output
   ```

2. **View the live logs (outputs the stored random string every 5 seconds):**
   ```bash
   kubectl logs -f deployment/log-output
   ```

   **Example Output:**
   ```text
   [2026-11-04T21:20:00.000000+00:00] App initialized with string: k9X2pQ8mR1aZ
   [2026-11-04T21:20:00.000123+00:00] Stored String: k9X2pQ8mR1aZ
   [2026-11-04T21:20:05.001456+00:00] Stored String: k9X2pQ8mR1aZ
   [2026-11-04T21:20:10.002890+00:00] Stored String: k9X2pQ8mR1aZ
   ```

3. **Clean Up:**
   To delete the deployment when you're finished:
   ```bash
   kubectl delete deployment log-output
   ```