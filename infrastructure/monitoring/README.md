# Monitoring (kube-prometheus-stack)

Prometheus, Alertmanager, Grafana, kube-state-metrics and node-exporter, installed with Helm
into the `prometheus` namespace.

```
infrastructure/
└── monitoring/
    ├── install.sh                       # helm upgrade --install, chart version pinned
    └── kube-prometheus-stack/
        └── values.yaml                  # our overrides of the chart defaults
```

## Install / upgrade

Only reachable through `kubectl port-forward`:

```bash
./infrastructure/monitoring/install.sh
```

Also reachable from one IP address (GKE creates a network load balancer, ~$18/month,
whose firewall rule only admits that address):

```bash
ALLOWED_CIDR=<your-ip>/32 ./infrastructure/monitoring/install.sh
```

Find your current public IP with `curl -s https://ifconfig.me`.

## Access Prometheus

Through the service with port-forward, then open http://localhost:9090:

```bash
kubectl port-forward svc/kube-prometheus-stack-prometheus -n prometheus 9090:9090
```

Or, when installed with `ALLOWED_CIDR`, from that IP at `http://<EXTERNAL-IP>:9090`:

```bash
kubectl get svc kube-prometheus-stack-prometheus -n prometheus
```

## Access Grafana

```bash
kubectl -n prometheus get secret kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 -d; echo
```

```bash
kubectl port-forward svc/kube-prometheus-stack-grafana -n prometheus 3000:80
```

## Exercise 4.3: pods created by StatefulSets

`kube_pod_info` has one series (value `1`) per pod, labelled with the pod's namespace and
the kind of its owner, so summing the filtered series counts the pods:

```promql
sum(kube_pod_info{namespace="prometheus", created_by_kind="StatefulSet"})
```

With this chart that is the Prometheus and Alertmanager pods.
