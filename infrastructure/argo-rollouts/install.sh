#!/usr/bin/env bash
# Installs or upgrades the Argo Rollouts controller (and its CRDs) into "argo-rollouts".
# Install monitoring first: the ServiceMonitor CRD comes from kube-prometheus-stack.
set -euo pipefail

CHART_VERSION="2.43.12"   # app version v1.10.2
RELEASE="argo-rollouts"
NAMESPACE="argo-rollouts"
DIR="$(cd "$(dirname "$0")" && pwd)"

helm repo add argo https://argoproj.github.io/argo-helm >/dev/null 2>&1 || true
helm repo update argo

helm upgrade --install "$RELEASE" argo/argo-rollouts \
  --version "$CHART_VERSION" \
  --namespace "$NAMESPACE" --create-namespace \
  -f "$DIR/values.yaml" \
  --wait --timeout 5m

kubectl -n "$NAMESPACE" get pods
