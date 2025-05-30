# On Kubernetes

This document contains instructions on installing, uninstalling and configuring Multi Tenant Operator on Kubernetes.

1. [Installing via Helm CLI](#installing-via-helm-cli)

1. [Uninstall](#uninstall-via-helm-cli)

## Requirements

* A **Kubernetes** cluster (v1.24 or higher)
* [Helm CLI](https://helm.sh/docs/intro/install/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/)
* To run on Kubernetes, two certificates are needed in the operator namespace for the operator to be up and running, named
    1. `quota-template-intconfig-server-cert` pointing to `multi-tenant-operator-quota-template-intconfig-webhook-service.{{ .Release.Namespace }}.svc.cluster.local`
    1. `webhook-server-cert` pointing to `multi-tenant-operator-webhook-service.{{ .Release.Namespace }}.svc.cluster.local`

    If you are using [Cert Manager](https://cert-manager.io/docs/installation/), these certificates will be handled by templates in Helm Chart

## Installing via Helm CLI

* Public Helm Chart of MTO is available at [Stakater ghcr Packages](https://github.com/orgs/stakater/packages/container/package/public/charts/multi-tenant-operator) and available Helm options can be seen at [MTO Helm Chart Options](./helm.md)

* Use `helm install` command to install MTO helm chart. Here, `bypassedGroups` has the names of groups which are designated as Cluster Admins in your cluster. For this example, we will use `system:masters`

```terminal
helm install tenant-operator oci://ghcr.io/stakater/public/charts/multi-tenant-operator --version 0.12.62 --namespace multi-tenant-operator --create-namespace --set bypassedGroups=system:masters'
```

!!! note
    It is better to install MTO in its preferred namespace, `multi-tenant-operator`

Wait for the pods to be up

```terminal
kubectl get pods -n multi-tenant-operator --watch
```

After all pods come in running state, you can follow [Tutorials](../tutorials/tenant/create-tenant.md).

### Enterprise License Configuration

For the Enterprise version, you need to have a ConfigMap `license` created in MTO's namespace `multi-tenant-operator`. You will get this ConfigMap when purchasing the Enterprise version. It would look like this:

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

MTO can be uninstalled by Helm CLI if Helm was used to install it earlier.

* Use `helm uninstall` command to remove the earlier created `Helm Release` in `multi-tenant-operator` namespace

```terminal
helm uninstall tenant-operator --namespace multi-tenant-operator
```

## Notes

* For details on licensing of MTO please refer [Pricing](../pricing.md).
* For more details on how to use MTO please refer [Tenant tutorial](../tutorials/tenant/create-tenant.md).
* For details on how to extend your MTO manager ClusterRole please refer [extend-default-clusterroles](../how-to-guides/extend-default-roles.md).
