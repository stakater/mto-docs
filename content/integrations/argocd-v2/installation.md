# Installation

For a platform administrator: install the chart once, then opt tenants in. The whole setup is cluster-wide — there is no per-tenant installation step.

## Requirements

| | |
|:---|:---|
| [Multi-Tenant Operator](../../getting-started/installation/overview.md) | `Tenant` `v1beta3` and `IntegrationConfig` `v1beta1` |
| [Template Operator](https://github.com/stakater/template-operator-v2) | `0.0.8` recommended. `0.0.7+` is needed to keep `AppProject`s on teardown (see [Operating](operating.md#what-deletes-an-appproject)); `strict` drift protection (the default) needs the sync webhook |
| ArgoCD | `argoproj.io/v1alpha1` `AppProject`; 3.x, tested on 3.5.4 |
| Kubernetes | 1.33+ tested. Template Operator's CRDs do not install on 1.31 |

### ArgoCD versions

Upstream ArgoCD supports the last three minors. OpenShift GitOps 1.22 ships ArgoCD 3.5, 1.21 ships 3.4, 1.20 ships 3.3. Some features need a specific line:

| Feature | Needs |
|:---|:---|
| this chart, security defaults included | ArgoCD 3.0+ |
| Applications in the tenant's own namespace | ArgoCD 3.x. 3-segment RBAC (`<project>/<namespace>/<app>`) needs 3.4.4+ |
| a `name` on `clusterResourceWhitelist` entries | ArgoCD 3.3+ |
| sync impersonation (beta); ApplicationSets in any namespace (stable) | ArgoCD 3.5+ / OpenShift GitOps 1.22 |

## Install Template Operator

The extension renders objects for Template Operator, so that must be running. The simplest route is to let MTO deploy it: set `components.templateOperatorV2.mode: Managed` in the `IntegrationConfig`.

```yaml
spec:
  components:
    templateOperatorV2:
      mode: Managed
```

MTO then runs Template Operator in `multi-tenant-operator` as the ServiceAccount `tenant-operator-template-operator-v2` — the values used below. To install it yourself from its Helm chart instead, it runs as `template-operator-v2` in `stakater-template-operator`; set `rbac.serviceAccount` to match.

## Install the extension

`argocd.namespace` is required (where `AppProject`s are created), and `rbac.serviceAccount` must match your Template Operator's identity.

```bash
helm install mto-extension-argocd \
  oci://ghcr.io/stakater/public/charts/mto-extension-argocd \
  --namespace multi-tenant-operator \
  --set argocd.namespace=openshift-gitops \
  --set rbac.serviceAccount.name=tenant-operator-template-operator-v2 \
  --set rbac.serviceAccount.namespace=multi-tenant-operator
```

!!! warning "The ServiceAccount must be your Template Operator's"
    The RBAC the chart installs binds to `rbac.serviceAccount`. If it names an account that is not the one Template Operator runs as, `helm install` still succeeds but nothing reconciles — the parent cannot even list `Tenant`s. The values above are for an MTO-managed Template Operator; a standalone install uses `template-operator-v2` in `stakater-template-operator`.

Nothing is created for a tenant yet — `scaffolding.mode` defaults to `OnAnnotation`, so a tenant is included only once it opts in.

## Opt a tenant in

The value must be exactly `"true"`; `"True"`, `"yes"` and `"1"` all read as opted out, deliberately.

```bash
kubectl annotate tenant acme argocd.tenantoperator.stakater.com/enabled=true
```

`scaffolding.mode` also offers `OnLabel` (a label instead of an annotation), `Always` (every tenant), and `Never` (none). See [Reference](reference.md).

!!! tip "Roll out gradually"
    Keep the default `OnAnnotation` and opt in **one** tenant first. Confirm its `AppProject` looks right, then opt in the rest. Switching to `Always` later brings every tenant in at once; narrowing the mode again *removes* the projects it now excludes (see [Operating → what deletes an AppProject](operating.md#what-deletes-an-appproject)), so change it deliberately.

## Verify

One row per opted-in tenant:

```bash
kubectl get templateinstances.templates.v2.stakater.com \
  -n multi-tenant-operator -l templates.v2.stakater.com/instance \
  -o custom-columns='TENANT:.spec.parameters[?(@.name=="tenant")].value,READY:.status.conditions[?(@.type=="Ready")].status'
```

```text
TENANT   READY
acme     True
```

!!! tip
    Always use the fully-qualified `templateinstances.templates.v2.stakater.com`. On OpenShift, a bare `kubectl get templateinstance` resolves to OpenShift's own `template.openshift.io` kind and returns the wrong object with an empty status — which looks exactly like "nothing is reconciling".

---

**Previous:** [Overview](overview.md) · **Next:** [Giving a tenant a project](giving-a-tenant-a-project.md)
