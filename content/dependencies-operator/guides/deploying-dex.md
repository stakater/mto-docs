# Deploying Dex

Dex is an OpenID Connect (OIDC) identity provider that federates authentication to upstream identity providers such as LDAP, SAML, and OAuth2 services.

## Prerequisites

- The MTO Dependencies Operator is running in your cluster (bundled with MTO).
- If using ingress, ensure an ingress controller is available.
- If using external storage (e.g. PostgreSQL), have the database accessible from the cluster.

## Minimal Example

The following CR deploys a basic Dex instance using in-cluster Kubernetes storage:

```yaml
apiVersion: dependencies.tenantoperator.stakater.com/v1alpha1
kind: Dex
metadata:
  name: dex
spec:
  replicaCount: 1
  config:
    issuer: https://dex.example.com
    storage:
      type: kubernetes
      config:
        inCluster: true
  service:
    type: ClusterIP
    ports:
      http:
        port: 5556
```

## Common Customizations

**Adding a static OAuth2 client:**

```yaml
spec:
  config:
    staticClients:
      - id: my-app
        name: My Application
        secret: my-client-secret
        redirectURIs:
          - https://my-app.example.com/callback
```

**Enabling ingress:**

```yaml
spec:
  ingress:
    enabled: true
    hosts:
      - host: dex.example.com
        paths:
          - path: /
            pathType: Prefix
```

**Configuring an upstream LDAP connector:**

```yaml
spec:
  config:
    connectors:
      - type: ldap
        id: ldap
        name: LDAP
        config:
          host: ldap.example.com:636
          rootCA: /etc/dex/tls/ca.crt
          bindDN: cn=admin,dc=example,dc=com
          bindPW: admin-password
          userSearch:
            baseDN: ou=users,dc=example,dc=com
            filter: "(objectClass=inetOrgPerson)"
            username: uid
            emailAttr: mail
```

## Verification

Confirm Dex is running:

```bash
kubectl get pods -l app.kubernetes.io/name=dex
```

## Further Reading

- [Dex Helm chart documentation](https://github.com/dexidp/helm-charts)
- [Dex official documentation](https://dexidp.io/docs/)
