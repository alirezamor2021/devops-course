Create the cluster
```bash
gcloud container clusters create dwk-cluster --zone=europe-north1-b --cluster-version=1.37 --disk-size=32 --num-nodes=4 --machine-type=e2-small
```

SET to the cluster that is created
```bash
gcloud container clusters get-credentials dwk-cluster --zone=europe-north1-b
```

Delete the cluster
```
gcloud container clusters delete dwk-cluster --zone=europe-north1-b
```