# Argo Rollouts

Controller for progressive delivery (canary / blue-green) with automated analysis.
The Ping-pong app is a `Rollout` that checks the namespace CPU usage in Prometheus before
it finishes an update (see `pingpong-app/manifests/`).

Install [monitoring](../monitoring/README.md) first: the analysis queries that Prometheus.

## Install / upgrade

```bash
./infrastructure/argo-rollouts/install.sh
```

## Dashboard

Only reachable through port-forward (ClusterIP service, no Ingress or load balancer).
Open http://localhost:3100/rollouts after running:

```bash
kubectl port-forward svc/argo-rollouts-dashboard -n argo-rollouts 3100:3100
```

## kubectl plugin

```bash
brew install argoproj/tap/kubectl-argo-rollouts
```

```bash
kubectl argo rollouts get rollout pingpong-app -n exercises --watch
```

## Exercise 4.4: CPU usage analysis

`pingpong-app/manifests/analysistemplate.yaml` sums the CPU usage rate of all containers in the
`exercises` namespace once a minute for 5 minutes:

```promql
sum(rate(container_cpu_usage_seconds_total{namespace="exercises", container!=""}[2m]))
```

The Rollout first runs the new version next to the old one (`setWeight: 50`), then runs the
analysis. If any measurement is `>= 0.2` cores the analysis fails, the rollout is aborted and
the old version keeps serving.

To see an update being refused, lower the threshold below the idle usage
(`successCondition: result[0] < 0.001`), apply, then change the image:

```bash
kubectl apply -f pingpong-app/manifests/analysistemplate.yaml
```

```bash
kubectl argo rollouts set image pingpong-app -n exercises pingpong=alirezamor2021/pingpong:v4.4.0-amd64
```

The rollout goes `Degraded` with the analysis `Failed`, and the stable pod stays on the old
image. Restore the threshold and run `kubectl argo rollouts retry rollout pingpong-app -n exercises`.
