# Configuring Managed Namespaces and ServiceAccounts in IntegrationConfig

Bill is a cluster admin who can use `IntegrationConfig` to configure how `Multi Tenant Operator (MTO)` manages the cluster.

By default, MTO watches all namespaces and will enforce all the governing policies on them.
All namespaces managed by MTO require the `stakater.com/tenant` label.
MTO ignores privileged namespaces that are mentioned in the IntegrationConfig, and does not manage them. Therefore, any tenant label on such namespaces will be ignored.

```bash
oc create namespace stakater-test
Error from server (Cannot Create namespace stakater-test without label stakater.com/tenant. User: Bill): admission webhook "vnamespace.kb.io" denied the request: Cannot CREATE namespace stakater-test without label stakater.com/tenant. User: Bill
```

Bill is trying to create a namespace without the `stakater.com/tenant` label. Creating a namespace without this label is only allowed if the namespace is privileged. Privileged namespaces will be ignored by MTO and do not require the said label. Therefore, Bill will add the required regex in the IntegrationConfig, along with any other namespaces which are privileged and should be ignored by MTO - like `default`, or namespaces with prefixes like `openshift`, `kube`:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  privileged:
    namespaces:
      - ^default$
      - ^openshift-.*
      - ^kube-.*
      - ^stakater-.*
```

After mentioning the required regex (`^stakater-.*`) under `privilegedNamespaces`, Bill can create the namespace without interference.

```bash
oc create namespace stakater-test
namespace/stakater-test created
```

MTO will also disallow all users which are not tenant owners to perform CRUD operations on namespaces. This will also prevent Service Accounts from performing CRUD operations.

If Bill wants MTO to ignore Service Accounts, then he would simply have to add them in the IntegrationConfig:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  privileged:
    serviceAccounts:
      - system:serviceaccount:openshift
      - system:serviceaccount:stakater
      - system:serviceaccount:kube
      - system:serviceaccount:redhat
      - system:serviceaccount:hive
```

Bill can also use regex patterns to ignore a set of service accounts:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  privileged:
    serviceAccounts:
      - ^system:serviceaccount:openshift-.*
      - ^system:serviceaccount:stakater-.*
```

## Configuring Vault in IntegrationConfig

[Vault](https://www.vaultproject.io/) is used to secure, store and tightly control access to tokens, passwords, certificates, and encryption keys for protecting secrets and other sensitive data using a UI, CLI, or HTTP API.

If Bill (the cluster admin) has Vault configured in his cluster, then he can take benefit from MTO's integration with Vault.

MTO automatically creates Vault secret paths for tenants, where tenant members can securely save their secrets. It also authorizes tenant members to access these secrets via OIDC.

Bill would first have to integrate Vault with MTO by adding the details in IntegrationConfig. For more [details](../how-to-guides/integration-config.md#vault)

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
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@acme.org
  viewers:
    users:
    - john@acme.org
  quota: small
  sandbox: false
```

Now Bill goes to `Vault` and sees that a path for `tenant` has been made under the name `bluesky/kv`, confirming that Tenant members with the Owner or Edit roles now have access to the tenant's Vault path.

Now if Anna sign's in to the Vault via OIDC, she can see her tenants path and secrets. Whereas if John sign's in to the Vault via OIDC, he can't see his tenants path or secrets as he doesn't have the access required to view them.
