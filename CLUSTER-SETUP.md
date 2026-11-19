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