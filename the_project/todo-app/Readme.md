# Todo App (Exercise 1.02)

A lightweight Python 3.14 web server managed by `uv` that listens on a configurable `PORT` environment variable and outputs `"Server started in port NNNN"` upon startup.

---

## Prerequisites

* [uv](https://docs.astral.sh/uv/) installed locally
* [Docker](https://www.docker.com/) installed
* A Kubernetes cluster (`minikube`, `k3d`, `kind`, or a cloud cluster) with `kubectl` configured

---

## Local Development (with `uv`)

1. **Navigate to the application directory:**
   ```bash
   cd the_project/todo-app
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

## Running in Kubernetes via kubectl

### Step 1: Make Image Available to Your Cluster

* **If using a local cluster (minikube / kind):**
  * Minikube: `minikube image load todo-app:latest`
  * Kind: `kind load docker-image todo-app:latest`

* **If using a remote registry (e.g., Docker Hub):**
  ```bash
  docker tag todo-app:latest <your-username>/todo-app:v1.0.0
  docker push <your-username>/todo-app:v1.0.0
  ```

### Step 2: Create the Deployment using Imperative Commands

Run the following command to deploy the web server directly from the CLI:

```bash
kubectl create deployment todo-app --image=todo-app:latest --replicas=1
```
*(Note: If using a private registry or custom tag, replace `--image=todo-app:latest` with `<your-username>/todo-app:v1.0.0`)*

---

## Monitoring, Accessing, and Testing

1. **Check Pod Status**  
   Verify that your deployment is running successfully:
   ```bash
   kubectl get pods -l app=todo-app
   ```

2. **View Startup Logs**  
   Check the application logs to confirm the startup message:
   ```bash
   kubectl logs -f deployment/todo-app
   ```
   **Expected Output:**
   ```text
   Server started in port 5000
   ```

3. **Port-Forward to Test the Web Server Locally**  
   Since the application is running inside a container in Kubernetes, you can use port-forwarding to route traffic from your machine directly to the pod/deployment:
   ```bash
   kubectl port-forward deployment/todo-app 5000:5000
   ```

4. **Test the Endpoint via curl**  
   Open a separate terminal window while port-forwarding is running and test the server response:
   ```bash
   curl http://localhost:5000
   ```
   **Expected Response:**
   ```text
   Todo app is running!
   ```

---

## Clean Up

To delete the deployment and clean up resources when finished:

```bash
kubectl delete deployment todo-app
```