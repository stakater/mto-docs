# MTO ArgoCD Extension

## ArgoCD multi-tenancy

> **ArgoCD multi-tenancy is implemented exclusively through `AppProject`.**

There are **no other tenancy primitives** in ArgoCD.

An `AppProject` defines:

* which namespaces a tenant can deploy to
* which clusters are allowed
* which Git repositories are allowed
* which users/groups can access and sync
* whether cluster-scoped resources are allowed

If a tenant has its **own AppProject**, it is isolated.
If not, it is not.

Everything else (applications, bootstrap, repo creds) is **supporting plumbing**, not tenancy.

## What MTO ArgoCD Extension is responsible for?

MTO’s ArgoCD Extension **only required responsibility** for ArgoCD is:

> **For each Tenant, create and maintain exactly one AppProject.**

That’s it.

Optional responsibilities (UX / automation):

* creating an initial Application (bootstrap)
* validating repo credentials exist
* cleaning up resources on tenant deletion

## Current implementation (what exists today) (this section to be removed later)

### A) IntegrationConfig (deprecated direction)

ArgoCD configuration exists inside a [central IntegrationConfig](https://docs.stakater.com/mto/latest/kubernetes-resources/integration-config.html#argocd), living in the tenant-operator repo.

Problems:

* tight coupling between tenant core and integrations
* hard to test in isolation
* hard to release independently
* unclear ownership boundaries

### B) Extensions CR (per-tenant) – current state

[Extensions CR](https://docs.stakater.com/mto/latest/integrations/argocd.html) per tenant

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Extensions
spec:
  tenantName: tenant-sample
  argoCD:
    onDeletePurgeAppProject: true
    appProject:
      sourceRepos: [...]
      clusterResourceWhitelist: [...]
      namespaceResourceBlacklist: [...]
```

Problems:

* one CR **per tenant per integration**
* CRD explosion
* heavy reconciliation
* allowlist/denylist leaks ArgoCD internals
* difficult upgrade/migration story

## New ArgoCDExtension` CR (v1alpha1) Proposal

```yaml
# ArgoCDExtension
# Purpose:
#   - Enable ArgoCD multi-tenancy for MTO tenants by creating ONE AppProject per tenant.
#   - AppProject is the ONLY ArgoCD multi-tenancy primitive (security boundary).
#   - Optional: create one "bootstrap" Application per tenant to auto-connect Git repo (UX only).
#
# Key design decisions:
#   - No per-tenant CRs (no CR explosion).
#   - Namespace destinations are derived from Namespace labels (clean + stable).
apiVersion: extensions.mto.stakater.com/v1alpha1
kind: ArgoCDExtension
metadata:
  # Convention: one instance per ArgoCD server/instance.
  # Keep this in a platform namespace (e.g., mto-system).
  name: cluster-default
  namespace: mto-system
spec:
  # Global on/off for this extension instance.
  enabled: true

  # Reference to the existing/shared ArgoCD instance this extension manages.
  # The controller will create AppProjects (and optional bootstrap Applications) that ArgoCD consumes.
  server:
    name: argocd
    namespace: openshift-operators
    # Optional: if you run multiple ArgoCD instances in the same namespace.
    # instanceName: argocd

  # Which tenants should be managed by this ArgoCD extension?
  # Recommended: opt-in via Tenant label (simple, GitOps-friendly).
  tenantSelector:
    matchLabels:
    # Tenant CR must carry this label to be managed by ArgoCD extension.
    mto.stakater.com/argocd: "enabled"

  # Lifecycle behavior for resources CREATED by this extension.
  # - Retain: leave AppProjects/Bootstrap apps in cluster when tenant opts out or is deleted.
  # - Delete: clean them up (typical if MTO is the owner-of-truth).
  deletionPolicy: Retain # Retain | Delete

  tenancy:
    # How we decide where tenant apps are allowed to deploy.
    # We DO NOT rely on namespace name prefixes/postfixes, and we DO NOT require Tenant.status.
    # Instead we select namespaces by labels (Kubernetes-native + stable).
    destinations:
      strategy: NamespaceLabelSelector

      # Include all namespaces that belong to the tenant (template resolved per tenant).
      # Requirement: tenant namespaces must be labeled like:
      #   mto.stakater.io/tenant: <tenant-name>
      namespaceSelectorTemplate:
        matchLabels:
          mto.stakater.io/tenant: "{{ .tenant.name }}"

      # Exclude system namespaces (platform-owned) even if they have the tenant label.
      # Requirement: system namespaces must be labeled like:
      #   mto.stakater.io/purpose: system
      excludeSelector:
        matchLabels:
          mto.stakater.io/purpose: "system"

    guardrails:
      # High-signal safety knob:
      # - false: tenants cannot deploy cluster-scoped resources via ArgoCD (recommended default)
      # - true: tenants MAY deploy cluster-scoped resources (use with extreme care)
      allowClusterScopedResources: false

  # How tenant users/groups get permissions in ArgoCD.
  # The extension should map tenant membership to AppProject roles/policies.
  tenantRoleMapping:
    owner: admin
    editor: write
    viewer: read

  # Repo credentials strategy (plumbing, not multi-tenancy):
  # This controls how ArgoCD gets access to private repos for each tenant.
  # Recommended: per-tenant repo creds secret.
  repoCredentials:
    strategy: PerTenantSecret # PerTenantSecret | SharedSecret | None

    perTenantSecret:
      # Where the secret lives:
      # - TenantSystemNamespace: a per-tenant "system" namespace (if you have it)
      # - ArgoCDNamespace: place per-tenant repo secrets in ArgoCD namespace for simpler RBAC
      namespaceStrategy: ArgoCDNamespace # TenantSystemNamespace | ArgoCDNamespace

      # Secret name convention (same for all tenants).
      # The secret content is provided by platform process/ESO/OpenBao/Vault/etc.
      # MTO can validate presence and report status if missing.
      secretName: argocd-repo-creds

  # Bootstrap (optional UX):
  # Creates ONE root Application per tenant so onboarding is "zero-click".
  # This is NOT required for multi-tenancy. Multi-tenancy is AppProject only.
  bootstrap:
    enabled: true

    # Repo URL/path/revision can be overridden per tenant via annotations (small scalar overrides only).
    # Example Tenant annotations:
    #   argocd.ext.mto.stakater.com/bootstrap-repo-url: https://github.com/acme/gitops
    #   argocd.ext.mto.stakater.com/bootstrap-path: tenants/acme
    #   argocd.ext.mto.stakater.com/bootstrap-revision: main
    repoURL:
      defaultTemplate: "https://github.com/{{ .tenant.name }}/gitops"
      overrideFromAnnotation: "argocd.ext.mto.stakater.com/bootstrap-repo-url"

    path:
      defaultTemplate: "tenants/{{ .tenant.name }}"
      overrideFromAnnotation: "argocd.ext.mto.stakater.com/bootstrap-path"

    revision:
      default: "main"
      overrideFromAnnotation: "argocd.ext.mto.stakater.com/bootstrap-revision"

    # Behavior if repoURL/path cannot be resolved (missing annotations + no usable defaults):
    # - SkipBootstrap: do not create bootstrap Application; still create AppProject (tenancy is intact)
    # - DegradedTenant: mark tenant as degraded in extension status
    onMissingRepoOrPath: SkipBootstrap # SkipBootstrap | DegradedTenant
```

## Supported per-tenant overrides (v1alpha1)

Only these annotations are supported:

```yaml
argocd.ext.mto.stakater.com/bootstrap-repo-url
argocd.ext.mto.stakater.com/bootstrap-path
argocd.ext.mto.stakater.com/bootstrap-revision
```

Nothing else.

Security, isolation, and topology are **platform-owned**.
