# Vault

[Vault](https://www.vaultproject.io/) is used to secure, store and tightly control access to tokens, passwords, certificates, and encryption keys for protecting secrets and other sensitive data using a UI, CLI, or http API.

To enable Vault multi-tenancy, a role has to be created in Vault under [Kubernetes authentication](https://developer.hashicorp.com/vault/docs/auth/kubernetes) with the following permissions:

```yaml
path "secret/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "sys/mounts" {
  capabilities = ["read", "list"]
}
path "sys/mounts/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "managed-addons/*" {
  capabilities = ["read", "list"]
}
path "auth/kubernetes/role/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "sys/auth" {
  capabilities = ["read", "list"]
}
path "sys/policies/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "identity/group" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "identity/group-alias" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "identity/group/name/*" {
  capabilities = ["read", "list"]
}
path "identity/group/id/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
```

If Bill (the cluster admin) has Vault configured in his cluster, then he can take benefit from MTO's integration with Vault.

MTO automatically creates Vault secret paths for tenants, where tenant members can securely save their secrets. It also authorizes tenant members to access these secrets via OIDC.

Bill would first have to integrate Vault with MTO by adding the details in IntegrationConfig. For more [details](../../kubernetes-resources/integration-config.md#vault)

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  integrations:
    vault:
      enabled: true
      authMethod: kubernetes
      accessInfo: 
        accessorPath: oidc/
        address: https://vault.apps.prod.abcdefghi.kubeapp.cloud/
        roleName: mto
        secretRef:       
          name: ''
          namespace: ''
      config: 
        ssoClient: vault
```

Bill then creates a tenant for Anna and John:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  accessControl:
    owners:
      users:
      - anna@acme.org
    viewers:
      users:
      - john@acme.org
  quota: small
  namespaces:
    sandboxes:
      enabled: false
```

Now Bill goes to `Vault` and sees that a path for `tenant` has been made under the name `bluesky/kv`, confirming that Tenant members with the Owner or Edit roles now have access to the tenant's Vault path.

Now if Anna sign's in to the Vault via OIDC, she can see her tenants path and secrets. Whereas if John sign's in to the Vault via OIDC, he can't see his tenants path or secrets as he doesn't have the access required to view them.

For more details around enabling Kubernetes auth in Vault, visit [here](https://developer.hashicorp.com/vault/docs/auth/kubernetes)
