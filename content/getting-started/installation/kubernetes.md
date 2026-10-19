# On Kubernetes

This document contains instructions for installing, uninstalling, and configuring Multi Tenant Operator on Kubernetes.

1. [Installing via Helm CLI](#installing-via-helm-cli)
1. [Uninstall](#uninstall-via-helm-cli)

## Requirements

* A **Kubernetes** cluster (v1.24 or higher)
* [Helm CLI](https://helm.sh/docs/intro/install/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/)
* [Cert Manager](https://cert-manager.io/docs/installation/) installed in the cluster.

  To run on Kubernetes, two certificates are needed in the operator namespace for the operator to be up and running. These certificates will be handled by Certificate CRs of [Cert Manager](https://cert-manager.io/docs/) in the Helm Chart.

## Installing via Helm CLI

* The public Helm Chart for MTO is available at [Stakater ghcr Packages](https://github.com/orgs/stakater/packages/container/package/public/charts/multi-tenant-operator).

### Choose the bypassed groups

MTO's webhook refuses to create a namespace that does not belong to a tenant, unless the request comes from a member of one of its **bypassed groups**. List the groups your cluster administrators belong to there; otherwise they cannot create namespaces such as the one for cert-manager or an operator.

Check which groups your own user is in:

```terminal
kubectl auth whoami
```

Which group a cluster administrator has depends on how the cluster was set up:

| Cluster | Administrator group |
|---|---|
| Clusters built with `kubeadm` on Kubernetes 1.29 or later, including kind | `kubeadm:cluster-admins` |
| Older `kubeadm` clusters, and certificate-based admin users | `system:masters` |
| Managed clusters (AKS, EKS) and clusters behind an identity provider | The group that grants your administrators cluster-admin. `kubectl auth whoami` shows it. |

`webhook.manager.env.bypassedGroups` takes a comma-separated list. Put it in a values file: on the command line, `--set` reads a comma as a list separator.

### Install

Write the values file, listing your administrator groups:

```bash
cat > mto-values.yaml <<'EOF'
webhook:
  manager:
    env:
      bypassedGroups: system:masters,kubeadm:cluster-admins
EOF
```

Install the chart into MTO's namespace:

```bash
helm install tenant-operator oci://ghcr.io/stakater/public/charts/tenant-operator \
  --namespace multi-tenant-operator --create-namespace \
  --values mto-values.yaml
```

!!! note
    It is better to install MTO in its preferred namespace, `multi-tenant-operator`

Wait for MTO to be ready:

```bash
kubectl -n multi-tenant-operator wait deployment --all --for=condition=Available --timeout=10m
```

### Verify

Check that you can still create a namespace that belongs to no tenant. If this is refused, your user is not in a bypassed group: see [Choose the bypassed groups](#choose-the-bypassed-groups).

```bash
kubectl create namespace mto-install-check
kubectl delete namespace mto-install-check
```

Then create a tenant and check that MTO creates its namespace:

```bash
kubectl apply -f - <<'EOF'
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Quota
metadata:
  name: small
spec:
  resourcequota:
    hard:
      configmaps: "10"
---
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: install-check
spec:
  quota: small
  accessControl:
    owners:
      users: [admin@example.com]
  namespaces:
    withTenantPrefix: [dev]
EOF
kubectl wait namespace/install-check-dev --for=create --timeout=120s
kubectl get namespace install-check-dev -L stakater.com/tenant
```

```text
NAME                STATUS   AGE   TENANT
install-check-dev   Active   5s    install-check
```

Remove the check tenant when you are done. A tenant you delete keeps its namespaces by default, so delete the namespace too:

```bash
kubectl delete tenant install-check
kubectl delete quota small
kubectl delete namespace install-check-dev --ignore-not-found
```

You can now follow the [Tutorials](../../guides/create-tenant.md).

### Enterprise License Configuration

For the Enterprise version, you need to have a ConfigMap named `license` created in MTO's namespace `multi-tenant-operator`. You will get this ConfigMap when purchasing the Enterprise version. It would look like this:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: license
  namespace: multi-tenant-operator
data:
  payload.json: |
    {
        "metaData": {
            "tier" : "paid",
            "company": "<company name here>"
        }
    }
  signature.base64.txt: <base64 signature here>
```

## Uninstall via Helm CLI

MTO can be uninstalled using Helm CLI if Helm was used to install it earlier.

* Use the `helm uninstall` command to remove the previously created `Helm Release` in the `multi-tenant-operator` namespace:

```bash
helm uninstall tenant-operator --namespace multi-tenant-operator
```

## Notes

* For details on licensing of MTO, please refer to [Pricing](../../pricing.md).
* For more details on how to use MTO, please refer to the [Tenant tutorial](../../guides/create-tenant.md).
* For details on how to extend your MTO manager ClusterRole, please refer to [extend-default-clusterroles](../../guides/extend-default-roles.md).
