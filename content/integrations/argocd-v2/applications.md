# Applications in tenant namespaces

By default a tenant's Applications live in the ArgoCD control-plane namespace. Write access there is effectively ArgoCD admin, so it is usually better to let tenants keep their Applications — and ApplicationSets — in their own namespaces. Both are off by default.

## Applications

Turn on source namespaces:

```yaml
argocd:
  sourceNamespaces:
    enabled: true
    pattern: "{{ tenant }}-argocd"   # the default
```

Every `AppProject` then carries `sourceNamespaces: [<tenant>-argocd]`, but only once that namespace exists and carries the tenant's `stakater.com/tenant` label — exactly like a destination. Anyone who can write an Application in a source namespace can use the project, so it is never a namespace belonging to someone else.

The pattern must contain `{{ tenant }}` and expand to a plain namespace name. ArgoCD reads a glob there, so `{{ tenant }}*` for `acme` would also match `acme-corp-argocd`; that, and a pattern expanding to the ArgoCD namespace or a privileged namespace, is refused (the whole-chart ones at install time, the per-tenant one failing only that tenant's child).

This needs two gates; the chart sets only the second:

1. **ArgoCD must watch the namespaces.** Upstream: `application.namespaces: "*-argocd"` in `argocd-cmd-params-cm`, then restart `argocd-server` and the application controller (`argocd-server` also needs the cluster RBAC in the ArgoCD docs). OpenShift GitOps 1.13+: `ArgoCD.spec.sourceNamespaces` on the cluster-scoped instance.
1. **The AppProject must allow them** — `sourceNamespaces`, rendered by this chart.

The `<tenant>-argocd` namespace itself comes from MTO, e.g. `namespaces.withTenantPrefix: [argocd]` on the `Tenant`. Keep it separate from workload namespaces: on OpenShift GitOps a namespace cannot be both `managed-by` an instance and a source namespace without custom roles.

Kubernetes RBAC on that namespace decides who may create Applications there — a tenant member with `edit` can `kubectl apply` one. The project roles (edit cannot create or delete) govern only the ArgoCD UI and API.

!!! note
    Applications-in-any-namespace is [stable in ArgoCD](https://argo-cd.readthedocs.io/en/stable/operator-manual/app-any-namespace/). 3-segment RBAC policies (`<project>/<namespace>/<app>`) need ArgoCD 3.4.4+.

## ApplicationSets

The roles already grant `applicationsets`, and with source namespaces on, tenants can create ApplicationSets in their own namespace too. ApplicationSets-in-any-namespace is stable in ArgoCD 3.5 / OpenShift GitOps 1.22; generated Applications land in the ApplicationSet's namespace.

They carry risks only platform settings can close ([ArgoCD docs](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Appset-Any-Namespace/)):

| Setting (`argocd-cmd-params-cm`) | Why |
|:---|:---|
| `applicationsetcontroller.namespaces: "*-argocd"` | the controller reads ApplicationSets only there; keep it equal to the source namespaces |
| `applicationsetcontroller.allowed.scm.providers` | SCM-provider and pull-request generators can reach arbitrary hosts with the tenant's tokens; allow only yours |
| `applicationsetcontroller.enable.scm.providers: "false"` | if tenants don't need those generators at all |
| `applicationsetcontroller.enable.tokenref.strict.mode: "true"` | a generator may only use token Secrets labelled for ApplicationSets |

On OpenShift GitOps 1.22 the same lives on the `ArgoCD` resource: `spec.applicationSet.sourceNamespaces` and `spec.applicationSet.scmProviders`. Two more: a `clusters: {}` generator discovers every cluster ArgoCD knows, and an ApplicationSet whose template sets `project` from a parameter cannot use project-scoped repositories.
