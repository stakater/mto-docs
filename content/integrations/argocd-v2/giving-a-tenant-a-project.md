# Giving a tenant a project

This walks through opting a tenant in, seeing its `AppProject`, and deploying an Application. It assumes the extension is installed ([Installation](installation.md)) and a `Tenant` named `acme` exists with two namespaces, `acme-dev` and `acme-prod`.

## 1. Set the repositories the tenant may deploy from

An `AppProject` with no `sourceRepos` permits **no** repository, and ArgoCD then rejects every Application with `application repo ... is not permitted in project`. Creating the project is not the same as letting the tenant deploy.

There is no shareable default — one org-wide value would let every tenant deploy from every other tenant's repos. The safe form is a per-tenant pattern templated on the tenant name, set once as a chart value:

```bash
helm upgrade mto-extension-argocd \
  oci://ghcr.io/stakater/public/charts/mto-extension-argocd \
  --namespace multi-tenant-operator --reuse-values \
  --set 'argocd.sourceRepos.pattern[0]=https://github.com/acme/{{ tenant }}-gitops'
```

Tenant `acme` then gets `https://github.com/acme/acme-gitops`. A tenant can also override its own repositories by annotation — see [Reference](reference.md#per-tenant-overrides).

## 2. Opt the tenant in

```bash
kubectl annotate tenant acme argocd.tenantoperator.stakater.com/enabled=true
kubectl -n multi-tenant-operator wait \
  templateinstances.templates.v2.stakater.com/mto-argocd-tenant-acme \
  --for=jsonpath='{.status.phase}'=Ready --timeout=90s
```

## 3. See the AppProject

```bash
kubectl -n openshift-gitops get appproject acme -o yaml
```

The project is scoped to the tenant's namespaces, with three roles bound to its groups and users:

```yaml
spec:
  description: Managed by mto-extension-argocd
  sourceRepos:
    - https://github.com/acme/acme-gitops
  destinations:                       # the tenant's namespaces, never the ArgoCD namespace
    - { namespace: acme-dev,  server: https://kubernetes.default.svc }
    - { namespace: acme-prod, server: https://kubernetes.default.svc }
  roles:
    - name: acme-owner
      groups:
        - acme-owner-group-c2ef09     # the MTO-generated group (OpenShift)
        - acme-admins                 # the tenant's groups
        - alice@acme.example          # and its users — see Security
      policies:
        - p, proj:acme:acme-owner, applications, *, acme/*, allow
        - p, proj:acme:acme-owner, applicationsets, *, acme/*, allow
        # ... repositories, clusters, logs
    # acme-edit: get, sync, update on applications; get on the rest
    # acme-view: get on everything
```

## 4. Deploy an Application

The tenant's owners and editors can now create Applications in that project. By default Applications live in the ArgoCD namespace; to let tenants keep them in their own namespaces instead, see [Applications in tenant namespaces](applications.md).

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: acme-web
  namespace: openshift-gitops
spec:
  project: acme
  source:
    repoURL: https://github.com/acme/acme-gitops
    path: web
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: acme-dev
```

ArgoCD accepts it because the repo matches `sourceRepos` and the destination is one of the project's `destinations`. A destination outside the tenant's namespaces, or a repo outside its `sourceRepos`, is refused.

## What a tenant cannot do

- Deploy into a namespace it does not own — `destinations` is the tenant's namespaces only.
- Deploy into the ArgoCD control-plane namespace — never a destination (see [Security](security.md)).
- Deploy from a repository outside its `sourceRepos`.
- Manage a cluster-scoped kind unless the platform allow-listed it (see [Reference](reference.md#cluster-scoped-kinds)).

Next: [Applications in tenant namespaces](applications.md), or [Identity and sync impersonation](identity-and-impersonation.md).
