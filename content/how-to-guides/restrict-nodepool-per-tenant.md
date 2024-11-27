# Restricting Tenant Workloads to Specific Nodes

Utilizing Kubernetes Node Selectors and the Multi-Tenant Operator's advanced templating capabilities allows administrators to restrict tenant workloads to specific nodes or node groups.

---

## Azure Kubernetes Service (AKS) Node Pools

To confine a tenant's workloads to a specific [AKS NodePool](https://learn.microsoft.com/en-us/azure/aks/create-node-pools), the [PodNodeSelector admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#podnodeselector) can be used. This controller ensures all workloads in specified namespaces are scheduled on the designated node pool by setting the annotation `scheduler.alpha.kubernetes.io/node-selector` to `agentpool=<nodepool_name>`.

### Prerequisites

- An AKS cluster.
- An existing node pool, for example, one named `marketing-pool`.

### How To

To ensure all namespaces associated with the tenant `marketing` are scheduled on the `marketing-pool` node pool, the annotation `scheduler.alpha.kubernetes.io/node-selector` with value `agentpool=marketing-pool` is added to `tenant.spec.namespaces.metadata.common.annotations`.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Tenant
metadata:
  name: marketing
spec:
  # Some fields have been omitted for clarity
  quota: quota-sample
  namespaces:
    withTenantPrefix:
      - alpha
      - beta
    metadata:
      common:
        annotations: # these annotations will be added to *all* of the tenants namespaces
          scheduler.alpha.kubernetes.io/node-selector: agentpool=marketing-pool
```

### Result

Once the `Tenant` resource is deployed, all workloads for the `marketing` tenant will be scheduled in the `marketing-pool` node pool.

---

## OpenShift

For OpenShift environments, workloads can be restricted to specific machine pools. This process is applicable across different OpenShift versions, though the method of creating the machine pool might vary. To restrict workloads, first create a machine pool and assign it a unique label. Then, use the annotation `openshift.io/node-selector` in the tenant’s namespaces, which ensures that workloads are scheduled on nodes with matching label key-value pairs.

### Prerequisites

- A RedHat OpenShift cluster.
- A configured machine pool. Ensure the machine pool has a unique label, which can be added during creation or configured after creation. For instance, the machine pool in this example is labeled as `pool-name=marketing-pool`.

### How To

To restrict workloads for the tenant, add the annotation `openshift.io/node-selector` with a value of `pool-name=marketing-pool` to `tenant.spec.namespaces.metadata.common.annotations`.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Tenant
metadata:
  name: marketing
spec:
  # Some fields have been omitted for clarity
  quota: quota-sample
  namespaces:
    withTenantPrefix:
      - alpha
      - beta
    metadata:
      common:
        annotations: # these annotations will be added to *all* of the tenants namespaces
          openshift.io/node-selector: pool-name=marketing-pool
```

### Result

When deployed, this configuration ensures that all workloads in the tenant's namespaces are scheduled on nodes in the `marketing-pool`.
