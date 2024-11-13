# Networking tenant policies

The networking tenant policies limits how tenants can communicate with each other.


## Disable intra-tenant networking


```yaml title="Integration Configuration"
apiVersion: v1beta1
kind: integrationconfigs.tenantoperator.stakater.com
spec:
    # other fields...
    tenantPolicies:
        network:
            disableIntraTenantNetworking: true

```

The flags works by deploying a set of `NetworPolicies` for each tenant which filteres incomming traffic comming from another tenants namespace. It allows all other traffic.

The `NetworkPolicy` is as follows:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: disable-intra-tenant-networking-${tenant} # tenant will be substituted for the tenant-name
  namespace: test # Will be deployed to all the tenants namespaces
spec:
  podSelector: {} # The rule selects all pods
  policyTypes:
    - Ingress # We only filter incomming traffic
  ingress:
    - from:
      - namespaceSelector:
          matchExpressions:
            - key: stakater.com/tenant
              operator: DoesNotExist
      - namespaceSelector:
          matchLabels:
          stakater.com/tenant: ${tenant}
```

#### Demo
![Disable intra-tenant networking demo](../../images/disableIntraTenantNetworkingDemo.gif)