Login terminal to gcloud
```bash
gcloud auth login
```

Set project ID
```bash
gcloud config set project project_id
```

Create the cluster
```bash
gcloud container clusters create dwk-cluster --zone=europe-north1-b --cluster-version=1.37 --disk-size=32 --num-nodes=4 --machine-type=e2-small
```

SET to the cluster that is created
```bash
gcloud container clusters get-credentials dwk-cluster --zone=europe-north1-b
```

Delete the cluster
```bash
gcloud container clusters delete dwk-cluster --zone=europe-north1-b
```

Create the required ns:
```bash
kubectl create ns exercises
```

Enable Gateway API
```bash
gcloud container clusters update dwk-cluster --location=europe-north1-b --gateway-api=standard
```

Get Loadbalancers
```bash
gcloud compute url-maps list
```


Create SA for github actions

# Create a service account
```bash
gcloud iam service-accounts create "github-actions-sa" \
  --display-name="GitHub Actions SA"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --role="roles/artifactregistry.writer" \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding my-dwk-gke \
  --role="roles/container.admin" \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com
```


```bash
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='alirezamor2021/devops-course'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```


```bash
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_ORG/YOUR_REPO"
```

There are several values here that need to be set correctly. The PROJECT_NUMBER can be seen by running the command gcloud projects list. We are now ready to set the action secrets:

Value of the SERVICE_ACCOUNT is github-actions-sa@PROJECT_ID.iam.gserviceaccount.com

Value of the WORKLOAD_IDENTITY_PROVIDER is a bit more complex:

```txt
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```