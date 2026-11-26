#!/usr/bin/env bash
# Installs or upgrades kube-prometheus-stack into the "prometheus" namespace.
#
#   ./install.sh                                  # ClusterIP, use kubectl port-forward
#   ALLOWED_CIDR=203.0.113.7/32 ./install.sh      # also expose Prometheus to that IP only
#
# The allowed IP is passed in, not stored here, because this repository is public.
set -euo pipefail

CHART_VERSION="94.0.0"
RELEASE="kube-prometheus-stack"
NAMESPACE="prometheus"
DIR="$(cd "$(dirname "$0")" && pwd)"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update prometheus-community

expose_args=()
if [ -n "${ALLOWED_CIDR:-}" ]; then
  # GKE creates a network load balancer whose firewall rule only admits ALLOWED_CIDR.
  expose_args=(
    --set prometheus.service.type=LoadBalancer
    --set "prometheus.service.loadBalancerSourceRanges={${ALLOWED_CIDR}}"
  )
fi

helm upgrade --install "$RELEASE" prometheus-community/kube-prometheus-stack \
  --version "$CHART_VERSION" \
  --namespace "$NAMESPACE" --create-namespace \
  -f "$DIR/kube-prometheus-stack/values.yaml" \
  ${expose_args[@]+"${expose_args[@]}"} \
  --wait --timeout 10m

kubectl -n "$NAMESPACE" get pods,svc
