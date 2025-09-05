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

* Use the `helm install` command to install the MTO helm chart. Here, `webhook.manager.env.bypassedGroups` has the names of groups which are designated as Cluster Admins in your cluster. For this example, we will use `system:masters`

```terminal
helm install tenant-operator oci://ghcr.io/stakater/public/charts/tenant-operator --namespace multi-tenant-operator --create-namespace --set 'webhook.manager.env.bypassedGroups=system:masters'
```

!!! note
    It is better to install MTO in its preferred namespace, `multi-tenant-operator`

Wait for the pods to be up:

```terminal
kubectl get pods -n multi-tenant-operator --watch
```

After all pods come in running state, you can follow the [Tutorials](../kubernetes-resources/tenant/how-to-guides/create-tenant.md).

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

```terminal
helm uninstall tenant-operator --namespace multi-tenant-operator
```

## Notes

* For details on licensing of MTO, please refer to [Pricing](../pricing.md).
* For more details on how to use MTO, please refer to the [Tenant tutorial](../kubernetes-resources/tenant/how-to-guides/create-tenant.md).
* For details on how to extend your MTO manager ClusterRole, please refer to [extend-default-clusterroles](../kubernetes-resources/tenant/how-to-guides/extend-default-roles.md).
