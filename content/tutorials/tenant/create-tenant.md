# Creating a Tenant

Bill, a cluster admin, has been tasked by the CTO of NordMart to set up a new tenant for Anna's team. Following the request, Bill proceeds to create a new tenant named bluesky in the Kubernetes cluster.

## Setting Up the Tenant

To establish the tenant, Bill crafts a Tenant Custom Resource (CR) with the necessary specifications:

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
    editors:
      users:
        - john@aurora.org
      groups:
        - alpha
  namespaces:
    sandboxes:
      enabled: false
EOF
```

In this configuration, Bill specifies <anna@aurora.org> as the owner, giving her full administrative rights over the tenant. The editor role is assigned to <john@aurora.org> and the group alpha, providing them with editing capabilities within the tenant's scope.

## Verifying the Tenant Creation

After creating the tenant, Bill checks its status to confirm it's active and operational:

```bash
kubectl get tenants.tenantoperator.stakater.com bluesky
NAME       STATE    AGE
bluesky    Active   3m
```

This output indicates that the tenant bluesky is successfully created and in an active state.

## Checking User Permissions

To ensure the roles and permissions are correctly assigned, Anna logs into the cluster to verify her capabilities:

**Namespace Creation:**

```bash
kubectl auth can-i create namespaces
yes
```

Anna is confirmed to have the ability to create namespaces within the tenant's scope.


**Cluster Resources Access:**

```bash
kubectl auth can-i get namespaces
no

kubectl auth can-i get persistentvolumes
no
```

As expected, Anna does not have access to broader cluster resources outside the tenant's confines.

**Tenant Resource Access:**

```bash
kubectl auth can-i get tenants.tenantoperator.stakater.com
no
```

Access to the Tenant resource itself is also restricted, aligning with the principle of least privilege.

## Adding Multiple Owners to a Tenant

Later, if there's a need to grant administrative privileges to another user, such as Anthony, Bill can easily update the tenant's configuration to include multiple owners:

```yaml
kubectl apply -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
        - anthony@aurora.org
    editors:
      users:
        - john@aurora.org
      groups:
        - alpha
  namespaces:
    sandboxes:
      enabled: false
EOF
```

With this update, both Anna and Anthony can administer the tenant bluesky, including the creation of namespaces:

```bash
kubectl auth can-i create namespaces
yes
```

This flexible approach allows Bill to manage tenant access control efficiently, ensuring that the team's operational needs are met while maintaining security and governance standards.
