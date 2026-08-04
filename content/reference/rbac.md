# RBAC

RBAC in Multi Tenant Operator comes in three layers:

1. What the **operator itself** may do, granted by the `manager-role` ClusterRole.
1. What **tenant members** may do inside their namespaces, granted by roles MTO creates for each tenant from the [IntegrationConfig](../concepts/integration-config.md).
1. What **cluster administrators** may do to MTO's own custom resources, granted by the editor and viewer roles shipped with the chart.

The second layer is the one most readers want. It is what makes a tenant owner an admin of their own namespaces and nothing else.

## Tenant roles

MTO does not invent permissions for tenant members. It binds existing ClusterRoles into each tenant namespace, and `integrationConfig.spec.accessControl.rbac.tenantRoles` decides which. The defaults map onto the standard Kubernetes user-facing roles:

| Tenant role | Default ClusterRole bound | Effect in the tenant's namespaces |
| --- | --- | --- |
| `owner` | `admin` | Full control of namespaced resources, including RBAC within the namespace |
| `editor` | `edit` | Read and write workloads and config, no RBAC changes |
| `viewer` | `view` | Read-only |

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
```

Replacing these is how you change what a tenant owner can do cluster-wide by policy rather than per namespace. `custom` accepts a namespace label selector and overrides the defaults for matching namespaces, which suits giving production namespaces a tighter editor role than development ones. See [Changing the default access level for tenant owners](../guides/custom-roles.md) and [Extending the default access level for tenant members](../guides/extend-default-roles.md).

Tenant owners additionally receive the cluster-scoped `owner` ClusterRole, which grants `create`, `update`, and `patch` on namespaces so they can create namespaces within their tenant. Creation is still gated by the namespace admission webhook, which is what keeps an owner from creating namespaces outside their tenant.

## Operator permissions

The `manager-role` ClusterRole is what the controllers run with. It is broad, because MTO provisions namespaces, quotas, RBAC, and workloads on the user's behalf.

| API group | Resources | Verbs |
| --- | --- | --- |
| `""` (core) | `configmaps`, `limitranges`, `namespaces`, `persistentvolumeclaims`, `resourcequotas`, `secrets` | create, delete, get, list, patch, update, watch |
| `""` (core) | `pods` | delete, deletecollection, get, list, watch |
| `""` (core) | `services` | create, delete, list, patch, update, watch |
| `""` (core) | `serviceaccounts` | get, list, watch |
| `apps` | `deployments`, `statefulsets` | create, delete, get, list, patch, update, watch |
| `batch` | `cronjobs` | create, delete, get, list, patch, update, watch |
| `rbac.authorization.k8s.io` | `clusterroles`, `clusterrolebindings`, `rolebindings` | create, delete, get, list, patch, update, watch |
| `admissionregistration.k8s.io` | `validatingwebhookconfigurations` | create, delete, get, list, patch, update, watch |
| `networking.k8s.io` | `ingresses` | create, delete, get, list, patch, update, watch |
| `networking.k8s.io` | `ingressclasses` | get, list, watch |
| `scheduling.k8s.io` | `priorityclasses` | get, list, watch |
| `storage.k8s.io` | `storageclasses` | get, list, watch |
| `apiextensions.k8s.io` | `customresourcedefinitions` | get, list, watch |
| `tenantoperator.stakater.com` | `tenants`, `quotas`, `integrationconfigs`, `extensions` | create, delete, get, list, patch, update, watch |
| `templates.stakater.com` | `templates`, `clustertemplateinstances` | create, delete, get, list, patch, update, watch |
| `argoproj.io` | `appprojects` | create, delete, get, list, patch, update, watch |
| `auth.stakater.com` | `clients`, `dexconfigs`, `localusers` | create, delete, get, list, patch, update, watch |
| `dependencies.tenantoperator.stakater.com` | `postgres`, `prometheuses`, `opencosts`, `dexes`, `dexconfigoperators`, `finopsoperators` | create, delete, get, list, patch, update, watch |
| `operators.coreos.com` | `clusterserviceversions` | delete, get, list, watch |

On OpenShift the role also covers `quota.openshift.io/clusterresourcequotas` with write access, and `user.openshift.io` groups and users, plus read access to `config.openshift.io/clusterversions` and `operator.openshift.io/ingresscontrollers`.

Two things are worth noting. Write access to `validatingwebhookconfigurations` is what lets the tenant controller register the [dynamic webhooks](webhooks.md) as tenants enable features, and write access to `clusterroles` and `rolebindings` is what lets it bind tenant roles into namespaces. Neither is optional given what MTO does, and both are why the operator's ServiceAccount should be treated as cluster-admin-equivalent in your threat model.

## Roles for managing MTO resources

For each custom resource the chart provides editor and viewer ClusterRoles intended for binding to your platform team:

| ClusterRole | Grants |
| --- | --- |
| `tenant-editor-role` | Full write on `tenants`, read on `tenants/status` |
| `tenant-viewer-role` | get, list, watch on `tenants` |
| `quota-editor-role` | Full write on `quotas`, read on `quotas/status` |
| `quota-viewer-role` | get, list, watch on `quotas` |
| `integrationconfig-editor-role` | Full write on `integrationconfigs`, read on status |
| `integrationconfig-viewer-role` | get, list, watch on `integrationconfigs` |
| `extensions-editor-role` | Full write on `extensions`, read on status |
| `extensions-viewer-role` | get, list, watch on `extensions` |

Bind one to a user or group:

```sh
kubectl create clusterrolebinding alice-tenant-viewer \
  --clusterrole=tenant-viewer-role \
  --user=alice
```

!!! note
    Granting `tenant-editor-role` is close to granting namespace creation across the cluster, since editing a `Tenant` changes which namespaces exist and who has access to them. Treat it as a platform-team permission.

## Component service accounts

The Console and its supporting workloads run under their own ServiceAccounts rather than the operator's:

| ServiceAccount | ClusterRole | Purpose |
| --- | --- | --- |
| `gateway` | `gateway` | Backend API for the Console. Read and write on tenants, quotas, and template resources; read on integrationconfigs |
| `console` | via gateway | Console frontend |
| `showback` | `showback` | Read-only on tenants, namespaces, pods, and workload kinds for cost attribution |
| `opencost-gateway` | `opencost-gateway` | Read-only across workload, node, and quota resources for cost data |
| `sa-prometheus` | `role-prometheus` | Read-only scrape access, plus the non-resource `/metrics` URL |
| `tenant-api-proxy` | `tenant-api-proxy` | `create` on `services/proxy`, used by the [kubectl plugin](../cli/overview.md) to reach the Tenants API |

## Supporting roles

- **Leader election** grants `coordination.k8s.io` leases, configmaps, and events in the operator namespace, used when `--leader-elect` is set.
- **`metrics-auth-role`** grants `tokenreviews` and `subjectaccessreviews`, which is how the metrics endpoint authenticates and authorizes scrapers.
- **`metrics-reader`** grants `get` on the non-resource `/metrics` URL and is the role you bind to Prometheus. See [Metrics](metrics.md).

## Related pages

- [Security Model](security-model.md) for how these permissions fit the overall isolation story
- [Webhooks](webhooks.md) for the admission checks that constrain what tenant members can do with the permissions above
