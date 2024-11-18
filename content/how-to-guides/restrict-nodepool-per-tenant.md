# Restrict tenant workloads to specific nodes

> Available on OpenShift, Azure Kubernetes Service and self-hosted Kubernetes (where you have access to [enable non-default admission controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers))

Bill is a cluster admin running Azure Kubernetes Service that wants to make sure that specific tenants are restricted to use a certain set of nodes. To do this he can apply annotations defining a tenants namespaces [`nodeSelectors`](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector).

!!! note
    #### About setting `nodeSelector` on namespace

    For Kubernetes deployments  [PodNodeSelector admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#podnodeselector) that is enabled by default in AKS but needs to be [manually enabled](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#how-do-i-turn-on-an-admission-controller) otherwise.

    The annotation is `scheduler.alpha.kubernetes.io/node-selector`

    For OpenShift there is a similar feature that works by setting the annotation `openshift.io/node-selector`.

Bill needs to select what label he wants to use as a node selector. In this case he wants to limit the `staging` tenant to only use nodes with label `agentpool` set to `small-pool`.

Bill adds the node selector annotation to all the namespaces for his `staging` tenant.

!!! note
    We have used the label `agentpool` in this example because it also demonstrates how one can limit a specific tenant to a certain [node pool in AKS](https://learn.microsoft.com/en-us/azure/aks/create-node-pools) (`small-pool` in this case). Similar concepts exist for most cloud providers, but the exact labels might differ, consult your providers documentation for more details.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Tenant
metadata:
  name: staging
spec:
  # Some fields have been omitted for clarity
  quota: quota-sample
  namespaces:
    withTenantPrefix:
      - alpha
      - beta
    metadata:
      common:
        annotations:
          scheduler.alpha.kubernetes.io/node-selector: agentpool=small-pool
```

This will set the annotation to all the tenants namespaces which in turn tells the [PodNodeSelector admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#podnodeselector) that all workloads in the tenants namespaces should be placed on nodes with the label `agentpool=small-pool`.

If Bill were to only want to limit a subset of a tenants namespaces he could use other fields in metadata as expected

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Tenant
metadata:
  name: production
spec:
  # Some fields have been omitted for clarity
  quota: quota-sample
  namespaces:
    withTenantPrefix:
      - alpha
      - beta
    metadata:
      sandbox:
        annotations:
          openshift.io/node-selector: machine-pool=small-pool
      specific:
        - namespaces: ["prod"]
          annotations:
            openshift.io/node-selector: machine-pool=production
```

!!! note
    This example instead uses the label for [OpenShift Container Platform on AWS](https://docs.redhat.com/en/documentation/red_hat_openshift_service_on_aws/4/html/cluster_administration/manage-nodes-using-machine-pools). The label `machine-pool` needs to be [set on the machine pool](https://docs.redhat.com/en/documentation/red_hat_openshift_service_on_aws/4/html/cluster_administration/manage-nodes-using-machine-pools#rosa-adding-node-labels_rosa-managing-worker-nodes) for it to work.
