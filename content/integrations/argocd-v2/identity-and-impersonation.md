# Identity and sync impersonation

Two independent settings: how the project's roles name their groups, and whose identity a sync runs as.

## Groups named by pattern

By default (`identity.mode: accessControl`) each role's groups are the `Tenant`'s owners, editors and viewers, plus the MTO-generated group and any privileged groups. The other Stakater extensions instead take access from identity-provider groups named by a pattern, and so can this one:

```yaml
identity:
  mode: groupPattern                              # or 'both' while moving over
  groupPattern: "tenant-{{ tenant }}-{{ tier }}"  # the default
```

Tenant `acme` then gets `tenant-acme-owners`, `tenant-acme-editors` and `tenant-acme-viewers`. The MTO-generated and privileged groups are kept in every mode; `both` appends the pattern groups to the `Tenant`'s own lists.

This matters most on OpenShift with external OIDC (4.20+), where the MTO-generated OpenShift group never reaches ArgoCD, and wherever user entries would otherwise need `scopes: [groups, email]` (see [Security](security.md#match-users-the-way-your-login-provides-them)). The pattern must contain both `{{ tenant }}` and `{{ tier }}`. Use a prefix your identity provider controls, and never a name a local ArgoCD user has — an SSO group named like a local user inherits that user's roles.

## Sync impersonation

Off by default. Without it, every sync runs as ArgoCD's application controller, which upstream ships with a `*/*/*` ClusterRole — so a sync can do anything, anywhere. With it, ArgoCD syncs as a ServiceAccount in the destination namespace, and a sync can only do what the tenant could do itself:

```yaml
argocd:
  impersonation:
    enabled: true
    serviceAccount: argocd-deployer   # the default
```

Every `AppProject` then carries one `destinationServiceAccounts` entry per tenant namespace, with `defaultServiceAccount: argocd-deployer`. There is deliberately no catch-all entry, unlike the upstream example: a destination without an entry fails the sync rather than falling back to the controller. The ArgoCD namespace never gets an entry.

Three things are needed outside this chart:

1. **ArgoCD 3.5+**, where [impersonation](https://argo-cd.readthedocs.io/en/stable/operator-manual/app-sync-using-impersonation/) is beta. Enable it with `application.sync.impersonation.enabled: "true"` in `argocd-cm` (on OpenShift GitOps, via `ArgoCD.spec.extraConfig`).
1. **The ServiceAccount in every tenant namespace**, bound to that namespace's `edit` ClusterRole. An MTO `Template` + `TemplateGroupInstance` selecting the `stakater.com/tenant` label does it once for every tenant:

    ```yaml
    apiVersion: tenantoperator.stakater.com/v1alpha1
    kind: Template
    metadata:
      name: argocd-deployer
    resources:
      manifests:
        - apiVersion: v1
          kind: ServiceAccount
          metadata: { name: argocd-deployer }
        - apiVersion: rbac.authorization.k8s.io/v1
          kind: RoleBinding
          metadata: { name: argocd-deployer-edit }
          roleRef: { apiGroup: rbac.authorization.k8s.io, kind: ClusterRole, name: edit }
          subjects:
            - { kind: ServiceAccount, name: argocd-deployer }
    ```

1. **A reduced controller ClusterRole**, for real damage limitation. Otherwise impersonation enforces tenant boundaries at sync time while the controller still holds cluster-admin.

ArgoCD picks the account by the Application's destination namespace, and the template above grants it `edit` in that namespace only. So two kinds of Application stop syncing: one carrying a cluster-scoped kind from `clusterResourceWhitelist` (such as a `Namespace`), and one whose manifests write into another namespace. Grant those rights to `argocd-deployer` deliberately, or keep such Applications out of tenant projects.
