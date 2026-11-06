# IntegrationConfig

`IntegrationConfig` is the single resource that configures Multi Tenant Operator for a cluster. One `IntegrationConfig`, named `tenant-operator-config`, lives in the `multi-tenant-operator` namespace and its `spec` is split into five sections:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  components: {}      # the console, showback and the services behind them
  accessControl: {}   # tenant roles, and privileged users/namespaces MTO leaves alone
  metadata: {}        # default labels/annotations for managed namespaces and groups
  integrations: {}    # ArgoCD and Vault wiring (deprecated — use Extensions)
  tenantPolicies: {}  # extra tenant isolation
```

Each section is described below.

## Components

`components` configures the MTO console, the showback (cost) feature, and the services that back them.

```yaml
components:
  console: true
  showback: true
  ingress:
    host: mto.apps.example.com
    tlsSecretName: mto-tls
    ingressClassName: nginx
  postgres:
    mode: Managed
  prometheus:
    mode: Managed
  opencost:
    mode: Managed
  dex:
    mode: Managed
  templateOperatorV2:
    mode: Managed
```

| Field | Purpose |
| --- | --- |
| `console` | Enable or disable the MTO console GUI. |
| `showback` | Enable or disable the showback (cost) feature in the console. |
| `ingress` | How the web components are exposed. See [Ingress](#ingress). |
| `postgres`, `prometheus`, `opencost`, `dex`, `dexConfigOperator`, `finopsOperator`, `templateOperatorV2` | The services behind the console and showback. See [Dependencies](#dependencies). |
| `showbackOpts` | **Deprecated** showback pricing options. See [Showback pricing](#showback-pricing-deprecated). |

The console GUI and showback are described in the [console overview](../console/overview.md).

### Ingress

MTO's web components — Console, Gateway, Dex, and the FinOps gateway — are served under a **single shared hostname** by default, each on its own path prefix, rather than one hostname per component.

#### Path layout

| Component | Path under the shared host | Example URL |
| --- | --- | --- |
| Console | `/` | `https://mto.apps.example.com/` |
| Gateway | `/gateway` | `https://mto.apps.example.com/gateway` |
| Dex | `/dex` | `https://mto.apps.example.com/dex` |
| FinOps Gateway | `/finops` | `https://mto.apps.example.com/finops` |

Every component ingress uses `pathType: Prefix` and no rewrite annotations, so the full path reaches the backend and each backend serves under its prefix. The Console holds `/` and relies on the ingress controller matching the longer prefixes first, which both the nginx ingress controller and the OpenShift router do.

#### Consolidated mode (recommended)

Set a top-level `host` to serve all components under one hostname:

```yaml
components:
  ingress:
    host: mto.apps.example.com   # shared host for all components
    tlsSecretName: mto-tls       # TLS cert covering the shared host
    ingressClassName: nginx      # applied to every component ingress
```

- `host`: the shared hostname. Setting it enables consolidated mode.
- `tlsSecretName`: a single TLS secret whose certificate covers the shared host, used by every component ingress.
- `ingressClassName`: ingress class for all component ingresses. On OpenShift, if omitted, MTO discovers the default IngressClass (falling back to `openshift-default`).

On OpenShift, when no host is set, the shared host is auto-derived from the cluster ingress domain as `tenant-operator-<operator-namespace>.<cluster-ingress-domain>`. On Kubernetes there is no cluster domain to derive from, so `host` must be set explicitly.

Create the TLS secret in the operator namespace:

```bash
kubectl -n multi-tenant-operator create secret tls <tls-secret-name> --key=<path-to-key.pem> --cert=<path-to-cert.pem>
```

!!! note
    In consolidated mode the Dex issuer becomes `https://<host>/dex`. Any external OIDC client that trusts MTO's Dex must be configured with this issuer.

#### Legacy mode (per-component hosts)

!!! danger "Deprecated"
    Per-component hosts are the pre-consolidation behavior; this mode is **deprecated** and will be removed in a future release. Use [consolidated mode](#consolidated-mode-recommended) instead.

Set explicit per-component hosts, with no top-level `host`, to keep each component on its own hostname:

```yaml
components:
  ingress:
    ingressClassName: nginx
    console:
      host: tenant-operator-console.apps.example.com
      tlsSecretName: console-tls
    gateway:
      host: tenant-operator-gateway.apps.example.com
      tlsSecretName: gateway-tls
    dex:
      host: tenant-operator-dex.apps.example.com
      tlsSecretName: dex-tls
    finopsGateway:
      host: tenant-operator-finops.apps.example.com
      tlsSecretName: finops-tls
```

A component without an explicit `host` still falls back to its auto-derived OpenShift hostname, `tenant-operator-<component>-<operator-namespace>.<cluster-ingress-domain>`.

#### Upgrading from per-component hosts

OpenShift installations that set no ingress hosts previously got one auto-derived hostname per component. They now move to a single shared host, which changes every component URL and the Dex issuer, so existing sessions have to re-authenticate and external OIDC clients need the new issuer. To stay on the old hostnames, set the per-component `host` fields as shown in legacy mode. Kubernetes installations already required hosts to be configured and are unaffected as long as a host is set.

### Dependencies

PostgreSQL, Prometheus, OpenCost, Dex, DexConfigOperator, FinOps Operator and Template Operator v2 are provisioned by the [MTO Dependencies Operator](https://github.com/stakater/mto-dependencies-operator). The services that support both `Managed` and `External` share the same shape:

- `mode`: `Managed` (MTO deploys and manages it — the default) or `External` (you supply it).
- `values`: Helm chart value overrides, applied when `mode: Managed`.
- `external`: connection details, used when `mode: External`.

#### PostgreSQL

`values` accepts [Bitnami PostgreSQL Helm chart values](https://github.com/bitnami/charts/blob/main/bitnami/postgresql/values.yaml).

```yaml
components:
  postgres:
    mode: Managed
    values:
      primary:
        persistence:
          size: "20Gi"
```

To use an external PostgreSQL instance, set `mode: External` and reference a connection secret:

```yaml
components:
  postgres:
    mode: External
    external:
      secretRef:
        name: external-postgres-connection
        namespace: shared-services
```

The referenced secret must contain either a `dsn` field with a full connection string (`postgresql://user:pass@host:5432/dbname?sslmode=require`) or the individual fields `host`, `port`, `username`, `password`, `database` and `sslmode`.

#### Prometheus

`values` accepts [Prometheus Helm chart values](https://github.com/prometheus-community/helm-charts/blob/main/charts/prometheus/values.yaml).

```yaml
components:
  prometheus:
    mode: Managed
    values:
      server:
        retention: "30d"
        persistence:
          size: "50Gi"
```

To use an external Prometheus instance, set `mode: External` and point MTO at it with `external.serverURL`:

```yaml
components:
  prometheus:
    mode: External
    external:
      serverURL: https://prometheus.example.com
```

#### OpenCost

`values` accepts [OpenCost Helm chart values](https://github.com/opencost/opencost-helm-chart/blob/main/charts/opencost/values.yaml).

```yaml
components:
  opencost:
    mode: Managed
    values:
      opencost:
        exporter:
          replicas: 2
```

To use an external OpenCost instance, set `mode: External` and point MTO at it with `external.serverURL`:

```yaml
components:
  opencost:
    mode: External
    external:
      serverURL: https://opencost.example.com
```

#### Dex

`values` accepts [Dex Helm chart values](https://github.com/dexidp/helm-charts/blob/master/charts/dex/values.yaml).

```yaml
components:
  dex:
    mode: Managed
    values: {}
```

To use an external Dex instance, set `mode: External` and give its issuer URL (used for OIDC discovery):

```yaml
components:
  dex:
    mode: External
    external:
      issuer: https://dex.example.com
```

#### DexConfigOperator

DexConfigOperator helps configure Dex on Kubernetes. It takes only `values`, Helm chart values for customizing its deployment:

```yaml
components:
  dexConfigOperator:
    values: {}
```

#### FinOps Operator

The FinOps Operator powers the showback feature. It takes only `values`, Helm chart values for customizing its deployment:

```yaml
components:
  finopsOperator:
    values: {}
```

#### Template Operator v2

Set `mode: Managed` to deploy Template Operator v2 alongside MTO. It is not deployed by default (`mode: Disabled`). Chart values can be overridden via `values`:

```yaml
components:
  templateOperatorV2:
    mode: Managed
    values: {}
```

### Showback pricing (deprecated)

!!! danger "Deprecated"
    `showbackOpts` is **deprecated** and will be removed in a future release. Its settings now belong in the Helm `values` of the FinOps Operator, OpenCost and Prometheus components.

Each legacy field moves as follows:

| Legacy field | Replacement |
| --- | --- |
| `showbackOpts.custom` | `components.finopsOperator.values.priceBook.rates` |
| `showbackOpts.cloudPricingSecretRef` | `components.opencost.values.opencost.cloudIntegrationSecret`, except for Azure customer-specific pricing |
| `showbackOpts.retentionPeriod` | `components.prometheus.values.server.retention` |

#### Migrating custom pricing

Custom rates are now set in the FinOps Operator price book. The rate names differ from the legacy keys:

```yaml
components:
  finopsOperator:
    values:
      priceBook:
        rates:
          cpuHour: "0.031611"         # was CPU
          spotCpuHour: "0.006655"     # was spotCPU
          ramGbHour: "0.004237"       # was RAM
          spotRamGbHour: "0.000892"   # was spotRAM
          gpuHour: "0.95"             # was GPU
          pvGbHour: "0.00005479452"   # was storage
          networkGiB: "0.01"          # was zoneNetworkEgress
```

The price book has a single network rate, so `regionNetworkEgress` and `internetNetworkEgress` have no equivalent. MTO already leaves both out when it builds the price book from `showbackOpts.custom`.

#### Migrating cloud pricing

For AWS pricing and Azure standard pricing, create the cloud integration secret in the operator namespace and reference it by name:

```yaml
components:
  opencost:
    values:
      opencost:
        cloudIntegrationSecret: cloud-integration
```

Unlike `cloudPricingSecretRef`, this field does not copy the secret from another namespace, so it must already exist in `multi-tenant-operator`.

!!! note
    Azure customer-specific pricing has no replacement yet. MTO reads the billing account and offer ID only from the secret referenced by `cloudPricingSecretRef`, so keep using that field for customer-specific pricing until a replacement is available.

#### Migrating retention

Set the Prometheus retention in the [Prometheus](#prometheus) chart values:

```yaml
components:
  prometheus:
    values:
      server:
        retention: "30d"
```

The sections below document the legacy `showbackOpts` fields for existing installations.

#### Custom Pricing

Override the default pricing model under `components.showbackOpts.custom`:

```yaml
components:
  console: true
  showback: true
  showbackOpts:
    custom:
      CPU: "0.031611"
      spotCPU: "0.006655"
      RAM: "0.004237"
      spotRAM: "0.000892"
      GPU: "0.95"
      storage: "0.00005479452"
      zoneNetworkEgress: "0.01"
      regionNetworkEgress: "0.01"
      internetNetworkEgress: "0.12"
```

After the `IntegrationConfig` is updated, MTO updates a ConfigMap named `opencost-custom-pricing` and the new pricing appears in the console.

#### Azure Pricing

MTO supports the Azure pricing model via `components.showbackOpts.cloudPricingSecretRef`, for both Azure Standard Pricing and customer-specific pricing.

#### AWS Pricing

MTO supports the AWS pricing model via `components.showbackOpts.cloudPricingSecretRef`, for both AWS Standard Pricing and AWS Spot Instance Pricing.

## Access Control

`accessControl` has three parts: [`rbac`](#rbac) sets the roles bound in each tenant namespace, [`namespaceAccessPolicy`](#namespace-access-policy) restricts who may act on managed namespaces, and [`privileged`](#privileged) lists the namespaces, service accounts, users and groups MTO leaves alone.

### RBAC

`rbac.tenantRoles` defines which roles are bound in each tenant namespace. It has a required `default` set and an optional `custom` set selected by namespace labels.

!!! warning
    If you configure no roles, tenant members receive the default cluster roles: `admin` for owners, `edit` for editors and `view` for viewers. See [Changing the default access level](../guides/custom-roles.md).

```yaml
accessControl:
  rbac:
    tenantRoles:
      default:
        owner:
          clusterRoles:
            - admin
        editor:
          clusterRoles:
            - edit
        viewer:
          clusterRoles:
            - view
      custom:
        - labelSelector:
            matchLabels:
              stakater.com/kind: dev
          owner:
            clusterRoles:
              - custom-owner
```

#### TenantRoles

`tenantRoles` holds a required `default` role set and an optional `custom` set selected by namespace labels.

##### Default

`default` holds the roles bound in every tenant namespace that is not matched by a `custom` entry. All three subfields — `owner`, `editor` and `viewer` — are required and must each name at least one role. They correspond to the member fields of the [Tenant CR](tenant.md).

##### Custom

`custom` is an optional array of roles applied only to namespaces matched by a `labelSelector`. A namespace matched by two selectors gets both sets of roles. Any of `owner`, `editor` or `viewer` omitted from a `custom` entry is inherited from `default`. For example, a `custom` entry that sets only `owner` takes its `editor` and `viewer` from `default`.

### Namespace Access Policy

`namespaceAccessPolicy.deny.privilegedNamespaces` restricts which privileged users and groups may perform CRUD operations on managed namespaces.

```yaml
accessControl:
  namespaceAccessPolicy:
    deny:
      privilegedNamespaces:
        users:
          - system:serviceaccount:openshift-argocd:argocd-application-controller
          - adam@stakater.com
        groups:
          - cluster-admins
```

### Privileged

`privileged` lists the namespaces, service accounts, users and groups that MTO ignores — it neither manages nor interferes with them, including deletion. Namespace and service-account entries are regex patterns.

```yaml
accessControl:
  privileged:
    namespaces:
      - ^default$
      - ^openshift.*
      - ^kube.*
    serviceAccounts:
      - ^system:serviceaccount:openshift.*
      - ^system:serviceaccount:kube.*
    users:
      - ''
    groups:
      - cluster-admins
```

#### Namespaces

`privileged.namespaces` lists namespaces MTO does not manage; privileged namespaces skip the integrations and finalizer processing applied to normal namespaces. Values are regex patterns, for example:

- `^default$` — the `default` namespace.
- `^openshift-.*` — every namespace with the `openshift-` prefix.
- `stakater` — every namespace whose name contains `stakater`. A pattern without `^` or `$` matches anywhere in the name.

#### Service Accounts

`privileged.serviceAccounts` lists service accounts MTO does not manage. Values are regex patterns — for example `^system:serviceaccount:openshift-.*` for all service accounts under the `openshift-` prefix, or `^system:serviceaccount:builder$` for one specific account.

!!! note
    `stakater` and `stakater.*` match the same namespaces. `stakater.` additionally requires at least one character after `stakater`, so it does not match a namespace named exactly `stakater`. To test a pattern, use [Regex101](https://regex101.com/) with the Golang flavor.

#### Users

`privileged.users` lists users MTO does not manage. Each entry must match the username exactly; regex patterns are not supported.

#### Groups

`privileged.groups` names groups allowed to perform CRUD operations on any namespace on the cluster without MTO getting in their way, including deletion of privileged namespaces.

!!! note
    `kube:admin` is bypassed by default and can operate as cluster admin on all namespaces.

!!! warning
    Test any non-trivial regex for `privileged.namespaces` or `privileged.serviceAccounts` before applying it — locally or with a tool such as [Regex101](https://regex101.com/).

## Metadata

`metadata` sets default `labels` and `annotations` that MTO applies to the namespaces, groups and sandbox namespaces it manages.

```yaml
metadata:
  groups:
    labels:
      role: customer-reader
    annotations: {}
  namespaces:
    labels:
      stakater.com/workload-monitoring: "true"
    annotations:
      openshift.io/node-selector: node-role.kubernetes.io/worker=
  sandboxes:
    labels:
      stakater.com/kind: sandbox
    annotations: {}
```

- `metadata.namespaces` applies to tenant namespaces, `metadata.groups` to managed groups, and `metadata.sandboxes` to sandbox namespaces.

Every project created afterwards carries these labels and annotations:

```yaml
kind: Project
apiVersion: project.openshift.io/v1
metadata:
  name: bluesky-build
  annotations:
    openshift.io/node-selector: node-role.kubernetes.io/worker=
  labels:
    stakater.com/workload-monitoring: 'true'
    stakater.com/tenant: bluesky
```

```yaml
kind: Group
apiVersion: user.openshift.io/v1
metadata:
  name: bluesky-owner-group
  labels:
    role: customer-reader
users:
  - andrew@stakater.com
```

## Integrations

!!! danger "Deprecated"
    Configuring integrations through the `IntegrationConfig` is the legacy mechanism; it is **deprecated** and will be removed in a future release. Configure these tools through [Extensions](../extensions/overview.md) instead.

`integrations` wires MTO into other tools. MTO supports ArgoCD and Vault.

### ArgoCD

!!! danger "Deprecated"
    Configuring ArgoCD through the `IntegrationConfig` is the legacy integration; it is **deprecated** and will be removed in a future release. Use the [ArgoCD v2 extension](../extensions/argocd-v2/overview.md) instead.

[ArgoCD](https://argoproj.github.io/argo-cd/) is a GitOps continuous-delivery tool for Kubernetes. When ArgoCD is installed on the cluster, MTO can create an AppProject per tenant so each tenant syncs only to its own namespaces.

```yaml
integrations:
  argocd:
    clusterResourceWhitelist:
      - group: tronador.stakater.com
        kind: EnvironmentProvisioner
    namespaceResourceBlacklist:
      - group: '' # all groups
        kind: ResourceQuota
    namespace: openshift-operators
```

- `clusterResourceWhitelist`: cluster-scoped resources ArgoCD may sync from your GitOps repo.
- `namespaceResourceBlacklist`: resources ArgoCD may **not** sync from your GitOps repo.
- `namespace`: where ArgoCD Applications and AppProjects are deployed. Set it when you want an AppProject created per tenant.

### Vault

!!! danger "Deprecated"
    Configuring Vault through the `IntegrationConfig` is the legacy Vault Community integration; it is **deprecated** and will be removed in a future release. Use the [Vault Enterprise extension](../extensions/vault-enterprise/overview.md) instead.

[Vault](https://www.vaultproject.io/) secures and controls access to tokens, passwords, certificates and encryption keys. When Vault is installed on the cluster, MTO can configure per-tenant access.

```yaml
integrations:
  vault:
    enabled: true
    authMethod: kubernetes      # kubernetes (default) or token
    accessInfo:
      accessorPath: oidc/
      address: https://vault.apps.prod.abcdefghi.kubeapp.cloud/
      roleName: mto
      secretRef:
        name: ''
        namespace: ''
    config:
      ssoClient: vault
    policies:
      - name: CustomPolicy
        rules:
          - capabilities:
              - read
              - list
            path: testPath
        tenantRoles:
          - viewer
          - editor
```

MTO supports two authentication methods, selected by `authMethod`:

- `kubernetes` (default): authenticate using Vault's Kubernetes auth method.
- `token`: authenticate using a Vault token.

#### AuthMethod - Kubernetes

With `authMethod: kubernetes`, specify:

- `accessorPath`: accessor path within Vault used to fetch the SSO accessor ID.
- `address`: a Vault address reachable from within the cluster.
- `roleName`: Vault's Kubernetes authentication role.
- `config.ssoClient`: the SSO client name.

See the [Vault Kubernetes auth docs](https://developer.hashicorp.com/vault/docs/auth/kubernetes) for enabling Kubernetes auth in Vault.

#### AuthMethod - Token

With `authMethod: token`, specify:

- `accessorPath`: accessor path within Vault used to fetch the SSO accessor ID.
- `address`: a Vault address reachable from within the cluster.
- `secretRef`: the secret holding the Vault token, by `name` and `namespace`.

#### Vault Policies

The Vault role used for Kubernetes authentication needs these permissions:

```hcl
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

##### Custom Policies

Custom policies are created in Vault and assigned to the tenant roles named in `tenantRoles`.

- `name`: the policy name created in Vault.
- `rules`: policy rules in Vault's policy language.
    - `capabilities`: any of `create`, `read`, `update`, `patch`, `delete`, `list`.
    - `path`: the path the capabilities apply to.
- `tenantRoles`: the roles the policy is assigned to — `viewer`, `editor` or `owner`.

```yaml
policies:
  - name: CustomEditor
    rules:
      - capabilities:
          - read
          - list
          - patch
          - update
        path: testPath
    tenantRoles:
      - editor
  - name: CustomViewer
    rules:
      - capabilities:
          - read
          - list
        path: testPath
    tenantRoles:
      - viewer
```

## TenantPolicies

`tenantPolicies` adds further tenant isolation.

### Network

`tenantPolicies.network` controls how tenants are allowed to communicate:

```yaml
tenantPolicies:
  network:
    disableIntraTenantNetworking: true
    disableNodePortServices: true
    disableHostPorts: true
```

- `disableIntraTenantNetworking` (default `false`): deploy NetworkPolicies that stop tenants communicating with other tenants.
- `disableNodePortServices` (default `false`): disallow `NodePort` services across all namespaces.
- `disableHostPorts` (default `false`): disallow containers that define a `hostPort`.

!!! warning
    `disableIntraTenantNetworking` blocks network traffic **only** — it does not stop DNS service discovery, so tenants can still resolve services in other namespaces even though traffic is blocked. For stricter filtering, turn this off and deploy stricter NetworkPolicies through [Templates](https://docs.stakater.com/template-operator/main/kubernetes-resources/template.html) or manually. For help with an enterprise environment, [contact us](https://www.stakater.com/contact/).

## Related guides

- [Changing the default access level for tenant owners](../guides/custom-roles.md)
- [Extending the default access level for tenant members](../guides/extend-default-roles.md)
- [Disable intra-tenant networking](../guides/disable-intra-tenant-networking.md)
- [Templated values in Labels and Annotations](../guides/templated-metadata-values.md)
